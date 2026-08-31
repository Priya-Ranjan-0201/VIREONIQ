import logging
from core.llm.nvidia_nim import NvidiaNimProvider
from core.config import settings

logger = logging.getLogger(__name__)

class NVIDIA_NIM_Client:
    def __init__(self):
        # Initialize the underlying provider using settings configuration
        self.provider = NvidiaNimProvider(api_key=settings.NVIDIA_NIM_API_KEY or "")

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Sends a query to the NVIDIA NIM client and returns the raw string content.
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.provider.chat(messages, system_prompt)
