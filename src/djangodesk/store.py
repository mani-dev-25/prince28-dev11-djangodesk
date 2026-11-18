"""Loads records from a JSON file into memory and answers simple lookups."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RecordStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: list[dict] = []
        self.loaded = False

    def load(self) -> None:
        """Read the JSON file. On any problem, log it and stay 'not loaded'."""
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("top level of the file must be a list")
        except (OSError, ValueError) as exc:
            self.records = []
            self.loaded = False
            logger.error(f"could not load records: {exc}")
            return
        self.records = data
        self.loaded = True
        logger.info("records loaded", extra={"fields": {"records": len(data)}})

    def get(self, record_id: str) -> dict | None:
        """Return the record with this id, or None."""
        return next((r for r in self.records if r.get("id") == record_id), None)

    def search(self, q: str) -> list[dict]:
        """Return records where any value contains the text (case-insensitive)."""
        q = q.lower()
        return [r for r in self.records if any(q in str(v).lower() for v in r.values())]
