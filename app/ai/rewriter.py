import asyncio
from typing import List

import requests

from app.ai.prompts import JD_EXTRACTION_PROMPT, BULLET_REWRITE_PROMPT
from app.core.config import settings
from app.schemas.jd import JDAnalysis

INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


class AIAssistant:
    def _call_nvidia_api(self, prompt: str) -> str:
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set")

        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Accept": "application/json",
        }

        payload = {
            "model": "qwen/qwen3.5-397b-a17b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 16384,
            "temperature": 0.60,
            "top_p": 0.95,
            "top_k": 20,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": True},
        }

        response = requests.post(INVOKE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def extract_jd_details(self, jd_text: str) -> JDAnalysis:
        """Extract structured JD details through the configured NVIDIA model."""
        prompt = JD_EXTRACTION_PROMPT.format(jd_text=jd_text)
        result_str = await asyncio.to_thread(self._call_nvidia_api, prompt)

        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].strip()

        return JDAnalysis.model_validate_json(result_str)

    async def rewrite_bullet(self, bullet: str, keywords: List[str]) -> str:
        """Rewrite a resume bullet against target JD keywords."""
        prompt = BULLET_REWRITE_PROMPT.format(bullet=bullet, keywords=", ".join(keywords))
        result_str = await asyncio.to_thread(self._call_nvidia_api, prompt)
        return result_str.strip()


ai_assistant = AIAssistant()
