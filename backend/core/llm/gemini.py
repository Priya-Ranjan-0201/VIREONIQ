import json
import logging
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types as genai_types
    _NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai  # type: ignore[no-redef]
        genai_types = None
        _NEW_SDK = False
    except ImportError:
        genai = None
        genai_types = None
        _NEW_SDK = False

from core.llm.base import BaseLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """LLM provider implementation for Google Gemini models."""

    def __init__(self, api_key: str, model_name: Optional[str] = None) -> None:
        """Initialise the Gemini provider.

        Args:
            api_key: Google AI Studio API key.
            model_name: Optional Gemini model name override (defaulting to config).
        """
        self.api_key = api_key
        self.model_name = model_name or getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

        if self.api_key and self.api_key not in ("", "AIzaSy-REPLACE_ME"):
            if _NEW_SDK:
                self._client = genai.Client(api_key=self.api_key)
            else:
                genai.configure(api_key=self.api_key)  # type: ignore[union-attr]
        else:
            self._client = None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send a chat completion request to Gemini.

        Args:
            messages: Conversation history in OpenAI-style format.
            system_prompt: Optional system instruction string.

        Returns:
            The model's text response.
        """
        if _NEW_SDK and self._client:
            contents: List[genai_types.Content] = []
            for msg in messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append(
                    genai_types.Content(
                        role=role,
                        parts=[genai_types.Part.from_text(text=msg["content"])],
                    )
                )
            config = genai_types.GenerateContentConfig(
                system_instruction=system_prompt or "",
            )
            try:
                response = await self._client.aio.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                )
                return response.text or ""
            except Exception as exc:
                logger.error("Gemini API error: %s", exc)
                raise
        else:
            # Legacy SDK fallback
            formatted = []
            for msg in messages:
                role = "model" if msg["role"] == "assistant" else "user"
                formatted.append({"role": role, "parts": [msg["content"]]})
            model = (
                genai.GenerativeModel(self.model_name, system_instruction=system_prompt)  # type: ignore[union-attr]
                if system_prompt
                else genai.GenerativeModel(self.model_name)  # type: ignore[union-attr]
            )
            try:
                response = await model.generate_content_async(formatted)
                return response.text
            except Exception as exc:
                logger.error("Gemini API error (legacy SDK): %s", exc)
                raise

    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Request a JSON-structured response from Gemini.

        Args:
            messages: Conversation history.
            system_prompt: Optional system instruction.

        Returns:
            Parsed JSON dictionary from the model response.

        Raises:
            ValueError: If the model does not return valid JSON.
        """
        if system_prompt:
            system_prompt += (
                "\n\nIMPORTANT: You must output ONLY valid JSON. "
                "Do not include markdown code blocks or any extra text."
            )

        response_text = await self.chat(messages, system_prompt)

        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as exc:
            import re
            json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group(1).strip())
                except Exception:
                    pass
            logger.error("Failed to parse JSON from Gemini: %s", response_text)
            raise ValueError(f"Invalid JSON returned from LLM: {exc}") from exc
