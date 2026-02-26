"""Render CVData to HTML and PDF using Jinja2 + WeasyPrint."""

from __future__ import annotations

from pathlib import Path

import jinja2
import weasyprint

from cv_gen.models import CVData

TEMPLATES_DIR = Path(__file__).parent / "templates"


def get_available_templates() -> list[str]:
    """Return list of available template names."""
    return sorted(
        d.name for d in TEMPLATES_DIR.iterdir()
        if d.is_dir() and (d / "template.html").exists()
    )


def render_html(cv: CVData, template_name: str = "modern") -> str:
    """Render CVData to HTML string using the specified template."""
    template_dir = TEMPLATES_DIR / template_name
    html_path = template_dir / "template.html"
    css_path = template_dir / "style.css"

    if not html_path.exists():
        available = ", ".join(get_available_templates())
        raise ValueError(
            f"Template '{template_name}' not found. Available: {available}"
        )

    html_template = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    template = env.from_string(html_template)

    return template.render(
        cv=cv,
        contact=cv.contact,
        sections=cv.sections,
        sidebar_sections=cv.sidebar_sections(),
        main_sections=cv.main_sections(),
        css=css,
    )


def render_pdf(cv: CVData, output_path: str, template_name: str = "modern") -> None:
    """Render CVData to PDF file."""
    html_string = render_html(cv, template_name)
    html = weasyprint.HTML(string=html_string, base_url=str(TEMPLATES_DIR / template_name))
    html.write_pdf(output_path)
