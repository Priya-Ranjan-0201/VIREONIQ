"""
AI Reliability & Validation Layer.
Ensures:
  1. Strict Pydantic schema validation for LLM JSON outputs
  2. Evidence grounding validation (rejects fabricated claims / unsupported entities)
  3. Layered prompt injection mitigation & untrusted document tagging
"""

import re
import json
import logging
from typing import Dict, Any, Type, Optional, Tuple, List
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

def sanitize_untrusted_input(text: str, source_label: str = "UNTRUSTED_USER_INPUT") -> str:
    """
    Wraps user-provided text in clear security boundary delimiters to prevent prompt injection.
    """
    if not text:
        return ""
    # Strip potential delimiter escapes
    cleaned = text.replace("<<<", "").replace(">>>", "")
    return f"\n<<<{source_label}>>>\n{cleaned}\n<<<END_{source_label}>>>\n"

def validate_llm_json_schema(raw_response: str, schema_class: Optional[Type[BaseModel]] = None) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Parses and validates LLM JSON response against a target Pydantic schema.
    Returns: (is_valid, parsed_dict, error_message)
    """
    try:
        # Extract JSON block if wrapped in markdown
        cleaned = raw_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        data = json.loads(cleaned)
        
        if schema_class:
            validated_obj = schema_class.model_validate(data)
            return True, validated_obj.model_dump(), None
        return True, data, None

    except json.JSONDecodeError as je:
        logger.warning(f"LLM output JSON decode failure: {je}")
        return False, {}, f"JSON Decode Error: {str(je)}"
    except ValidationError as ve:
        logger.warning(f"LLM output schema validation failure: {ve}")
        return False, {}, f"Schema Validation Error: {str(ve)}"
    except Exception as e:
        logger.warning(f"Unexpected validation error: {e}")
        return False, {}, str(e)

def verify_evidence_grounding(extracted_claims: List[str], ground_truth_text: str) -> List[Dict[str, Any]]:
    """
    Checks whether extracted claims/skills actually exist in the underlying candidate evidence.
    Downgrades or flags unsupported hallucinated claims.
    """
    ground_truth_lower = ground_truth_text.lower()
    verified_results = []
    
    for claim in extracted_claims:
        claim_clean = str(claim).strip()
        if not claim_clean:
            continue
        is_grounded = claim_clean.lower() in ground_truth_lower
        verified_results.append({
            "claim": claim_clean,
            "grounded_in_evidence": is_grounded,
            "status": "GROUNDED" if is_grounded else "UNSUPPORTED_DOWNGRADED"
        })
        
    return verified_results
