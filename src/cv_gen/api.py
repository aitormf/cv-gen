"""FastAPI web application for cv-gen."""

from __future__ import annotations

import os
from pathlib import Path

import weasyprint
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cv_gen.parser import parse_cv
from cv_gen.renderer import TEMPLATES_DIR, get_available_templates, render_html

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


# --- Production: serve frontend build ---

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa_fallback(path: str) -> HTMLResponse:
        index = FRONTEND_DIST / "index.html"
        return HTMLResponse(index.read_text(encoding="utf-8"))
