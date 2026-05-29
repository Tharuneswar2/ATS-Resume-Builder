from fastapi import APIRouter, HTTPException

from app.schemas.jd import JDAnalysis, JDUploadRequest, JDScore
from app.services.jd_service import jd_service

router = APIRouter()


@router.post("/analyze", response_model=JDAnalysis)
async def analyze_jd(request: JDUploadRequest):
    """Analyze raw job description text and extract structured requirements."""
    try:
        return await jd_service.analyze_jd(request.text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze JD: {str(e)}")


@router.post("/score/{profile_id}", response_model=JDScore)
async def score_resume(profile_id: str, request: JDUploadRequest):
    """Score an existing profile against a job description."""
    try:
        jd_analysis = await jd_service.analyze_jd(request.text)
        return await jd_service.score_profile_against_jd(profile_id, jd_analysis)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
