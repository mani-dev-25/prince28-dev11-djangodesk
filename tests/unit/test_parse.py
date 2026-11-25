from djangodesk.ingest.parse import (
    clean_text,
    extract_heading,
    extract_rst_heading,
    parse_text,
    split_long_text,
)


def test_clean_text_removes_extra_blank_lines():
    result = clean_text("Hello\n\n\n\nWorld")
    assert result == "Hello\n\nWorld"


def test_extract_markdown_heading():
    result = extract_heading("## Installation")
    assert result == ("Installation", 2)


def test_extract_rst_heading():
    lines = [
        "Django documentation",
        "====================",
    ]
    result = extract_rst_heading(lines, 0)
    assert result == ("Django documentation", 1)


def test_extract_rst_overline_heading():
    lines = [
        "====================",
        "Django documentation",
        "====================",
    ]
    result = extract_rst_heading(lines, 0)
    assert result == ("Django documentation", 1)


def test_parse_text_extracts_headings():
    content = "\n".join(
        [
            "# Main heading",
            "",
            "Some text.",
            "",
            "## Child heading",
            "",
            "More text.",
        ]
    )

    pages = parse_text(content)

    assert len(pages) >= 1
    assert pages[0].headings == ["Main heading"]


def test_parse_text_empty_content():
    assert parse_text("") == []


def test_parse_text_chunks_long_content():
    content = "A " * 5000
    pages = parse_text(content, chunk_size=100)

    assert len(pages) > 1
    assert all(len(page.text) <= 100 for page in pages)


def test_split_long_text():
    text = "Hello world " * 100
    chunks = split_long_text(text, max_size=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_heading_hierarchy():
    content = "\n".join(
        [
            "# Main",
            "",
            "Main content.",
            "",
            "## Child",
            "",
            "Child content.",
            "",
            "### Grandchild",
            "",
            "Grandchild content.",
        ]
    )

    pages = parse_text(content)

    assert pages[0].headings == ["Main"]

    child_page = next(page for page in pages if "Child content." in page.text)
    assert child_page.headings == ["Main", "Child"]

    grandchild_page = next(page for page in pages if "Grandchild content." in page.text)
    assert grandchild_page.headings == [
        "Main",
        "Child",
        "Grandchild",
    ]


def test_markdown_headings_inside_code_block_are_ignored():
    content = "\n".join(
        [
            "# Real heading",
            "",
            "Some content.",
            "",
            "```python",
            "# This is a code comment",
            "## Not a real heading",
            "```",
            "",
            "More content.",
        ]
    )

    pages = parse_text(content)

    assert pages
    assert all("Not a real heading" not in page.headings for page in pages)


def test_rst_heading_parsing():
    content = "\n".join(
        [
            "Django Guide",
            "============",
            "",
            "Introduction",
            "------------",
            "",
            "Welcome to Django.",
        ]
    )

    pages = parse_text(content)

    assert pages
    assert pages[0].headings == ["Django Guide"]


def test_multiple_markdown_headings():
    content = "\n".join(
        [
            "# Introduction",
            "",
            "Welcome.",
            "",
            "# Installation",
            "",
            "Install the package.",
        ]
    )

    pages = parse_text(content)

    assert len(pages) >= 2
    assert pages[0].headings == ["Introduction"]
    assert pages[-1].headings == ["Installation"]


def test_parse_text_respects_chunk_size():
    content = "This is a sentence. " * 1000
    pages = parse_text(content, chunk_size=200)

    assert len(pages) > 1
    assert all(len(page.text) <= 200 for page in pages)


def test_parse_file(tmp_path):
    from djangodesk.ingest.parse import parse_file

    test_file = tmp_path / "sample.txt"
    test_file.write_text(
        "# Sample Heading\n\nSample content.",
        encoding="utf-8",
    )

    pages = parse_file(test_file)

    assert pages
    assert pages[0].headings == ["Sample Heading"]


def test_split_long_text_empty():
    assert split_long_text("", max_size=50) == []


def test_split_long_text_invalid_size():
    import pytest

    with pytest.raises(ValueError):
        split_long_text("Hello world", max_size=0)
