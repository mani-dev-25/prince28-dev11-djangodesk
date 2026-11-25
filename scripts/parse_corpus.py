"""Parse downloaded corpus files into PostgreSQL pages (Day 7)."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from sqlalchemy import select

from djangodesk.config import get_settings
from djangodesk.db.models import Document
from djangodesk.db.session import make_engine, make_sessionmaker
from djangodesk.ingest.parse import parse_html, parse_pdf, parse_text
from djangodesk.ingest.store import record_parse_failure, save_document_pages

ROOT = Path.cwd()
MANIFEST = ROOT / "data" / "manifest.jsonl"


def read_manifest() -> list[dict]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST}")
    items = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") == "downloaded" and row.get("path"):
            items.append(row)
    # Keep the latest record per URL.
    latest = {}
    for row in items:
        latest[row.get("url", row["path"])] = row
    return list(latest.values())


def parse_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix in {".html", ".htm"}:
        return parse_html(path)
    if suffix in {".txt", ".md", ".rst", ".py", ".json", ".yaml", ".yml", ".toml", ".csv"}:
        return parse_text(path.read_text(encoding="utf-8", errors="replace"))
    raise ValueError(f"Unsupported file type: {suffix or '(no extension)'}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Parse downloaded corpus into PostgreSQL")
    parser.add_argument(
        "--limit", type=int, default=0, help="Process only the first N manifest files (0 = all)"
    )
    args = parser.parse_args()
    settings = get_settings()
    engine = make_engine(settings)
    session_factory = make_sessionmaker(engine)
    manifest = read_manifest()
    if args.limit > 0:
        manifest = manifest[: args.limit]

    parsed_count = failed_count = skipped_count = page_count = 0
    try:
        async with session_factory() as session:
            for item in manifest:
                relative = Path(item["path"])
                path = ROOT / relative
                if not path.exists():
                    failed_count += 1
                    print(f"MISSING: {path}")
                    continue
                file_hash = item.get("sha256") or hashlib.sha256(path.read_bytes()).hexdigest()
                url = item.get("url", "")
                title = item.get("title") or item.get("source") or path.name
                # Stable ID from source URL (not from a temporary local filename).
                external_id = "corpus:" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
                try:
                    async with session.begin():
                        doc = await session.scalar(
                            select(Document).where(Document.external_id == external_id)
                        )
                        if doc is None:
                            doc = Document(
                                external_id=external_id,
                                title=title,
                                source_url=url or None,
                                licence=item.get("licence"),
                                doc_type=path.suffix.lower().lstrip(".") or "unknown",
                                published_on=None,
                                sha256=file_hash,
                                metadata_={
                                    "manifest_path": item["path"],
                                    "source": item.get("source"),
                                    "content_type": item.get("content_type"),
                                },
                            )
                            session.add(doc)
                            await session.flush()
                        else:
                            doc.title = title
                            doc.source_url = url or None
                            doc.licence = item.get("licence")
                            doc.doc_type = path.suffix.lower().lstrip(".") or "unknown"
                            doc.sha256 = file_hash
                            doc.metadata_ = {
                                "manifest_path": item["path"],
                                "source": item.get("source"),
                                "content_type": item.get("content_type"),
                            }
                            await session.flush()
                        pages = parse_file(path)
                        saved = await save_document_pages(
                            session=session,
                            document_id=doc.id,
                            path=str(path),
                            parsed_pages=pages,
                        )
                    parsed_count += 1
                    page_count += saved
                    print(f"OK: {path.name} -> {saved} pages/chunks")
                except Exception as exc:
                    failed_count += 1
                    detail = f"{type(exc).__name__}: {exc}"
                    async with session.begin():
                        await record_parse_failure(
                            session=session,
                            path=str(path),
                            sha256=file_hash,
                            source_url=url or None,
                            reason="parse_error",
                            detail=detail,
                        )
                    print(f"FAIL: {path.name}: {detail}")
    finally:
        await engine.dispose()

    print("\nParsing summary")
    print(
        f"files={len(manifest)} parsed={parsed_count} "
        f"failed={failed_count} skipped={skipped_count} "
        f"pages/chunks={page_count}"
    )


if __name__ == "__main__":
    asyncio.run(main())
