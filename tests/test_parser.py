"""Tests for the Markdown CV parser."""

from cv_gen.parser import parse_cv, _detect_section_type, _slugify


SAMPLE_MD = """\
---
name: Test User
title: Developer
email: test@example.com
phone: "+34 600 000 000"
location: Madrid
linkedin: linkedin.com/in/test
github: github.com/test
website: test.dev
photo: photo.jpg
---

## Perfil Profesional
Soy un developer con experiencia.

## Experiencia Laboral
### Senior Dev | Company | 2020 - Presente
- Logro 1
- Logro 2

## Educacion
### Master en CS | UPM | 2017

## Habilidades
- Python, Go
- Docker, K8s

## Idiomas
- Espanol (Nativo)
- Ingles (C1)
"""


def test_parse_contact_info():
    cv = parse_cv(SAMPLE_MD)
    assert cv.contact.name == "Test User"
    assert cv.contact.title == "Developer"
    assert cv.contact.email == "test@example.com"
    assert cv.contact.phone == "+34 600 000 000"
    assert cv.contact.location == "Madrid"
    assert cv.contact.linkedin == "linkedin.com/in/test"
    assert cv.contact.github == "github.com/test"
    assert cv.contact.website == "test.dev"
    assert cv.contact.photo == "photo.jpg"


def test_parse_sections_count():
    cv = parse_cv(SAMPLE_MD)
    assert len(cv.sections) == 5


def test_parse_section_types():
    cv = parse_cv(SAMPLE_MD)
    types = [s.section_type for s in cv.sections]
    assert types == ["profile", "experience", "education", "skills", "languages"]


def test_parse_section_headings():
    cv = parse_cv(SAMPLE_MD)
    headings = [s.heading for s in cv.sections]
    assert headings == [
        "Perfil Profesional",
        "Experiencia Laboral",
        "Educacion",
        "Habilidades",
        "Idiomas",
    ]


def test_section_html_contains_content():
    cv = parse_cv(SAMPLE_MD)
    profile = cv.sections[0]
    assert "developer con experiencia" in profile.content_html

    experience = cv.sections[1]
    assert "Logro 1" in experience.content_html
    assert "<li>" in experience.content_html


def test_sidebar_and_main_sections():
    cv = parse_cv(SAMPLE_MD)
    sidebar = cv.sidebar_sections()
    main = cv.main_sections()

    sidebar_types = {s.section_type for s in sidebar}
    main_types = {s.section_type for s in main}

    assert sidebar_types == {"skills", "languages"}
    assert "experience" in main_types
    assert "education" in main_types
    assert "profile" in main_types


def test_detect_section_type_multilang():
    assert _detect_section_type("Work Experience") == "experience"
    assert _detect_section_type("Experiencia Laboral") == "experience"
    assert _detect_section_type("Formation") == "education"
    assert _detect_section_type("Compétences") == "skills"
    assert _detect_section_type("Sprachen") == "languages"
    assert _detect_section_type("Random Heading") == "other"


def test_slugify():
    assert _slugify("Perfil Profesional") == "perfil-profesional"
    assert _slugify("Experiencia Laboral") == "experiencia-laboral"
    assert _slugify("Educación") == "educacion"


def test_preamble_as_profile():
    md = """\
---
name: Test
---

Some preamble text before any heading.

## Skills
- Python
"""
    cv = parse_cv(md)
    assert cv.sections[0].section_type == "profile"
    assert "preamble text" in cv.sections[0].content_html


def test_empty_sections():
    md = """\
---
name: Test
---

## Skills
"""
    cv = parse_cv(md)
    assert len(cv.sections) == 1
    assert cv.sections[0].content_html == ""
