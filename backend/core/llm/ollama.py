"""
Ollama Local LLM Provider — Zero-cost, offline-first AI inference.

Connects to a locally running Ollama server (default: http://localhost:11434).
Enables students with no API budget to run the full platform using open-source
models like Llama 3, Mistral, or Phi on their own hardware.
"""

import json
import logging
from typing import List, Dict, Any, Optional

import httpx
from core.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama local inference provider for offline/free-tier usage."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ) -> None:
        """
        Initialize the Ollama provider.

        Args:
            base_url: URL of the running Ollama server.
            model: Model name to use (e.g. llama3, mistral, phi3).
        """
        self.base_url = base_url.rstrip("/")
        self.model_name = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Send a chat request to the local Ollama server.

        Args:
            messages: List of message dictionaries with role and content.
            system_prompt: Optional system instruction.

        Returns:
            The assistant's text response.
        """
        api_messages: List[Dict[str, str]] = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)

        payload = {
            "model": self.model_name,
            "messages": api_messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out — is Ollama running locally?")
            raise ConnectionError(
                "Ollama server timed out. Make sure Ollama is running: `ollama serve`"
            )
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Install Ollama from https://ollama.com and run `ollama serve`."
            )
        except Exception as e:
            logger.error(f"Ollama API Error: {e}")
            raise

    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response from Ollama.

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
            logger.error(f"Failed to parse JSON from Ollama: {response_text}")
            raise ValueError(f"Invalid JSON returned from Ollama: {e}")
