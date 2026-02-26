"""Base protocol for AI providers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class AIProvider(Protocol):
    """Duck-typed interface that every AI provider must satisfy."""

    async def complete(self, system_prompt: str, user_text: str) -> str:
        """Send a text prompt and return the model response."""
        ...

    async def complete_with_pdf(self, system_prompt: str, pdf_bytes: bytes) -> str:
        """Send a PDF document and return the model response."""
        ...
