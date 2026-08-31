"""
LLM Factory — Provider registry and instantiation.

Supports: Claude, Gemini, Nvidia NIM, DeepSeek, Ollama.
"""

from typing import Optional

from core.config import settings
from core.llm.base import BaseLLMProvider
from core.llm.claude import ClaudeProvider
from core.llm.gemini import GeminiProvider
from core.llm.nvidia_nim import NvidiaNimProvider
from core.llm.deepseek import DeepSeekProvider
from core.llm.ollama import OllamaProvider
from core.llm.fallback import FallbackLLMProvider


def get_llm_provider(provider_override: Optional[str] = None) -> BaseLLMProvider:
    """
    Instantiate and return the appropriate LLM provider.

    Args:
        provider_override: If set, overrides settings.DEFAULT_LLM_PROVIDER.
            This allows per-request provider selection (e.g. user picks DeepSeek
            for cost savings or Ollama for offline mode).

    Returns:
        An instance of BaseLLMProvider.

    Raises:
        ValueError: If the requested provider is unknown.
    """
    provider_name = provider_override or settings.DEFAULT_LLM_PROVIDER
    primary: BaseLLMProvider

    if provider_name == "claude":
        primary = ClaudeProvider(
            api_key=settings.ANTHROPIC_API_KEY or "mock_key"
        )

    elif provider_name == "gemini":
        primary = GeminiProvider(
            api_key=settings.GEMINI_API_KEY or ""
        )

    elif provider_name == "nvidia_nim":
        primary = NvidiaNimProvider(
            api_key=settings.NVIDIA_NIM_API_KEY or ""
        )

    elif provider_name == "deepseek":
        primary = DeepSeekProvider(
            api_key=settings.DEEPSEEK_API_KEY or "",
            model=settings.DEEPSEEK_MODEL,
        )

    elif provider_name == "ollama":
        primary = OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider_name}'. "
            f"Supported: claude, gemini, nvidia_nim, deepseek, ollama"
        )

    return FallbackLLMProvider(primary)

