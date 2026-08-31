"""
LLM Orchestrator — Async-first interface to the multi-provider LLM factory.

Exposes:
  - acall_llm()  → awaitable coroutine for use inside async FastAPI handlers
  - call_llm()   → synchronous wrapper for Celery workers and startup scripts
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List

from core.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Async-first interface (preferred in services)
# ──────────────────────────────────────────────

async def acall_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider_override: Optional[str] = None,
) -> str:
    """
    Asynchronously query the LLM provider with a prompt.

    This is the preferred entry point for all async FastAPI service methods.
    It does NOT block the event loop.

    Args:
        prompt: The user-facing prompt text.
        system_prompt: Optional system-level instruction prepended to the conversation.
        provider_override: Optional provider name to override the default (e.g. 'deepseek', 'ollama').

    Returns:
        The LLM's text response.
    """
    try:
        provider = get_llm_provider(provider_override)
        messages: List[Dict[str, str]] = [{"role": "user", "content": prompt}]
        return await provider.chat(messages, system_prompt)
    except Exception as e:
        logger.error(f"Error in acall_llm: {e}")
        raise


async def acall_llm_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Asynchronously query the LLM and parse a structured JSON response.

    Args:
        prompt: The user-facing prompt text.
        system_prompt: Optional system-level instruction.
        provider_override: Optional provider name override.

    Returns:
        Parsed JSON dictionary from the LLM response.
    """
    try:
        provider = get_llm_provider(provider_override)
        messages: List[Dict[str, str]] = [{"role": "user", "content": prompt}]
        return await provider.generate_json(messages, system_prompt)
    except Exception as e:
        logger.error(f"Error in acall_llm_json: {e}")
        raise


# ──────────────────────────────────────────────
# Synchronous wrapper (for Celery workers only)
# ──────────────────────────────────────────────

def _run_async(coro):
    """
    Helper to run an async coroutine synchronously.
    If there is already a running event loop in the current thread, it spawns a new thread
    with a new event loop to execute the coroutine and block until completion, preventing RuntimeError.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        result = []
        exception = []

        def target():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                res = new_loop.run_until_complete(coro)
                result.append(res)
            except Exception as e:
                exception.append(e)
            finally:
                new_loop.close()

        thread = threading.Thread(target=target)
        thread.start()
        thread.join()

        if exception:
            raise exception[0]
        return result[0]
    else:
        return asyncio.run(coro)


def call_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Synchronously query the default LLM provider with a prompt.

    WARNING: This blocks the calling thread. Use acall_llm() inside async contexts.
    This wrapper exists solely for Celery task compatibility.
    """
    try:
        provider = get_llm_provider()
        messages = [{"role": "user", "content": prompt}]
        return _run_async(provider.chat(messages, system_prompt))
    except Exception as e:
        logger.error(f"Error in call_llm: {e}")
        raise e
