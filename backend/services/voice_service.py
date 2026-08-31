"""
Web Speech API integration service.
Processes transcribed audio text, formats inputs, and logs events.
"""
from typing import Dict, Any


def process_audio_transcript(transcript: str) -> Dict[str, Any]:
    """
    Cleans transcript strings, filters vocal fillers (um, ah, like, you know), and returns clean text.
    """
    fillers = ["um", "uh", "ah", "like", "you know", "basically", "actually"]
    words = transcript.split()
    cleaned_words = [w for w in words if w.lower().strip(",.?!") not in fillers]
    
    cleaned_text = " ".join(cleaned_words)
    filler_count = len(words) - len(cleaned_words)
    filler_ratio = filler_count / max(len(words), 1)
    
    return {
        "original_transcript": transcript,
        "cleaned_text": cleaned_text,
        "filler_words_detected": filler_count,
        "filler_words_ratio": round(filler_ratio, 4)
    }
