"""Tests for the extractors module."""

from __future__ import annotations

import io

import pytest
from docx import Document

from cv_gen.extractors import SUPPORTED_EXTENSIONS, extract_text, get_extension


def _make_docx(paragraphs: list[str]) -> bytes:
    """Create a minimal DOCX file in memory."""
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestExtractText:
    def test_docx_basic(self):
        content = _make_docx(["Hello", "World"])
        result = extract_text(content, "test.docx")
        assert "Hello" in result
        assert "World" in result

    def test_unsupported_type(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text(b"some text", "file.txt")


class TestGetExtension:
    def test_lowercase(self):
        assert get_extension("file.PDF") == ".pdf"

    def test_docx(self):
        assert get_extension("resume.docx") == ".docx"

    def test_no_extension(self):
        assert get_extension("noext") == ""

    def test_multiple_dots(self):
        assert get_extension("my.file.DOCX") == ".docx"


class TestSupportedExtensions:
    def test_contains_pdf(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS

    def test_contains_docx(self):
        assert ".docx" in SUPPORTED_EXTENSIONS
