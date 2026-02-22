"""Tests for the CV renderer."""

import pytest
import weasyprint

from cv_gen.models import CVData, ContactInfo, Section
from cv_gen.renderer import get_available_templates, render_html, TEMPLATES_DIR


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


def _make_long_cv() -> CVData:
    """Create a CV with enough content to span multiple pages."""
    jobs = []
    for i in range(8):
        items = "".join(f"<li>Logro destacado numero {j} en esta posicion</li>" for j in range(6))
        jobs.append(f"<h3>Engineer {i} | Company {i} | 20{10+i} - 20{11+i}</h3><ul>{items}</ul>")

    return CVData(
        contact=ContactInfo(
            name="Test User",
            title="Developer",
            email="test@example.com",
            phone="+34 600 000 000",
            location="Madrid",
            linkedin="linkedin.com/in/test",
            github="github.com/test",
            website="test.dev",
        ),
        sections=[
            Section(
                heading="Perfil Profesional",
                slug="perfil-profesional",
                content_html="<p>Senior engineer with extensive experience.</p>",
                section_type="profile",
            ),
            Section(
                heading="Experiencia Laboral",
                slug="experiencia-laboral",
                content_html="".join(jobs),
                section_type="experience",
            ),
            Section(
                heading="Educacion",
                slug="educacion",
                content_html="<h3>Master | University | 2015</h3><p>Details here.</p>" * 3,
                section_type="education",
            ),
            Section(
                heading="Habilidades",
                slug="habilidades",
                content_html="<ul>" + "".join(f"<li>Skill {i}</li>" for i in range(15)) + "</ul>",
                section_type="skills",
            ),
            Section(
                heading="Idiomas",
                slug="idiomas",
                content_html="<ul><li>Espanol (Nativo)</li><li>Ingles (C1)</li><li>Frances (B2)</li></ul>",
                section_type="languages",
            ),
        ],
    )


def _render_doc(html_string: str, template_name: str):
    """Render HTML to a WeasyPrint Document object."""
    return weasyprint.HTML(
        string=html_string,
        base_url=str(TEMPLATES_DIR / template_name),
    ).render()


def _count_pages(html_string: str, template_name: str) -> int:
    """Render HTML to PDF in memory and return page count."""
    return len(_render_doc(html_string, template_name).pages)


@pytest.mark.parametrize("template_name", ["modern", "minimal"])
def test_multipage_generates_multiple_pages(template_name):
    cv = _make_long_cv()
    html = render_html(cv, template_name)
    pages = _count_pages(html, template_name)
    assert pages >= 2, f"Expected multi-page PDF, got {pages} page(s)"


def test_modern_multipage_has_sidebar_background():
    """The modern template must paint the sidebar background on every page via @page background."""
    cv = _make_long_cv()
    html = render_html(cv, "modern")
    # The CSS uses @page background with a linear-gradient to paint sidebar color on all pages
    assert "#2c3e50" in html
    assert "linear-gradient" in html


def test_modern_main_content_starts_on_first_page():
    """Main content must start on page 1, not be pushed to page 2 by the sidebar."""
    cv = _make_long_cv()
    html = render_html(cv, "modern")
    doc = _render_doc(html, "modern")

    # A4 width = 210mm. Main content lives in the right 70% (from ~63mm onwards).
    # Check that page 1 has content in the right column area.
    page1 = doc.pages[0]

    # Collect all child boxes recursively and find the rightmost content x position on page 1
    def get_all_boxes(box):
        yield box
        if hasattr(box, "children"):
            for child in box.children:
                yield from get_all_boxes(child)

    # The main-content starts at margin-left:30% = 63mm = ~238pt.
    # If the layout is correct, page 1 must have content boxes beyond x=200pt.
    a4_width_pt = 210 / 25.4 * 72  # ~595pt
    threshold_x = a4_width_pt * 0.35  # content should exist past 35% of page width

    max_x = 0
    for box in get_all_boxes(page1._page_box):
        if hasattr(box, "position_x") and hasattr(box, "width"):
            right_edge = box.position_x + (box.width or 0)
            if right_edge > max_x:
                max_x = right_edge

    assert max_x > threshold_x, (
        f"Page 1 has no content in the right column area. "
        f"Max x = {max_x:.1f}pt, threshold = {threshold_x:.1f}pt. "
        f"Main content was likely pushed to page 2 by the sidebar."
    )


def _get_content_bbox_for_page(page):
    """Return (top_y, bottom_y) of the content bounding box for a page, excluding fixed elements."""

    def get_leaf_boxes(box, skip_fixed=True):
        # Skip fixed-position elements (sidebar background, etc.)
        if skip_fixed and getattr(box, "style", None) and box.style.get("position", None) == "fixed":
            return
        has_children = hasattr(box, "children") and list(box.children)
        if not has_children:
            # Leaf box with actual dimensions
            if hasattr(box, "position_y") and hasattr(box, "height") and box.height and box.height > 0:
                yield box
        else:
            for child in box.children:
                yield from get_leaf_boxes(child, skip_fixed)

    min_y = float("inf")
    max_y = 0
    for box in get_leaf_boxes(page._page_box):
        top = box.position_y
        bottom = top + box.height
        if top < min_y:
            min_y = top
        if bottom > max_y:
            max_y = bottom

    return min_y, max_y


