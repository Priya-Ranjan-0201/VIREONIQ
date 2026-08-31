import logging
from typing import List, Dict, Any, Optional
from core.llm.base import BaseLLMProvider
from core.llm.mock import MockLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)

class FallbackLLMProvider(BaseLLMProvider):
    def __init__(self, primary_provider: BaseLLMProvider):
        self.primary_provider = primary_provider
        self.mock_provider = MockLLMProvider()

    def _is_unconfigured(self) -> bool:
        if hasattr(self.primary_provider, "api_key"):
            key = getattr(self.primary_provider, "api_key")
            if not key or "REPLACE_ME" in key or key == "mock_key":
                return True
        return False

    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        if settings.ENVIRONMENT == "production":
            if self._is_unconfigured():
                logger.error("Production AI Error: Primary LLM API key is unconfigured.")
                raise RuntimeError("AI_ANALYSIS_UNAVAILABLE: Primary LLM is not configured in production environment.")
            try:
                return await self.primary_provider.chat(messages, system_prompt)
            except Exception as e:
                logger.error(f"Production AI Error: Primary LLM Provider failed: {e}")
                raise RuntimeError(f"AI_ANALYSIS_UNAVAILABLE: External AI provider error: {str(e)}")

        if self._is_unconfigured():
            logger.warning("Primary LLM Provider API key is unconfigured. Falling back to MockLLMProvider in development mode.")
            return await self.mock_provider.chat(messages, system_prompt)

        try:
            return await self.primary_provider.chat(messages, system_prompt)
        except Exception as e:
            logger.error(f"Primary LLM Provider failed: {e}. Falling back to MockLLMProvider in development mode.")
            return await self.mock_provider.chat(messages, system_prompt)

    async def generate_json(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if settings.ENVIRONMENT == "production":
            if self._is_unconfigured():
                logger.error("Production AI Error: Primary LLM API key is unconfigured.")
                return {"status": "AI_ANALYSIS_UNAVAILABLE", "message": "AI analysis is unconfigured in production environment.", "uncertainty_tier": "INSUFFICIENT_EVIDENCE"}
            try:
                return await self.primary_provider.generate_json(messages, system_prompt)
            except Exception as e:
                logger.error(f"Production AI Error: Primary LLM Provider failed: {e}")
                return {"status": "AI_ANALYSIS_UNAVAILABLE", "message": f"External AI provider failed: {str(e)}", "uncertainty_tier": "INSUFFICIENT_EVIDENCE"}

        if self._is_unconfigured():
            logger.warning("Primary LLM Provider API key is unconfigured. Falling back to MockLLMProvider in development mode.")
            return await self.mock_provider.generate_json(messages, system_prompt)

        try:
            return await self.primary_provider.generate_json(messages, system_prompt)
        except Exception as e:
            logger.error(f"Primary LLM Provider failed: {e}. Falling back to MockLLMProvider in development mode.")
            return await self.mock_provider.generate_json(messages, system_prompt)
