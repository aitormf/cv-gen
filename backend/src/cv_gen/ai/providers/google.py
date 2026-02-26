"""Google Gemini AI provider."""

from __future__ import annotations

from google import genai
from google.genai import types


class GoogleProvider:
    """AI provider backed by Google Gemini (google-genai SDK)."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def complete(self, system_prompt: str, user_text: str) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=user_text,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text

    async def complete_with_pdf(self, system_prompt: str, pdf_bytes: bytes) -> str:
        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=pdf_part,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text