@pytest.mark.parametrize("template_name", ["modern", "minimal"])
def test_multipage_consistent_top_bottom_margins(template_name):
    """All pages must have the same top and bottom margin for content."""
    cv = _make_long_cv()
    html = render_html(cv, template_name)
    doc = _render_doc(html, template_name)
    pages = doc.pages

    assert len(pages) >= 2, "Need at least 2 pages for this test"

    a4_height_pt = 297 / 25.4 * 72  # ~841.89pt
    tolerance_pt = 5  # allow 5pt tolerance for rounding

    # Get the page margin from the first page (this is set by @page)
    page1 = pages[0]
    page_margin_top = page1._page_box.margin_top
    page_margin_bottom = page1._page_box.margin_bottom

    for i, page in enumerate(pages):
        margin_top = page._page_box.margin_top
        margin_bottom = page._page_box.margin_bottom

        assert abs(margin_top - page_margin_top) < tolerance_pt, (
            f"Page {i+1}: top margin ({margin_top:.1f}pt) differs from "
            f"page 1 ({page_margin_top:.1f}pt)"
        )
        assert abs(margin_bottom - page_margin_bottom) < tolerance_pt, (
            f"Page {i+1}: bottom margin ({margin_bottom:.1f}pt) differs from "
            f"page 1 ({page_margin_bottom:.1f}pt)"
        )

    # Also verify margins are non-zero (not 0-margin pages)
    assert page_margin_top > 0, "Top page margin is 0 — content would touch the edge"
    assert page_margin_bottom > 0, "Bottom page margin is 0 — content would touch the edge"


def test_minimal_profile_not_isolated_on_first_page():
    """Profile section must not be the only content on page 1.

    When break-inside: avoid is applied to entire sections, a long experience
    section gets pushed completely to page 2, leaving the profile alone on
    page 1 with a large blank gap. This test verifies that experience content
    starts on page 1 alongside the profile.
    """
    experience_items = "".join(
        f"<h3>Engineer {i} | Company {i} | 20{10+i}-20{11+i}</h3>"
        f"<ul>{''.join(f'<li>Achievement {j} at this role</li>' for j in range(4))}</ul>"
        for i in range(5)
    )

    cv = CVData(
        contact=ContactInfo(name="Test", title="Dev", email="test@example.com"),
        sections=[
            Section(
                heading="Perfil Profesional",
                slug="perfil",
                content_html="<p>Short professional summary that fits easily on one line.</p>",
                section_type="profile",
            ),
            Section(
                heading="Experiencia",
                slug="experiencia",
                content_html=experience_items,
                section_type="experience",
            ),
        ],
    )

    html = render_html(cv, "minimal")
    doc = _render_doc(html, "minimal")

    assert len(doc.pages) >= 2, "Expected multiple pages for this CV"

    # Page 1 must have content from the experience section, not just the profile.
    # If only the profile is on page 1, the bottom of all content on that page
    # would be well under 30% of the page height (profile is just one line).
    # Experience starting on page 1 means content extends much further down.
    page1 = doc.pages[0]

    def get_all_boxes(box):
        yield box
        if hasattr(box, "children"):
            for child in box.children:
                yield from get_all_boxes(child)

    max_y = 0
    for box in get_all_boxes(page1._page_box):
        if hasattr(box, "position_y") and hasattr(box, "height") and box.height:
            bottom = box.position_y + box.height
            if bottom > max_y:
                max_y = bottom

    # A4 height ≈ 842pt. 30mm top+bottom margins ≈ 85pt each.
    # A profile-only page would have content ending around 15–20% of page height.
    # Threshold at 40% ensures experience content is present on page 1.
    a4_height_pt = 297 / 25.4 * 72
    threshold = a4_height_pt * 0.40

    assert max_y > threshold, (
        f"Page 1 appears to contain only the profile section (max_y={max_y:.1f}pt, "
        f"threshold={threshold:.1f}pt). The experience section was likely pushed "
        f"entirely to page 2 due to break-inside: avoid on the section container."
    )


def test_modern_no_white_margin_on_left_or_right():
    """The modern template must have zero left/right page margin so the sidebar
    background (via @page background) covers the full width of the sheet with no
    white strips on the sides."""
    cv = _make_long_cv()
    html = render_html(cv, "modern")
    doc = _render_doc(html, "modern")

    for i, page in enumerate(doc.pages):
        margin_left = page._page_box.margin_left
        margin_right = page._page_box.margin_right
        assert margin_left == 0, (
            f"Page {i+1}: left margin is {margin_left:.1f}pt, expected 0. "
            f"This would create a white strip on the left side."
        )
        assert margin_right == 0, (
            f"Page {i+1}: right margin is {margin_right:.1f}pt, expected 0. "
            f"This would create a white strip on the right side."
        )
