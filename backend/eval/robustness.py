"""
Robustness and Perturbation Evaluation Suite.

Evaluates scoring resilience against:
1. Formatting invariance (plain text, markdown, extra whitespace).
2. Keyword stuffing (detecting artificial score inflation).
3. Minor typographical perturbations.
"""

from typing import Any, Callable, Dict, List


class RobustnessSuite:
    """
    Tests whether model scoring functions remain invariant to benign surface formatting
    and resistant to adversarial keyword stuffing.
    """

    @staticmethod
    def test_formatting_invariance(
        scoring_fn: Callable[[str], float],
        base_text: str,
        tolerance: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Verifies that converting text to markdown or modifying whitespace does not
        substantially change the output score (preventing F1 benchmark artifacts).
        """
        base_score = scoring_fn(base_text)

        # Markdown variant
        markdown_variant = f"## Profile\n**Summary:**\n{base_text}\n- Key Experience"
        # Whitespace variant
        whitespace_variant = f"   \n\n{base_text}   \n\t"

        score_md = scoring_fn(markdown_variant)
        score_ws = scoring_fn(whitespace_variant)

        delta_md = abs(score_md - base_score)
        delta_ws = abs(score_ws - base_score)

        passed = (delta_md <= tolerance) and (delta_ws <= tolerance)

        return {
            "passed": passed,
            "base_score": round(base_score, 4),
            "markdown_score": round(score_md, 4),
            "whitespace_score": round(score_ws, 4),
            "max_delta": round(max(delta_md, delta_ws), 4),
            "tolerance": tolerance,
        }

    @staticmethod
    def test_keyword_stuffing_resilience(
        scoring_fn: Callable[[str], float],
        base_text: str,
        keywords: List[str],
        max_acceptable_inflation: float = 0.10,
    ) -> Dict[str, Any]:
        """
        Tests whether appending repeated keyword dumps artificially inflates the match score.
        """
        base_score = scoring_fn(base_text)

        stuffed_text = base_text + "\n" + " ".join(keywords * 10)
        stuffed_score = scoring_fn(stuffed_text)

        inflation = stuffed_score - base_score
        resilient = inflation <= max_acceptable_inflation

        return {
            "resilient": resilient,
            "base_score": round(base_score, 4),
            "stuffed_score": round(stuffed_score, 4),
            "inflation": round(inflation, 4),
            "threshold": max_acceptable_inflation,
        }
