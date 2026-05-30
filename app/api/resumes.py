"""
Resume generation endpoints — protected by authentication.

Verifies profile ownership before generating PDFs or scoring.
"""

from fastapi import APIRouter, Response

from app.core.dependencies import CurrentUser
from app.schemas.jd import JDUploadRequest
from app.services.jd_resume_service import jd_resume_service
from app.services.profile_service import profile_service
from app.services.resume_service import DEFAULT_TEMPLATE, resume_service
import re
from pathlib import Path

router = APIRouter()


@router.post("/generate/{profile_id}")
async def generate_resume_pdf(profile_id: str, user: CurrentUser, template: str = DEFAULT_TEMPLATE):
    """Generate and return a PDF resume for a profile (ownership verified)."""
    # Verify the current user owns this profile before generating
    await profile_service.get_profile(profile_id, user_id=user["_id"])
    pdf_bytes = await resume_service.generate_pdf(profile_id, template)
    name = re.sub(
        r"^\d+_",
        "",
        Path(template).name.replace(".tex.j2", "")
    ).replace("_", "-")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=resume_{name}.pdf"
        }
    )


@router.post("/generate-from-jd/{profile_id}")
async def generate_resume_pdf_from_jd(
    profile_id: str,
    request: JDUploadRequest,
    user: CurrentUser,
    template: str = DEFAULT_TEMPLATE,
):
    """Generate a PDF resume tailored to a job description (ownership verified)."""
    await profile_service.get_profile(profile_id, user_id=user["_id"])
    pdf_bytes = await jd_resume_service.generate_pdf_for_jd(profile_id, request.text, template)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=resume_{profile_id}_jd_tailored.pdf"
        },
    )


@router.get("/ats-score/{profile_id}")
async def get_resume_ats_score(profile_id: str, user: CurrentUser, template: str = DEFAULT_TEMPLATE):
    """Estimate ATS readiness (ownership verified)."""
    from app.services.ats_service import ats_service
    await profile_service.get_profile(profile_id, user_id=user["_id"])
    return await ats_service.score_profile(profile_id, template)
