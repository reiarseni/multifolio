import asyncio
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.services.public import get_published_facet

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

VALID_PDF_LAYOUTS = {"classic", "two-column", "compact"}


def _build_theme_css(tokens: dict) -> str:
    color = tokens.get("color", {})
    typography = tokens.get("typography", {})
    spacing = tokens.get("spacing", {})
    shape = tokens.get("shape", {})
    lines = [":root {"]
    if color.get("primary"):
        lines.append(f"  --color-primary: {color['primary']};")
    if color.get("background"):
        lines.append(f"  --color-background: {color['background']};")
    if color.get("surface"):
        lines.append(f"  --color-surface: {color['surface']};")
    if color.get("text_heading"):
        lines.append(f"  --color-text-heading: {color['text_heading']};")
    if color.get("text_body"):
        lines.append(f"  --color-text-body: {color['text_body']};")
    if color.get("text_muted"):
        lines.append(f"  --color-text-muted: {color['text_muted']};")
    if color.get("border"):
        lines.append(f"  --color-border: {color['border']};")
    if color.get("accent"):
        lines.append(f"  --color-accent: {color['accent']};")
    if typography.get("font_heading"):
        lines.append(f"  --font-heading: {typography['font_heading']};")
    if typography.get("font_body"):
        lines.append(f"  --font-body: {typography['font_body']};")
    if typography.get("size_base"):
        lines.append(f"  --size-base: {typography['size_base']};")
    if spacing.get("section_gap"):
        lines.append(f"  --spacing-section-gap: {spacing['section_gap']};")
    if spacing.get("item_gap"):
        lines.append(f"  --spacing-item-gap: {spacing['item_gap']};")
    if shape.get("radius_md"):
        lines.append(f"  --radius-md: {shape['radius_md']};")
    lines.append("}")
    return "\n".join(lines)


async def generate_facet_pdf(db, slug: str) -> bytes:
    data = await get_published_facet(db, slug)
    pdf_layout = data.get("pdf_layout", "classic")
    if pdf_layout not in VALID_PDF_LAYOUTS:
        pdf_layout = "classic"
    theme_css = _build_theme_css(data.get("theme_tokens") or {})
    template = env.get_template(f"{pdf_layout}.html")
    html_str = template.render(**data, theme_css=theme_css)
    pdf_bytes = await asyncio.to_thread(lambda: HTML(string=html_str).write_pdf())
    return pdf_bytes
