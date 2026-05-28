from fastapi import APIRouter, Response

from app.services.ats_service import ats_service
from app.schemas.jd import JDUploadRequest
from app.services.jd_resume_service import jd_resume_service
from app.services.resume_service import DEFAULT_TEMPLATE, resume_service

router = APIRouter()


@router.post("/generate/{profile_id}")
async def generate_resume_pdf(profile_id: str, template: str = DEFAULT_TEMPLATE):
    """Generate and return a PDF resume for a profile."""
    pdf_bytes = await resume_service.generate_pdf(profile_id, template)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=resume_{profile_id}.pdf"
        }
    )


@router.post("/generate-from-jd/{profile_id}")
async def generate_resume_pdf_from_jd(
    profile_id: str,
    request: JDUploadRequest,
    template: str = DEFAULT_TEMPLATE,
):
    """Generate a PDF resume tailored to a job description."""
    pdf_bytes = await jd_resume_service.generate_pdf_for_jd(profile_id, request.text, template)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=resume_{profile_id}_jd_tailored.pdf"
        },
    )


@router.get("/ats-score/{profile_id}")
async def get_resume_ats_score(profile_id: str, template: str = DEFAULT_TEMPLATE):
    """Estimate ATS readiness before generating or submitting a resume."""
    return await ats_service.score_profile(profile_id, template)
