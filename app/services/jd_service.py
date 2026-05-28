import re

from app.ai.rewriter import ai_assistant
from app.repositories.profile_repository import profile_repo
from app.schemas.jd import JDAnalysis, JDScore

TECH_KEYWORDS = [
    "python",
    "javascript",
    "java",
    "fastapi",
    "node.js",
    "node",
    "express",
    "angular",
    "react",
    "mongodb",
    "sql",
    "qdrant",
    "kafka",
    "mqtt",
    "websockets",
    "docker",
    "docker compose",
    "kubernetes",
    "aws",
    "nginx",
    "linux",
    "github actions",
    "ci/cd",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "transformers",
    "llm",
    "rag",
    "embeddings",
    "semantic search",
    "vector search",
    "machine learning",
    "deep learning",
    "computer vision",
    "opencv",
    "ocr",
    "microservices",
    "distributed systems",
    "event-driven",
    "async",
    "api",
    "rest",
]

STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "have",
    "with",
    "this",
    "that",
    "will",
    "your",
    "you",
    "our",
    "the",
    "a",
    "an",
    "to",
    "of",
    "in",
    "on",
    "as",
    "by",
    "or",
    "is",
}


class JDService:
    async def analyze_jd(self, text: str) -> JDAnalysis:
        """Use the configured LLM to parse JD text into structured data."""
        return await ai_assistant.extract_jd_details(text)

    async def analyze_jd_with_fallback(self, text: str) -> JDAnalysis:
        """Analyze a JD with the LLM, falling back to local keyword extraction."""
        try:
            return await self.analyze_jd(text)
        except Exception:
            return self.analyze_jd_locally(text)

    def analyze_jd_locally(self, text: str) -> JDAnalysis:
        """Extract practical JD signals locally when the LLM is unavailable."""
        normalized = text.lower()
        found_skills = [
            keyword
            for keyword in TECH_KEYWORDS
            if re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", normalized)
        ]

        frequent_terms = self._extract_frequent_terms(text)
        keywords = self._dedupe(found_skills + frequent_terms)
        responsibilities = self._extract_responsibility_lines(text)

        return JDAnalysis(
            role=self._extract_role(text),
            required_skills=found_skills,
            preferred_skills=[],
            keywords=keywords,
            responsibilities=responsibilities,
        )

    async def score_profile_against_jd(self, profile_id: str, jd: JDAnalysis) -> JDScore:
        """Score a profile against extracted JD keywords."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile_str = str(profile).lower()
        matched = [kw for kw in jd.keywords if kw.lower() in profile_str]
        missing = [kw for kw in jd.keywords if kw.lower() not in profile_str]

        overall = len(matched) / max(len(jd.keywords), 1) * 100

        return JDScore(
            overall_match=round(overall, 2),
            matched_keywords=matched,
            missing_keywords=missing,
        )

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        result = []
        for value in values:
            cleaned = value.strip()
            key = cleaned.lower()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

    def _extract_frequent_terms(self, text: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9.+#/-]{2,}", text)
        counts: dict[str, int] = {}
        original: dict[str, str] = {}
        for word in words:
            key = word.lower().strip("-/")
            if key in STOPWORDS or len(key) < 3:
                continue
            counts[key] = counts.get(key, 0) + 1
            original.setdefault(key, word)

        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [original[key] for key, count in ranked[:20] if count > 1]

    def _extract_responsibility_lines(self, text: str) -> list[str]:
        lines = [line.strip(" -•\t") for line in text.splitlines()]
        useful_lines = [
            line
            for line in lines
            if len(line.split()) >= 5
            and any(verb in line.lower() for verb in ["build", "design", "develop", "manage", "implement", "deploy", "optimize"])
        ]
        return useful_lines[:8]

    def _extract_role(self, text: str) -> str:
        for line in text.splitlines():
            cleaned = line.strip(" -|\t")
            if 2 <= len(cleaned.split()) <= 8 and any(term in cleaned.lower() for term in ["engineer", "developer", "scientist", "architect"]):
                return cleaned
        return "Target Role"


jd_service = JDService()
