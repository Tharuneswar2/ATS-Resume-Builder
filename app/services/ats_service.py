from typing import Any, Dict, List

from fastapi import HTTPException

from app.generators.latex_engine import latex_engine
from app.repositories.profile_repository import profile_repo


ATS_TARGET_MIN = 80
ATS_TARGET_MAX = 95
ATS_STARTING_SCORE = 95

ProfileDocument = Dict[str, Any]
ATSCheck = Dict[str, Any]

RISKY_LAYOUT_TOKENS = {
    "tables": ["\\begin{tabular", "\\begin{tabularx"],
    "multi_column": ["\\begin{paracol", "\\begin{multicols"],
    "framed_boxes": ["\\begin{tcolorbox", "\\begin{mdframed", "\\colorbox"],
    "minipages": ["\\begin{minipage"],
    "icons": ["\\faIcon"],
}

REQUIRED_HEADINGS = [
    "Professional Summary",
    "Skills",
    "Work Experience",
    "Projects",
    "Education",
]


class ATSService:
    async def score_profile(self, profile_id: str, template_name: str) -> Dict[str, Any]:
        """Render a profile/template pair and return its ATS readiness score."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        try:
            tex_content = await latex_engine.render_template(template_name, profile)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return self.score_rendered_resume(profile, template_name, tex_content)

    def score_rendered_resume(
        self,
        profile: ProfileDocument,
        template_name: str,
        tex_content: str,
    ) -> Dict[str, Any]:
        """Score rendered LaTeX against ATS-friendly structure and content checks."""
        checks: List[ATSCheck] = []
        score = ATS_STARTING_SCORE

        def add_check(name: str, passed: bool, penalty: int = 0, message: str = "") -> None:
            nonlocal score
            if not passed:
                score -= penalty
            checks.append(
                {
                    "name": name,
                    "passed": passed,
                    "penalty": 0 if passed else penalty,
                    "message": message,
                }
            )

        for name, tokens in RISKY_LAYOUT_TOKENS.items():
            found = any(token in tex_content for token in tokens)
            add_check(
                name=f"Avoid {name.replace('_', ' ')}",
                passed=not found,
                penalty=8 if name in {"tables", "multi_column"} else 4,
                message="ATS parsers prefer single-column text flow without layout objects.",
            )

        for heading in REQUIRED_HEADINGS:
            add_check(
                name=f"Has {heading}",
                passed=heading.lower() in tex_content.lower(),
                penalty=5,
                message=f"Use a standard '{heading}' section heading.",
            )

        basic_info = profile.get("basic_info", {})
        links = basic_info.get("links", {})
        contact_complete = bool(basic_info.get("email") and basic_info.get("phone") and links.get("linkedin"))
        add_check(
            name="Complete contact information",
            passed=contact_complete,
            penalty=6,
            message="Email, phone, and LinkedIn should be present as selectable text.",
        )

        visible_links = all(
            not link or link in tex_content
            for link in [links.get("linkedin"), links.get("portfolio"), links.get("github")]
        )
        add_check(
            name="Visible profile links",
            passed=visible_links,
            penalty=5,
            message="ATS-safe resumes should expose URL text, not only hidden labels.",
        )

        skills = profile.get("skills", {})
        flattened_skills = [
            item
            for values in skills.values()
            if isinstance(values, list)
            for item in values
        ]
        add_check(
            name="Keyword-rich skills",
            passed=len(set(flattened_skills)) >= 30,
            penalty=8,
            message="Include a broad, explicit skills section with role keywords.",
        )

        experience = profile.get("experience", [])
        responsibility_count = sum(len(job.get("responsibilities", [])) for job in experience)
        impact_count = sum(len(job.get("impact", [])) for job in experience)
        add_check(
            name="Enough experience bullets",
            passed=responsibility_count + impact_count >= 8,
            penalty=8,
            message="Use enough bullet points for ATS keyword matching.",
        )
        add_check(
            name="Quantified impact",
            passed=self._has_quantified_impact(profile),
            penalty=6,
            message="Include metrics such as percentages, scale, latency, users, or throughput.",
        )

        has_open_source = bool(profile.get("open_source_projects"))
        add_check(
            name="Open source / portfolio evidence",
            passed=has_open_source,
            penalty=4,
            message="Open-source and portfolio projects improve technical evidence density.",
        )

        metadata_present = all(
            token in tex_content
            for token in ["pdfauthor", "pdftitle", "pdfsubject", "pdfkeywords"]
        )
        add_check(
            name="PDF metadata",
            passed=metadata_present,
            penalty=5,
            message="Generated PDFs should include author, title, subject, and keyword metadata.",
        )

        score = max(0, min(ATS_TARGET_MAX, score))
        return {
            "template": template_name,
            "score": score,
            "minimum_target": ATS_TARGET_MIN,
            "maximum_target": ATS_TARGET_MAX,
            "target_range": f"{ATS_TARGET_MIN}-{ATS_TARGET_MAX}",
            "status": "pass" if score >= ATS_TARGET_MIN else "needs_improvement",
            "recommendation": (
                "Use the ATS optimized template for job applications."
                if score >= ATS_TARGET_MIN
                else "Switch to 00_ats_optimized.tex.j2 or simplify the selected template."
            ),
            "checks": checks,
        }

    def _has_quantified_impact(self, profile: ProfileDocument) -> bool:
        searchable_text = " ".join(
            [
                str(profile.get("experience", "")),
                str(profile.get("projects", "")),
                str(profile.get("achievement_bank", "")),
            ]
        )
        return any(char.isdigit() for char in searchable_text) or "%" in searchable_text


ats_service = ATSService()
