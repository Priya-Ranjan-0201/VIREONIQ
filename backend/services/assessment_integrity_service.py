"""
Assessment Integrity & Anti-Gaming Signal Service.
Analyzes interaction telemetry (typing rate, paste bursts, timing anomalies, similarity)
to produce non-punitive, objective Assessment Integrity Signals:
  - Never claims 'Cheating Confirmed'
  - Emits Signal, Severity (LOW, MEDIUM, HIGH), Confidence, and human-readable explanation
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def evaluate_interaction_integrity(
    submission_text: str,
    duration_seconds: float,
    paste_event_count: int = 0,
    paste_character_count: int = 0
) -> Dict[str, Any]:
    """
    Evaluates timing and interaction telemetry for anomalies.
    """
    char_count = len(submission_text) if submission_text else 0
    signals = []
    integrity_score = 100.0

    # Check 1: Ultra-fast submission of large text / code (Paste Burst Anomaly)
    if char_count > 300 and duration_seconds < 3.0:
        signals.append({
            "signal_type": "RAPID_SUBMISSION_BURST",
            "severity": "MEDIUM",
            "confidence": "HIGH",
            "explanation": f"Submission of {char_count} characters completed in {duration_seconds:.1f}s indicates an external clipboard transfer."
        })
        integrity_score -= 15.0

    # Check 2: High Paste-to-Type Ratio
    if paste_character_count > 0 and char_count > 0:
        paste_ratio = paste_character_count / char_count
        if paste_ratio > 0.85 and char_count > 400:
            signals.append({
                "signal_type": "HIGH_PASTE_RATIO",
                "severity": "LOW",
                "confidence": "MEDIUM",
                "explanation": f"{paste_ratio*100:.0f}% of submission characters originated from clipboard paste operations."
            })
            integrity_score -= 10.0

    # Determine status
    if integrity_score >= 85.0:
        status = "VERIFIED"
    elif integrity_score >= 65.0:
        status = "FLAGGED_REVIEW"
    else:
        status = "AUDIT_REQUIRED"

    return {
        "integrity_score": max(20.0, round(integrity_score, 1)),
        "integrity_status": status,
        "signals_count": len(signals),
        "signals": signals,
        "is_credential_eligible": integrity_score >= 80.0
    }
