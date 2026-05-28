import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
LATEX_COMMAND = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "resume.tex"]
PDF_BUILD_PASSES = 2

# Custom Jinja2 environment to avoid conflicts with LaTeX braces {}
# We use:
# Block start/end: \BLOCK{ }
# Variable start/end: \VAR{ }
# Comment start/end: \#{ }
latex_jinja_env = Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=FileSystemLoader(str(TEMPLATE_DIR))
)


def escape_latex(text: str) -> str:
    """Escape characters that are special in LaTeX text nodes."""
    if not isinstance(text, str):
        return text

    # Must replace backslash first to avoid double escaping
    text = text.replace('\\', r'\textbackslash{}')

    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)
    return text


def visible_url(url: str) -> str:
    """Escape URL characters that commonly break LaTeX while keeping links readable."""
    if not isinstance(url, str):
        return url
    return url.replace('\\', r'\textbackslash{}').replace('%', r'\%').replace('#', r'\#')


latex_jinja_env.filters['escape_latex'] = escape_latex
latex_jinja_env.filters['visible_url'] = visible_url


class LatexEngine:
    def build_pdf_metadata(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Build metadata injected into generated PDFs through hyperref."""
        basic_info = context.get("basic_info", {})
        summary = context.get("professional_summary", {})
        skills = context.get("skills", {})
        preferences = context.get("preferences", {})

        keyword_groups = [
            summary.get("domains", []),
            summary.get("key_strengths", []),
            skills.get("programming", []),
            skills.get("ml_ai", []),
            skills.get("backend", []),
            skills.get("distributed_systems", []),
            skills.get("developer_tooling", []),
            preferences.get("target_roles", []),
        ]
        keywords = []
        for group in keyword_groups:
            keywords.extend(group or [])

        return {
            "author": basic_info.get("name", "Resume"),
            "title": f"{basic_info.get('name', 'Resume')} - {basic_info.get('title', 'Resume')}",
            "subject": summary.get("core_identity", "Professional resume"),
            "keywords": ", ".join(dict.fromkeys(keywords)),
            "creator": "AI Resume Generator",
        }

    def get_available_templates(self) -> list[str]:
        """Return renderable LaTeX templates known to the Jinja loader."""
        return sorted(
            template_name
            for template_name in latex_jinja_env.list_templates()
            if template_name.endswith(".tex.j2")
        )

    async def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 LaTeX template with the given profile context."""
        available_templates = self.get_available_templates()
        if template_name not in available_templates:
            raise ValueError(
                "Invalid template name. "
                f"Available templates: {', '.join(available_templates)}"
            )
        render_context = {
            **context,
            "resume_metadata": self.build_pdf_metadata(context),
        }
        template = latex_jinja_env.get_template(template_name)
        return template.render(**render_context)

    async def compile_pdf(self, tex_content: str) -> bytes:
        """Compile a LaTeX document string to PDF bytes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file_path = Path(temp_dir) / "resume.tex"
            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            for _ in range(PDF_BUILD_PASSES):
                process = subprocess.run(
                    LATEX_COMMAND,
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if process.returncode != 0:
                    output = "\n".join(part for part in [process.stdout, process.stderr] if part)
                    raise RuntimeError(f"LaTeX compilation failed:\n{output.strip()}")

            pdf_file_path = Path(temp_dir) / "resume.pdf"
            if not pdf_file_path.exists():
                raise RuntimeError("PDF was not generated.")

            with open(pdf_file_path, "rb") as pdf_file:
                return pdf_file.read()


latex_engine = LatexEngine()
