import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from core.llm.base import BaseLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model or getattr(settings, "CLAUDE_MODEL", "claude-3-7-sonnet-20250219")

    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        try:
            # Filter and format messages for Anthropic
            anthropic_messages = []
            for msg in messages:
                role = "assistant" if msg.get("role") == "assistant" else "user"
                anthropic_messages.append({"role": role, "content": msg.get("content", "")})

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt if system_prompt else "",
                messages=anthropic_messages
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            logger.error(f"Claude API Error: {str(e)}")
            raise

    async def generate_json(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        json_system_prompt = (system_prompt or "") + "\n\nIMPORTANT: You must respond ONLY with a valid JSON object. No other text."
        raw_response = await self.chat(messages, system_prompt=json_system_prompt)
        try:
            clean_response = raw_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            return json.loads(clean_response.strip())
        except json.JSONDecodeError as e:
            import re
            json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', raw_response)
            if json_match:
                try:
                    return json.loads(json_match.group(1).strip())
                except Exception:
                    pass
            logger.error(f"Failed to parse JSON from Claude: {raw_response}")
            raise ValueError(f"LLM returned invalid JSON: {e}") from e
