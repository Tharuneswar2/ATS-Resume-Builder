from pydantic import BaseModel, Field
from typing import List, Optional

class JDAnalysis(BaseModel):
    role: str
    company: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    years_of_experience: Optional[int] = None
    responsibilities: List[str] = Field(default_factory=list)
    
class JDUploadRequest(BaseModel):
    text: str

class JDScore(BaseModel):
    overall_match: float
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
