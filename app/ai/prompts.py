JD_EXTRACTION_PROMPT = """
You are an expert technical recruiter and AI Job Description parser.
Extract the following information from the provided Job Description text and output ONLY valid JSON matching the schema below.

Job Description Text:
{jd_text}

JSON Schema:
{{
  "role": "Extracted Job Title",
  "company": "Company Name",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "keywords": ["distributed systems", "scalable", "agile"],
  "years_of_experience": 3,
  "responsibilities": ["resp1", "resp2"]
}}
"""

BULLET_REWRITE_PROMPT = """
You are an expert FAANG-level resume writer. 
Rewrite the following resume bullet point to make it more impactful, metric-driven, and aligned with the provided Job Description keywords.
Maintain technical accuracy. Make it concise and punchy.

Original Bullet: {bullet}
Target Keywords: {keywords}

Output ONLY the rewritten bullet string, nothing else.
"""
