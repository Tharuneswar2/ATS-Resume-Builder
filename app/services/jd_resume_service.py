from copy import deepcopy
from typing import Any, Dict, Iterable

from fastapi import HTTPException

from app.generators.latex_engine import latex_engine
from app.repositories.profile_repository import profile_repo
from app.schemas.jd import JDAnalysis
from app.services.jd_service import jd_service
from app.services.resume_service import DEFAULT_TEMPLATE


class JDResumeService:
    async def generate_pdf_for_jd(
        self,
        profile_id: str,
        jd_text: str,
        template_name: str = DEFAULT_TEMPLATE,
    ) -> bytes:
        """Generate a resume PDF after tailoring the profile to a job description."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        jd_analysis = await jd_service.analyze_jd_with_fallback(jd_text)
        tailored_profile = self.tailor_profile(profile, jd_analysis)

        try:
            tex_content = await latex_engine.render_template(template_name, tailored_profile)
            return await latex_engine.compile_pdf(tex_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate JD-based resume: {str(e)}")

    def tailor_profile(self, profile: Dict[str, Any], jd: JDAnalysis) -> Dict[str, Any]:
        """Prioritize existing profile content according to JD keywords."""
        tailored = deepcopy(profile)
        keywords = self._keyword_set(
            [
                *jd.required_skills,
                *jd.preferred_skills,
                *jd.keywords,
                *jd.responsibilities,
                jd.role,
                jd.company or "",
            ]
        )

        self._tailor_summary(tailored, jd, keywords)
        self._prioritize_skill_sections(tailored, keywords)
        self._prioritize_experience(tailored, keywords)
        self._prioritize_projects(tailored, keywords)
        self._prioritize_open_source(tailored, keywords)

        return tailored

    def _tailor_summary(self, profile: Dict[str, Any], jd: JDAnalysis, keywords: set[str]) -> None:
        summary = profile.get("professional_summary", {})
        strengths = summary.get("key_strengths", [])
        summary["key_strengths"] = self._rank_strings(strengths, keywords)

        alignment = summary.get("target_company_alignment", [])
        jd_alignment = [
            value
            for value in [jd.role, jd.company, *jd.required_skills[:6], *jd.keywords[:6]]
            if value
        ]
        summary["target_company_alignment"] = self._dedupe(jd_alignment + alignment)

    def _prioritize_skill_sections(self, profile: Dict[str, Any], keywords: set[str]) -> None:
        skills = profile.get("skills", {})
        for section, values in skills.items():
            if isinstance(values, list):
                skills[section] = self._rank_strings(values, keywords)

    def _prioritize_experience(self, profile: Dict[str, Any], keywords: set[str]) -> None:
        for job in profile.get("experience", []):
            job["responsibilities"] = self._rank_strings(job.get("responsibilities", []), keywords)
            job["impact"] = self._rank_dicts(job.get("impact", []), keywords)
            job["tech_stack"] = self._rank_strings(job.get("tech_stack", []), keywords)
        profile["experience"] = self._rank_dicts(profile.get("experience", []), keywords)

    def _prioritize_projects(self, profile: Dict[str, Any], keywords: set[str]) -> None:
        for project in profile.get("projects", []):
            project["highlights"] = self._rank_strings(project.get("highlights", []), keywords)
            project["tech_stack"] = self._rank_strings(project.get("tech_stack", []), keywords)
            project["faang_alignment"] = self._rank_strings(project.get("faang_alignment", []), keywords)
        profile["projects"] = self._rank_dicts(profile.get("projects", []), keywords)

    def _prioritize_open_source(self, profile: Dict[str, Any], keywords: set[str]) -> None:
        for project in profile.get("open_source_projects", []):
            project["highlights"] = self._rank_strings(project.get("highlights", []), keywords)
            project["tech_stack"] = self._rank_strings(project.get("tech_stack", []), keywords)
            project["core_engineering_concepts"] = self._rank_strings(project.get("core_engineering_concepts", []), keywords)
        profile["open_source_projects"] = self._rank_dicts(profile.get("open_source_projects", []), keywords)

    def _rank_strings(self, values: list[str], keywords: set[str]) -> list[str]:
        return sorted(values, key=lambda value: (-self._match_score(value, keywords), values.index(value)))

    def _rank_dicts(self, values: list[Dict[str, Any]], keywords: set[str]) -> list[Dict[str, Any]]:
        return sorted(values, key=lambda value: (-self._match_score(str(value), keywords), values.index(value)))

    def _match_score(self, value: str, keywords: set[str]) -> int:
        normalized = value.lower()
        return sum(1 for keyword in keywords if keyword in normalized)

    def _keyword_set(self, values: Iterable[str]) -> set[str]:
        keywords = set()
        for value in values:
            for token in str(value).lower().replace("/", " ").replace("-", " ").split():
                cleaned = token.strip(".,:;()[]{}")
                if len(cleaned) >= 3:
                    keywords.add(cleaned)
            if value and len(str(value).strip()) >= 3:
                keywords.add(str(value).lower().strip())
        return keywords

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        result = []
        for value in values:
            key = str(value).lower()
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result


jd_resume_service = JDResumeService()
