"""Tests for the CLI."""

from click.testing import CliRunner

from cv_gen.cli import main


def test_list_templates():
    runner = CliRunner()
    result = runner.invoke(main, ["--list-templates"])
    assert result.exit_code == 0
    assert "modern" in result.output
    assert "minimal" in result.output


def test_missing_input():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0


def test_generate_pdf(tmp_path):
    md_content = """\
---
name: Test
title: Dev
email: test@test.com
---

## Perfil
Experienced.

## Habilidades
- Python
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content)
    out_file = tmp_path / "test.pdf"

    runner = CliRunner()
    result = runner.invoke(main, [str(md_file), "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert out_file.stat().st_size > 0


def test_generate_html(tmp_path):
    md_content = """\
---
name: Test
title: Dev
---

## Perfil
Hello world.
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content)
    out_file = tmp_path / "test.html"

    runner = CliRunner()
    result = runner.invoke(main, [str(md_file), "--html", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "Test" in content
    assert "Hello world" in content
