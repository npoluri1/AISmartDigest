"""LLM client abstraction — works with Ollama (default) or OpenAI-compatible APIs."""

import json
import logging
from typing import Optional, AsyncGenerator
import httpx
from src.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.base_url = settings.llm_api_base.rstrip("/")
        self.api_key = settings.llm_api_key
        self.timeout = settings.llm_timeout

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.provider == "ollama":
            return await self._call_ollama(prompt, system_prompt)
        return await self._call_openai(prompt, system_prompt)

    async def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.llm_temperature,
                "num_predict": settings.llm_max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    def extract_json(self, text: str) -> dict:
        text = text.strip()
        for marker in ["```json", "```JSON", "```"]:
            if marker in text:
                text = text.split(marker, 1)[-1]
        if "```" in text:
            text = text.split("```", 1)[0]
        return json.loads(text.strip())
