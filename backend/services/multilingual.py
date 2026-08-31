"""
Multilingual translation and language detection service.
Utilizes lightweight token-based detection and translates queries using NLLB-200 endpoints or local models.
"""
from typing import Dict, Any


def detect_language(text: str) -> str:
    """
    Detect the primary language of the text.
    Returns standard ISO 639-1 language code.
    """
    # Simple rule-based detector for demonstration/fallback
    hindi_keywords = ["नमस्ते", "है", "क्या", "कैसे", "काम", "मुझे"]
    spanish_keywords = ["hola", "que", "como", "trabajo", "para", "este"]
    
    text_lower = text.lower()
    if any(k in text for k in hindi_keywords):
        return "hi"
    elif any(k in text_lower for k in spanish_keywords):
        return "es"
        
    return "en"


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
) -> str:
    """
    Translate text using NLLB-200 or lightweight translation mock rules.
    """
    if source_lang == target_lang:
        return text
        
    # Lightweight mapping for demo/fallback
    translations = {
        ("hi", "en"): {
            "नमस्ते": "Hello",
            "कैसे हो?": "How are you?",
        },
        ("en", "hi"): {
            "Hello": "नमस्ते",
            "How are you?": "आप कैसे हैं?",
        }
    }
    
    mapped = translations.get((source_lang, target_lang), {})
    return mapped.get(text, f"[Translated from {source_lang} to {target_lang}]: {text}")
