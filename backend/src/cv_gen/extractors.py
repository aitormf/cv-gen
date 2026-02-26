"""Text extraction from document files."""

from __future__ import annotations

import os


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def get_extension(filename: str) -> str:
    """Return the lowercased file extension including the dot."""
    return os.path.splitext(filename)[-1].lower()


def extract_text(content: bytes, filename: str) -> str:
    """Extract plain text from a document.

    Currently supports .docx files.  PDF files are handled directly
    by multimodal AI providers so they don't go through this function.
    """
    ext = get_extension(filename)
    if ext == ".docx":
        return _extract_docx(content)
    raise ValueError(f"Unsupported file type: {ext}")


def _extract_docx(content: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    import io

    from docx import Document

    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)
