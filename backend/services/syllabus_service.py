import json
from typing import Dict, Any, List
from fastapi import HTTPException, status
from core.llm.factory import get_llm_provider
from core.security import check_prompt_injection

SYLLABUS_OPTIMIZER_PROMPT = """
You are a Senior Curriculum Architect at a top Big Tech company (Google/NVIDIA).
Analyze the following university syllabus and distinguish between "Academic Filler" and "Industry Gold".

SYLLABUS CONTENT:
{syllabus_text}

OUTPUT FORMAT:
Return ONLY a valid JSON object:
{{
  "industry_gold": [
    {{
      "topic": "string",
      "why_it_matters": "string",
      "real_world_application": "string",
      "priority": "High" | "Medium"
    }}
  ],
  "academic_filler": [
    {{
      "topic": "string",
      "industry_replacement": "string (What should they learn instead?)",
      "reason": "string"
    }}
  ],
  "career_roadmap": [
    {{
      "phase": "string (e.g., Sem 1-2)",
      "target_skill": "string",
      "industry_milestone": "string"
    }}
  ],
  "overall_relevance_score": float (0-100)
}}
"""

async def optimize_syllabus(syllabus_text: str) -> Dict[str, Any]:
    """
    Validate and analyze a university syllabus for Big Tech industry readiness.

    Before forwarding any user-supplied content to the LLM, the function runs a
    prompt injection check on ``syllabus_text``.  If a potential injection
    pattern is found the request is rejected immediately with HTTP 400, ensuring
    that malicious payloads cannot hijack the system prompt.

    On clean input, the syllabus is embedded into ``SYLLABUS_OPTIMIZER_PROMPT``
    and sent to the configured LLM provider via ``generate_json``.  The model
    returns a structured curriculum analysis that classifies topics into
    ``industry_gold`` and ``academic_filler`` categories, proposes a career
    roadmap, and assigns an overall relevance score.

    Args:
        syllabus_text: Raw text of the university syllabus submitted by the user.

    Returns:
        A dict with keys ``industry_gold``, ``academic_filler``,
        ``career_roadmap``, and ``overall_relevance_score`` as defined in
        ``SYLLABUS_OPTIMIZER_PROMPT``.

    Raises:
        HTTPException: HTTP 400 if prompt injection is detected in the syllabus
            content.
    """
    if check_prompt_injection(syllabus_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security validation failed: Potential prompt injection detected in syllabus content."
        )

    llm = get_llm_provider()

    prompt = SYLLABUS_OPTIMIZER_PROMPT.format(syllabus_text=syllabus_text)

    analysis = await llm.generate_json(
        messages=[{"role": "user", "content": "Analyze this syllabus for Big Tech readiness."}],
        system_prompt=prompt
    )

    return analysis
