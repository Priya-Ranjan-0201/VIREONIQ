import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from core.llm.base import BaseLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = settings.CLAUDE_MODEL

    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        try:
            # Convert messages to Anthropic format if necessary
            # Anthropic messages are usually {"role": "user", "content": "..."}
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API Error: {str(e)}")
            raise

    async def generate_json(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # Append instruction for JSON
        json_system_prompt = (system_prompt or "") + "\nRespond ONLY with a valid JSON object."
        
        raw_response = await self.chat(messages, system_prompt=json_system_prompt)
        try:
            # Simple cleanup for potential markdown blocks
            clean_response = raw_response.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude: {raw_response}")
            raise ValueError("LLM returned invalid JSON")
