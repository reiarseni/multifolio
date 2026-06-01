from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.services.public import get_published_facet

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


async def generate_facet_pdf(db, slug: str) -> bytes:
    data = await get_published_facet(db, slug)
    template_name = data.get("pdf_template", "moderna")
    if template_name not in ("moderna", "clasica"):
        template_name = "moderna"
    template = env.get_template(f"{template_name}.html")
    html_str = template.render(**data)
    pdf_bytes = HTML(string=html_str).write_pdf()
    return pdf_bytes
