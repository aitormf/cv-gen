"""Tests for the CV renderer."""

import pytest

from cv_gen.models import CVData, ContactInfo, Section
from cv_gen.renderer import get_available_templates, render_html


@pytest.fixture
def sample_cv():
    return CVData(
        contact=ContactInfo(
            name="Test User",
            title="Developer",
            email="test@example.com",
            phone="+34 600 000 000",
            location="Madrid",
        ),
        sections=[
            Section(
                heading="Perfil",
                slug="perfil",
                content_html="<p>Experienced developer.</p>",
                section_type="profile",
            ),
            Section(
                heading="Experience",
                slug="experience",
                content_html="<h3>Senior Dev | Company</h3><ul><li>Did things</li></ul>",
                section_type="experience",
            ),
            Section(
                heading="Skills",
                slug="skills",
                content_html="<ul><li>Python</li><li>Go</li></ul>",
                section_type="skills",
            ),
        ],
    )


def test_available_templates():
    templates = get_available_templates()
    assert "modern" in templates
    assert "minimal" in templates


def test_render_modern_html(sample_cv):
    html = render_html(sample_cv, "modern")
    assert "Test User" in html
    assert "Developer" in html
    assert "test@example.com" in html
    assert "Experienced developer." in html
    assert "sidebar" in html


def test_render_minimal_html(sample_cv):
    html = render_html(sample_cv, "minimal")
    assert "Test User" in html
    assert "Developer" in html
    assert "Experienced developer." in html


def test_invalid_template(sample_cv):
    with pytest.raises(ValueError, match="not found"):
        render_html(sample_cv, "nonexistent")
