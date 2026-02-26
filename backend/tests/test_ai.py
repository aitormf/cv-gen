"""Tests for AI conversion feature."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, patch

import pytest
from docx import Document
from fastapi.testclient import TestClient

from cv_gen.ai.base import AIProvider
from cv_gen.ai.prompt import SYSTEM_PROMPT
from cv_gen.ai.providers import get_provider, is_ai_configured
from cv_gen.api import _strip_code_fences, app

client = TestClient(app)

FAKE_MARKDOWN = "---\nname: Test\n---\n\n## Experience\n"


# --- helpers ---


def _make_docx(paragraphs: list[str]) -> bytes:
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _mock_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.complete.return_value = FAKE_MARKDOWN
    provider.complete_with_pdf.return_value = FAKE_MARKDOWN
    return provider


# --- Protocol ---


class TestProtocol:
    def test_satisfies_protocol(self):
        class MyProvider:
            async def complete(self, system_prompt: str, user_text: str) -> str:
                return ""

            async def complete_with_pdf(self, system_prompt: str, pdf_bytes: bytes) -> str:
                return ""

        assert isinstance(MyProvider(), AIProvider)


# --- Configuration ---


class TestConfig:
    def test_not_configured_missing_provider(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")
        assert is_ai_configured() is False

    def test_not_configured_missing_key(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.delenv("AI_API_KEY", raising=False)
        monkeypatch.setenv("AI_MODEL", "model")
        assert is_ai_configured() is False

    def test_not_configured_missing_model(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.delenv("AI_MODEL", raising=False)
        assert is_ai_configured() is False

    def test_configured(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "gemini-2.0-flash")
        assert is_ai_configured() is True

    def test_unknown_provider(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "unknown")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")
        with pytest.raises(ValueError, match="Unknown AI provider"):
            get_provider()

    def test_missing_model(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.delenv("AI_MODEL", raising=False)
        with pytest.raises(RuntimeError, match="AI_MODEL"):
            get_provider()


# --- Prompt ---


class TestPrompt:
    @pytest.mark.parametrize(
        "field",
        ["name", "title", "email", "phone", "location", "linkedin", "github", "website"],
    )
    def test_contains_contact_field(self, field):
        assert field in SYSTEM_PROMPT


# --- _strip_code_fences ---


class TestStripCodeFences:
    def test_with_markdown_fence(self):
        text = "```markdown\n---\nname: Test\n---\n```"
        assert _strip_code_fences(text) == "---\nname: Test\n---\n"

    def test_with_md_fence(self):
        text = "```md\ncontent\n```"
        assert _strip_code_fences(text) == "content\n"

    def test_with_plain_fence(self):
        text = "```\ncontent\n```"
        assert _strip_code_fences(text) == "content\n"

    def test_without_fence(self):
        text = "---\nname: Test\n---\n"
        assert _strip_code_fences(text) == text


# --- API endpoints ---


class TestAiStatus:
    def test_not_configured(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        monkeypatch.delenv("AI_API_KEY", raising=False)
        monkeypatch.delenv("AI_MODEL", raising=False)
        resp = client.get("/api/ai/status")
        assert resp.status_code == 200
        assert resp.json() == {"available": False}


class TestAiConvert:
    def test_not_configured(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        monkeypatch.delenv("AI_API_KEY", raising=False)
        monkeypatch.delenv("AI_MODEL", raising=False)
        resp = client.post("/api/ai/convert", files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")})
        assert resp.status_code == 503

    def test_unsupported_file(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")
        resp = client.post("/api/ai/convert", files={"file": ("file.txt", b"text", "text/plain")})
        assert resp.status_code == 400

    def test_empty_file(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")
        resp = client.post("/api/ai/convert", files={"file": ("cv.pdf", b"", "application/pdf")})
        assert resp.status_code == 400

    def test_pdf_conversion(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")

        provider = _mock_provider()
        with patch("cv_gen.api.get_provider", return_value=provider):
            resp = client.post(
                "/api/ai/convert",
                files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
            )

        assert resp.status_code == 200
        assert resp.json()["markdown"] == FAKE_MARKDOWN
        provider.complete_with_pdf.assert_called_once()

    def test_docx_conversion(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "google")
        monkeypatch.setenv("AI_API_KEY", "key")
        monkeypatch.setenv("AI_MODEL", "model")

        docx_bytes = _make_docx(["John Doe", "Software Engineer"])
        provider = _mock_provider()
        with patch("cv_gen.api.get_provider", return_value=provider):
            resp = client.post(
                "/api/ai/convert",
                files={"file": ("cv.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )

        assert resp.status_code == 200
        assert resp.json()["markdown"] == FAKE_MARKDOWN
        provider.complete.assert_called_once()
        # Verify text was extracted and passed
        call_text = provider.complete.call_args[0][1]
        assert "John Doe" in call_text


# --- Provider instantiation ---


class TestProviders:
    def test_google_provider_instantiates(self):
        from cv_gen.ai.providers.google import GoogleProvider

        p = GoogleProvider(api_key="test-key", model="gemini-2.0-flash")
        assert p._model == "gemini-2.0-flash"

    def test_openai_provider_instantiates(self):
        from cv_gen.ai.providers.openai import OpenAIProvider

        p = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
        assert p._model == "gpt-4o-mini"

    def test_openai_provider_custom_base_url(self):
        from cv_gen.ai.providers.openai import OpenAIProvider

        p = OpenAIProvider(api_key="test-key", model="gpt-4o", base_url="http://localhost:8080")
        assert p._model == "gpt-4o"

    def test_anthropic_provider_instantiates(self):
        from cv_gen.ai.providers.anthropic import AnthropicProvider

        p = AnthropicProvider(api_key="test-key", model="claude-sonnet-4-20250514")
        assert p._model == "claude-sonnet-4-20250514"

    def test_openrouter_uses_openai_provider(self, monkeypatch):
        from cv_gen.ai.providers.openai import OpenAIProvider

        monkeypatch.setenv("AI_PROVIDER", "openrouter")
        monkeypatch.setenv("AI_API_KEY", "sk-or-test")
        monkeypatch.setenv("AI_MODEL", "anthropic/claude-sonnet-4")
        p = get_provider()
        assert isinstance(p, OpenAIProvider)
        assert p._model == "anthropic/claude-sonnet-4"
