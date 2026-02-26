"""Tests for the FastAPI web API."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from cv_gen.api import app

client = TestClient(app)

SAMPLE_MD = (Path(__file__).resolve().parent.parent / "examples" / "sample_cv.md").read_text(encoding="utf-8")


def test_list_templates():
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert "modern" in data["templates"]
    assert "minimal" in data["templates"]
    assert data["default"] == "modern"


def test_pdf_download():
    resp = client.post("/api/pdf", json={"markdown": SAMPLE_MD, "template": "modern"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


def test_pdf_invalid_template():
    resp = client.post("/api/pdf", json={"markdown": SAMPLE_MD, "template": "nonexistent"})
    assert resp.status_code == 400


def test_pdf_empty_markdown():
    resp = client.post("/api/pdf", json={"markdown": "", "template": "modern"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
