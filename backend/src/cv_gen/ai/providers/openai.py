"""OpenAI (and compatible) AI provider."""

from __future__ import annotations

import base64

from openai import AsyncOpenAI


class OpenAIProvider:
    """AI provider backed by the OpenAI API.

    Supports any OpenAI-compatible service via ``base_url``
    (LiteLLM, Ollama, Azure, etc.).
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self._model = model

    async def complete(self, system_prompt: str, user_text: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )
        return response.choices[0].message.content

    async def complete_with_pdf(self, system_prompt: str, pdf_bytes: bytes) -> str:
        b64 = base64.standard_b64encode(pdf_bytes).decode()
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "filename": "document.pdf",
                                "file_data": f"data:application/pdf;base64,{b64}",
                            },
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content
