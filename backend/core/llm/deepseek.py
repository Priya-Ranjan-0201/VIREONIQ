"""
DeepSeek LLM Provider — Ultra-low-cost API for global accessibility.

Uses the OpenAI-compatible chat completions endpoint at api.deepseek.com.
Ideal for free-tier students and high-volume usage patterns.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from openai import AsyncOpenAI
from core.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek V3/R1 provider via OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = "deepseek-chat") -> None:
        """
        Initialize the DeepSeek provider.

        Args:
            api_key: DeepSeek API key.
            model: Model identifier (deepseek-chat for V3, deepseek-reasoner for R1).
        """
        self.api_key = api_key
        self.client = AsyncOpenAI(
            base_url="https://api.deepseek.com",
            api_key=api_key if api_key else "mock_key",
        )
        self.model_name = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Send a chat completion request to DeepSeek.

        Args:
            messages: List of message dictionaries with role and content.
            system_prompt: Optional system instruction prepended to the conversation.

        Returns:
            The assistant's text response.
        """
        api_messages: List[Dict[str, str]] = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)

        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"DeepSeek API Error: {e}")
            raise

    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response from DeepSeek.

        Args:
            messages: List of message dictionaries.
            system_prompt: Optional system instruction.

        Returns:
            Parsed JSON dictionary.
        """
        json_system = (system_prompt or "") + (
            "\n\nIMPORTANT: You must output ONLY valid JSON. "
            "Do not include markdown code blocks or extra text."
        )
        response_text = await self.chat(messages, json_system)

        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from DeepSeek: {response_text}")
            raise ValueError(f"Invalid JSON returned from DeepSeek: {e}")
