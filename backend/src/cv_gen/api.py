"""FastAPI web application for cv-gen."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import weasyprint
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cv_gen.ai.providers import get_provider, is_ai_configured
from cv_gen.extractors import SUPPORTED_EXTENSIONS, extract_text, get_extension
from cv_gen.parser import parse_cv
from cv_gen.renderer import TEMPLATES_DIR, get_available_templates, render_html

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")

app = FastAPI(title="cv-gen")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RenderRequest(BaseModel):
    markdown: str
    template: str = "modern"


@app.get("/api/templates")
def list_templates() -> dict:
    return {"templates": get_available_templates(), "default": "modern"}


@app.post("/api/pdf")
def pdf(req: RenderRequest) -> Response:
    available = get_available_templates()
    if req.template not in available:
        raise HTTPException(400, f"Unknown template '{req.template}'. Available: {', '.join(available)}")
    cv = parse_cv(req.markdown)
    html_string = render_html(cv, req.template)
    pdf_bytes = weasyprint.HTML(
        string=html_string,
        base_url=str(TEMPLATES_DIR / req.template),
    ).write_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cv.pdf"},
    )


# --- AI document conversion ---


def _strip_code_fences(text: str) -> str:
    """Remove wrapping Markdown code fences that LLMs sometimes add."""
    return re.sub(r"^```(?:markdown|md|yaml)?\n(.*?)```\s*$", r"\1", text, flags=re.DOTALL)


@app.get("/api/ai/status")
def ai_status() -> dict:
    return {"available": is_ai_configured()}


@app.post("/api/ai/convert")
async def ai_convert(file: UploadFile) -> dict:
    if not is_ai_configured():
        raise HTTPException(503, "AI conversion is not configured")

    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    filename = file.filename or ""
    ext = get_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    from cv_gen.ai.prompt import SYSTEM_PROMPT

    provider = get_provider()

    try:
        if ext == ".pdf":
            raw = await provider.complete_with_pdf(SYSTEM_PROMPT, content)
        else:
            text = extract_text(content, filename)
            if not text.strip():
                raise HTTPException(422, "Could not extract text from document")
            raw = await provider.complete(SYSTEM_PROMPT, text)
    except HTTPException:
        raise
    except Exception:
        logger.exception("AI conversion failed")
        raise HTTPException(502, "AI conversion failed")

    return {"markdown": _strip_code_fences(raw)}


# --- AI CV adaptation ---


class AdaptRequest(BaseModel):
    markdown: str
    job_offer: str


@app.post("/api/ai/adapt")
async def ai_adapt(req: AdaptRequest) -> dict:
    if not is_ai_configured():
        raise HTTPException(503, "AI adaptation is not configured")
    if not req.markdown.strip():
        raise HTTPException(400, "CV markdown is empty")
    if not req.job_offer.strip():
        raise HTTPException(400, "Job offer text is empty")

    from cv_gen.ai.prompt import ADAPT_SYSTEM_PROMPT, build_adapt_user_prompt

    provider = get_provider()
    user_text = build_adapt_user_prompt(req.markdown, req.job_offer)

    try:
        raw = await provider.complete(ADAPT_SYSTEM_PROMPT, user_text)
    except Exception:
        logger.exception("AI adaptation failed")
        raise HTTPException(502, "AI adaptation failed")

    return {"markdown": _strip_code_fences(raw)}


# --- Production: serve frontend build ---

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa_fallback(path: str) -> HTMLResponse:
        index = FRONTEND_DIST / "index.html"
        return HTMLResponse(index.read_text(encoding="utf-8"))
