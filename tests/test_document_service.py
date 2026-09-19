from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.services.document_service import (
    clean_text,
    chunk_text,
    sanitize_filename,
    extract_text_from_pdf,
)


# ---- clean_text ----

def test_clean_text_collapses_repeated_spaces():
    assert clean_text("hello    world") == "hello world"


def test_clean_text_collapses_excessive_newlines():
    assert clean_text("para one\n\n\n\npara two") == "para one\n\npara two"


def test_clean_text_removes_null_bytes():
    assert "\x00" not in clean_text("bad\x00text")


def test_clean_text_strips_leading_trailing_whitespace():
    assert clean_text("   padded text   ") == "padded text"


# ---- chunk_text ----

def test_chunk_text_empty_string_returns_empty_list():
    assert chunk_text("") == []


def test_chunk_text_respects_chunk_size():
    text = " ".join(f"word{i}" for i in range(1000))
    chunks = chunk_text(text, chunk_size=100, overlap=10)

    for chunk in chunks[:-1]:
        assert len(chunk.split()) == 100


def test_chunk_text_overlap_shares_words_between_chunks():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    first_tail = chunks[0].split()[-20:]
    second_head = chunks[1].split()[:20]
    assert first_tail == second_head


def test_chunk_text_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_text("some text here", chunk_size=100, overlap=100)


def test_chunk_text_single_short_text_returns_one_chunk():
    assert chunk_text("just a few words") == ["just a few words"]


# ---- sanitize_filename ----

def test_sanitize_filename_strips_directory_components():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"


def test_sanitize_filename_replaces_unsafe_characters():
    result = sanitize_filename("my report?!.pdf")
    assert "?" not in result and "!" not in result


def test_sanitize_filename_empty_input_returns_fallback():
    assert sanitize_filename("") == "document.pdf"


# ---- extract_text_from_pdf ----

def test_extract_text_from_pdf_empty_pdf_returns_empty_string(tmp_path: Path):
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)

    pdf_path = tmp_path / "blank.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)

    text = extract_text_from_pdf(pdf_path)
    assert text == ""
