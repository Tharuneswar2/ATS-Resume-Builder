from fastapi import HTTPException

from app.generators.latex_engine import latex_engine
from app.repositories.profile_repository import profile_repo

DEFAULT_TEMPLATE = "00_ats_optimized.tex.j2"


class ResumeService:
    async def generate_pdf(self, profile_id: str, template_name: str = DEFAULT_TEMPLATE) -> bytes:
        """Fetch a profile and generate a PDF resume using the selected template."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        try:
            tex_content = await latex_engine.render_template(template_name, profile)
            return await latex_engine.compile_pdf(tex_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")


resume_service = ResumeService()
