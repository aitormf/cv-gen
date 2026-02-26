"""Anthropic AI provider."""

from __future__ import annotations

import base64

import anthropic


class AnthropicProvider:
    """AI provider backed by the Anthropic API."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(self, system_prompt: str, user_text: str) -> str:
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_text}],
        )
        return message.content[0].text

    async def complete_with_pdf(self, system_prompt: str, pdf_bytes: bytes) -> str:
        b64 = base64.standard_b64encode(pdf_bytes).decode()
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": b64,
                            },
                        },
                    ],
                },
            ],
        )
        return message.content[0].text
