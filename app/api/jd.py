"""
Job Description analysis and scoring endpoints — protected by authentication.
"""

from fastapi import APIRouter, HTTPException

from app.core.dependencies import CurrentUser
from app.schemas.jd import JDAnalysis, JDUploadRequest, JDScore
from app.services.jd_service import jd_service
from app.services.profile_service import profile_service

router = APIRouter()


@router.post("/analyze", response_model=JDAnalysis)
async def analyze_jd(request: JDUploadRequest, user: CurrentUser):
    """Analyze raw job description text and extract structured requirements."""
    try:
        return await jd_service.analyze_jd(request.text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze JD: {str(e)}")


@router.post("/score/{profile_id}", response_model=JDScore)
async def score_resume(profile_id: str, request: JDUploadRequest, user: CurrentUser):
    """Score an existing profile against a job description (ownership verified)."""
    try:
        # Verify ownership before scoring
        await profile_service.get_profile(profile_id, user_id=user["_id"])
        jd_analysis = await jd_service.analyze_jd(request.text)
        return await jd_service.score_profile_against_jd(profile_id, jd_analysis)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
