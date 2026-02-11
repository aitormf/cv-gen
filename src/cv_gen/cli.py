"""CLI entry point for cv-gen."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

from cv_gen.parser import parse_cv_file
from cv_gen.renderer import get_available_templates, render_html, render_pdf


@click.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option("-t", "--template", default="modern", help="Template name (default: modern).")
@click.option("-o", "--output", default=None, help="Output file path.")
@click.option("--list-templates", is_flag=True, help="List available templates.")
@click.option("--preview", is_flag=True, help="Generate PDF and open it.")
@click.option("--html", is_flag=True, help="Export HTML instead of PDF (debug).")
def main(
    input_file: str | None,
    template: str,
    output: str | None,
    list_templates: bool,
    preview: bool,
    html: bool,
) -> None:
    """Generate a professional PDF CV from a Markdown file."""
    if list_templates:
        templates = get_available_templates()
        click.echo("Available templates:")
        for t in templates:
            marker = " (default)" if t == "modern" else ""
            click.echo(f"  - {t}{marker}")
        return

    if not input_file:
        raise click.UsageError("Missing argument 'INPUT_FILE'. Use --list-templates or provide a Markdown file.")

    cv = parse_cv_file(input_file)
    input_path = Path(input_file)

    if html:
        html_output = output or input_path.with_suffix(".html").name
        html_string = render_html(cv, template)
        Path(html_output).write_text(html_string, encoding="utf-8")
        click.echo(f"HTML exported: {html_output}")
        return

    pdf_output = output or input_path.with_suffix(".pdf").name
    render_pdf(cv, pdf_output, template)
    click.echo(f"PDF generated: {pdf_output}")

    if preview:
        _open_file(pdf_output)


def _open_file(path: str) -> None:
    """Open a file with the system default viewer."""
    if sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    elif sys.platform == "win32":
        subprocess.run(["start", path], shell=True, check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)
