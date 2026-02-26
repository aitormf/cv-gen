"""Parse Markdown CV files into CVData."""

from __future__ import annotations

import re
import unicodedata

import frontmatter
import markdown

from cv_gen.models import CVData, ContactInfo, Section

# Keywords for section type detection (multilingual: ES, EN, FR, DE)
SECTION_KEYWORDS: dict[str, list[str]] = {
    "profile": [
        "perfil", "profile", "profil", "about", "sobre mi", "resumen",
        "summary", "objetivo", "objective", "presentacion",
    ],
    "experience": [
        "experiencia", "experience", "erfahrung", "trabajo", "work",
        "empleos", "employment", "professional",
    ],
    "education": [
        "educacion", "formacion", "formation", "education", "ausbildung", "estudios",
        "academic", "akademisch",
    ],
    "skills": [
        "habilidades", "skills", "competencias", "competences", "kenntnisse", "tecnologias",
        "technologies", "tech stack", "herramientas", "tools",
    ],
    "languages": [
        "idiomas", "languages", "sprachen", "langues",
    ],
    "projects": [
        "proyectos", "projects", "projekte", "projets", "portfolio",
    ],
    "certifications": [
        "certificaciones", "certifications", "certificados", "zertifikate",
        "certificats", "cursos", "courses",
    ],
}

MD_EXTENSIONS = ["tables", "smarty", "sane_lists"]


def _normalize(text: str) -> str:
    """Normalize text for keyword matching: lowercase, strip accents."""
    text = text.lower().strip()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _slugify(text: str) -> str:
    """Convert heading to a URL-friendly slug."""
    text = _normalize(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _detect_section_type(heading: str) -> str:
    """Detect section type from heading using keyword matching."""
    normalized = _normalize(heading)
    for section_type, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return section_type
    return "other"


def _render_md(text: str) -> str:
    """Render Markdown text to HTML."""
    return markdown.markdown(text, extensions=MD_EXTENSIONS)


def parse_cv(text: str) -> CVData:
    """Parse a Markdown CV string into CVData."""
    post = frontmatter.loads(text)

    # Build ContactInfo from frontmatter
    meta = post.metadata
    contact = ContactInfo(
        name=str(meta.get("name", "")),
        title=str(meta.get("title", "")),
        email=str(meta.get("email", "")),
        phone=str(meta.get("phone", "")),
        location=str(meta.get("location", "")),
        linkedin=str(meta.get("linkedin", "")),
        github=str(meta.get("github", "")),
        website=str(meta.get("website", "")),
        photo=str(meta.get("photo", "")),
    )

    # Split body by h2 headings (## )
    body = post.content
    sections: list[Section] = []

    # Content before the first ## is treated as profile
    parts = re.split(r"^## ", body, flags=re.MULTILINE)

    # First part is content before any ## heading
    preamble = parts[0].strip()
    if preamble:
        sections.append(Section(
            heading="Perfil",
            slug="perfil",
            content_html=_render_md(preamble),
            section_type="profile",
        ))

    # Remaining parts are "Heading\ncontent..."
    for part in parts[1:]:
        lines = part.split("\n", 1)
        heading = lines[0].strip()
        content = lines[1] if len(lines) > 1 else ""
        content = content.strip()

        section_type = _detect_section_type(heading)
        content_html = _render_md(content) if content else ""

        sections.append(Section(
            heading=heading,
            slug=_slugify(heading),
            content_html=content_html,
            section_type=section_type,
        ))

    return CVData(contact=contact, sections=sections)


def parse_cv_file(path: str) -> CVData:
    """Parse a Markdown CV file into CVData."""
    with open(path, encoding="utf-8") as f:
        return parse_cv(f.read())
