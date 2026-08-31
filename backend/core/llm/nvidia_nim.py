import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from core.llm.base import BaseLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)

class NvidiaNimProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key if api_key and api_key != "nvapi-REPLACE_ME" else "mock_key"
        )
        self.model_name = settings.NVIDIA_MODEL

    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)
        
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"NVIDIA NIM API Error: {e}")
            raise e

    async def generate_json(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if system_prompt:
            system_prompt += "\n\nIMPORTANT: You must output ONLY valid JSON format. Do not include markdown code blocks or any extra text."
        
        response_text = await self.chat(messages, system_prompt)
        
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from NVIDIA NIM: {response_text}")
            raise ValueError(f"Invalid JSON returned from LLM: {e}")
