import re
from dataclasses import dataclass
from pathlib import Path

CHUNK_SIZE = 3000

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".rst",
    ".py",
    ".js",
    ".css",
    ".html",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".sh",
    ".bat",
}


class ParseError(Exception):
    """A permanent error in a source document that should not be retried."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        super().__init__(detail or reason)


@dataclass
class ParsedPage:
    page_no: int
    text: str
    headings: list[str]


def clean_text(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = content.replace("\x00", "")
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def extract_heading(line: str):
    match = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", line)
    if match:
        return match.group(2).strip(), len(match.group(1))
    return None


RST_HEADING_CHARS = set("=-~^\"':+*#")


def valid_underline(line: str, title: str) -> bool:
    line = line.strip()
    if not line or len(line) < len(title) or len(set(line)) != 1:
        return False
    return line[0] in RST_HEADING_CHARS


def get_rst_level(char: str) -> int:
    levels = {"=": 1, "-": 2, "~": 3, "^": 4, '"': 5, ":": 6, "+": 6, "*": 6, "#": 6}
    return levels.get(char, 1)


def extract_rst_heading(lines: list[str], index: int):
    if index >= len(lines):
        return None

    # RST overline + title + underline format.
    if index + 2 < len(lines):
        overline = lines[index].strip()
        title = lines[index + 1].strip()
        underline = lines[index + 2].strip()
        if (
            title
            and valid_underline(overline, title)
            and valid_underline(underline, title)
            and overline[0] == underline[0]
        ):
            return title, get_rst_level(overline[0])

    # RST title + underline format.
    if index + 1 < len(lines):
        title = lines[index].strip()
        underline = lines[index + 1].strip()
        if title and valid_underline(underline, title):
            return title, get_rst_level(underline[0])

    return None


def split_long_text(text: str, max_size: int = CHUNK_SIZE) -> list[str]:
    if max_size <= 0:
        raise ValueError("max_size must be greater than zero")

    text = text.strip()
    if not text:
        return []

    chunks = []
    while len(text) > max_size:
        split_at = text.rfind(" ", 0, max_size)
        if split_at <= 0:
            split_at = max_size
        chunk = text[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        text = text[split_at:].strip()

    if text:
        chunks.append(text)
    return chunks


def parse_text(content: str, chunk_size: int = CHUNK_SIZE) -> list[ParsedPage]:
    content = clean_text(content)
    if not content:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    lines = content.splitlines()
    pages = []
    heading_stack = []
    current_heading_path = []
    current_content = []
    page_no = 1
    inside_code_block = False
    code_marker = None

    def save_chunk():
        nonlocal page_no, current_content
        text = clean_text("\n".join(current_content))
        if not text:
            current_content = []
            return
        for chunk in split_long_text(text, chunk_size):
            pages.append(ParsedPage(page_no, chunk, current_heading_path.copy()))
            page_no += 1
        current_content = []

    def add_content(text: str):
        text = text.strip()
        if not text:
            return
        existing = "\n".join(current_content)
        if existing and len(existing) + len(text) + 1 > chunk_size:
            save_chunk()
        current_content.append(text)
        if len("\n".join(current_content)) > chunk_size:
            save_chunk()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Ignore Markdown headings inside fenced code blocks.
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not inside_code_block:
                inside_code_block = True
                code_marker = marker
            elif marker == code_marker:
                inside_code_block = False
                code_marker = None
            add_content(line)
            i += 1
            continue

        if inside_code_block:
            add_content(line)
            i += 1
            continue

        markdown_heading = extract_heading(line)
        if markdown_heading:
            title, level = markdown_heading
            save_chunk()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            current_heading_path = [item[1] for item in heading_stack]
            add_content(title)
            i += 1
            continue

        rst_heading = extract_rst_heading(lines, i)
        if rst_heading:
            title, level = rst_heading
            save_chunk()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            current_heading_path = [item[1] for item in heading_stack]
            add_content(title)
            if i + 2 < len(lines) and lines[i].strip() == lines[i + 2].strip():
                i += 3
            else:
                i += 2
            continue

        add_content(line)
        i += 1

    save_chunk()
    return pages


def parse_file(path: Path) -> list[ParsedPage]:
    path = Path(path)
    if not path.exists():
        raise ParseError("missing_file", str(path))
    if not path.is_file():
        raise ParseError("not_a_file", f"Not a file: {path}")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ParseError("unsupported_type", f"Unsupported file type: {suffix}")
    content = path.read_text(encoding="utf-8", errors="replace")
    return parse_text(content)


def parse_html(path: Path) -> list[ParsedPage]:
    import trafilatura

    path = Path(path)
    html_content = path.read_text(encoding="utf-8", errors="replace")
    extracted = trafilatura.extract(
        html_content,
        include_tables=True,
        include_comments=False,
        include_links=False,
        output_format="txt",
    )
    if not extracted:
        raise ParseError("empty_html", "No readable content extracted from HTML")
    return parse_text(extracted)


def parse_pdf(path: Path) -> list[ParsedPage]:
    """Extract PDF text while preserving each source PDF page number."""
    import pymupdf

    path = Path(path)
    try:
        document = pymupdf.open(path)
    except (pymupdf.FileDataError, ValueError, OSError) as error:
        raise ParseError("invalid_pdf", str(error)) from error
    parsed_pages = []

    try:
        for source_page_no, pdf_page in enumerate(document, start=1):
            text = clean_text(pdf_page.get_text())
            if not text:
                continue

            # Keep one ParsedPage per actual PDF page so page_no maps
            # directly to the original PDF page number in the source.
            blocks = pdf_page.get_text("dict").get("blocks", [])
            page_headings = []
            font_sizes = []

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    line_text = "".join(
                        span.get("text", "") for span in line.get("spans", [])
                    ).strip()
                    sizes = [
                        span.get("size", 0)
                        for span in line.get("spans", [])
                        if span.get("text", "").strip()
                    ]
                    if not line_text or not sizes:
                        continue
                    avg_size = sum(sizes) / len(sizes)
                    font_sizes.append(avg_size)

            median_font_size = sorted(font_sizes)[len(font_sizes) // 2] if font_sizes else 0

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    line_text = "".join(
                        span.get("text", "") for span in line.get("spans", [])
                    ).strip()
                    sizes = [
                        span.get("size", 0)
                        for span in line.get("spans", [])
                        if span.get("text", "").strip()
                    ]
                    if not line_text or not sizes:
                        continue
                    avg_size = sum(sizes) / len(sizes)
                    if (
                        median_font_size
                        and avg_size > median_font_size * 1.15
                        and len(line_text) < 150
                    ):
                        page_headings.append(line_text)

            parsed_pages.append(
                ParsedPage(
                    page_no=source_page_no,
                    text=text,
                    headings=page_headings,
                )
            )
    finally:
        document.close()

    return parsed_pages


def parse_document(path: Path) -> list[ParsedPage]:
    """Parse a supported source format and report permanent document errors consistently."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pages = parse_pdf(path)
    elif suffix in {".html", ".htm"}:
        pages = parse_html(path)
    else:
        pages = parse_file(path)
    if not pages:
        raise ParseError("empty_document", "No readable text found in document")
    return pages
