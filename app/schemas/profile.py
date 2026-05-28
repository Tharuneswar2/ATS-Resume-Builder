from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class BasicInfoLinks(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    shortlist_live: Optional[str] = None
    debugignore_docs: Optional[str] = None
    # Flexible field to support any other links
    other_links: Optional[Dict[str, str]] = Field(default_factory=dict)

class BasicInfo(BaseModel):
    name: str
    title: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    links: BasicInfoLinks

class ProfessionalSummary(BaseModel):
    experience_years: float
    core_identity: str
    domains: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    target_company_alignment: List[str] = Field(default_factory=list)

class Skills(BaseModel):
    programming: List[str] = Field(default_factory=list)
    ml_ai: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    distributed_systems: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    data_processing: List[str] = Field(default_factory=list)
    computer_vision: List[str] = Field(default_factory=list)
    cloud_devops: List[str] = Field(default_factory=list)
    developer_tooling: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    automation: List[str] = Field(default_factory=list)
    software_engineering: List[str] = Field(default_factory=list)
    # Flexible for adding extra skill sections
    extra_categories: Optional[Dict[str, List[str]]] = Field(default_factory=dict)

class ImpactItem(BaseModel):
    area: str
    achievement: str
    method: str

class Experience(BaseModel):
    company: str
    role: str
    type: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    impact: List[ImpactItem] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    faang_alignment: List[str] = Field(default_factory=list)

class OpenSourceProjectLinks(BaseModel):
    documentation: Optional[str] = None
    github: Optional[str] = None

class OpenSourceProject(BaseModel):
    name: str
    type: str
    links: OpenSourceProjectLinks
    highlights: List[str] = Field(default_factory=list)
    core_engineering_concepts: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    target_company_alignment: List[str] = Field(default_factory=list)

class Project(BaseModel):
    name: str
    category: List[str] = Field(default_factory=list)
    live_link: Optional[str] = None
    github_link: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    faang_alignment: List[str] = Field(default_factory=list)

class Education(BaseModel):
    degree: str
    institution: str
    status: Optional[str] = None
    duration: Optional[str] = None

class Certification(BaseModel):
    name: str
    provider: str

class AchievementBankItem(BaseModel):
    tags: List[str] = Field(default_factory=list)
    text: str

class Preferences(BaseModel):
    target_roles: List[str] = Field(default_factory=list)
    work_type: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    target_companies: List[str] = Field(default_factory=list)

class WritingStyle(BaseModel):
    tone: str
    style: str
    rules: List[str] = Field(default_factory=list)

class ProfileCreate(BaseModel):
    basic_info: BasicInfo
    professional_summary: ProfessionalSummary
    skills: Skills
    experience: List[Experience] = Field(default_factory=list)
    open_source_projects: List[OpenSourceProject] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    achievement_bank: List[AchievementBankItem] = Field(default_factory=list)
    preferences: Preferences
    writing_style: WritingStyle

class ProfileResponse(ProfileCreate):
    id: str = Field(alias="_id")

class ProfileUpdate(BaseModel):
    basic_info: Optional[BasicInfo] = None
    professional_summary: Optional[ProfessionalSummary] = None
    skills: Optional[Skills] = None
    experience: Optional[List[Experience]] = None
    open_source_projects: Optional[List[OpenSourceProject]] = None
    projects: Optional[List[Project]] = None
    education: Optional[List[Education]] = None
    certifications: Optional[List[Certification]] = None
    awards: Optional[List[str]] = None
    achievement_bank: Optional[List[AchievementBankItem]] = None
    preferences: Optional[Preferences] = None
    writing_style: Optional[WritingStyle] = None
