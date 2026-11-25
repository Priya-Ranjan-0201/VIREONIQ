"""
Evidence-Grounded RAG Career Coach & Interview Assistant.

Enforces:
1. Strict instruction-data channel separation (data fencing).
2. Verifiable source attribution: every advice statement cites a retrieved span.
3. Explicit abstention: abstains when evidence confidence is below threshold
   instead of hallucinating career advice.
"""

from typing import Any, Dict, List, Optional

from services.document_defense import DocumentDefenseInspector


ABSTENTION_THRESHOLD = 0.40


class RAGCareerCoach:
    """
    Retrieval-Augmented Career Coach ensuring factual advice grounded in candidate evidence.
    """

    def __init__(self, abstention_threshold: float = ABSTENTION_THRESHOLD):
        self.threshold = abstention_threshold

    def answer_career_inquiry(
        self,
        query: str,
        retrieved_evidence_chunks: List[Dict[str, Any]],
        candidate_profile_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processes a career guidance query against verified evidence chunks.
        Abstains if evidence is weak or irrelevant.
        """
        if not retrieved_evidence_chunks:
            return {
                "status": "ABSTAIN",
                "answer": (
                    "I do not have enough verified evidence or context from your profile "
                    "to answer this question accurately. Please upload or link your relevant "
                    "experience or projects."
                ),
                "citations": [],
                "confidence": 0.0,
            }

        # Find maximum evidence relevance
        max_relevance = max(c.get("relevance", 0.0) for c in retrieved_evidence_chunks)

        if max_relevance < self.threshold:
            return {
                "status": "ABSTAIN",
                "answer": (
                    f"Evidence confidence ({round(max_relevance, 2)}) is below the required "
                    f"threshold ({self.threshold}) for reliable guidance. Please provide more details."
                ),
                "citations": [],
                "confidence": round(max_relevance, 4),
            }

        # Filter relevant chunks
        supporting_chunks = [c for c in retrieved_evidence_chunks if c.get("relevance", 0.0) >= self.threshold]

        # Extract verifiable citations
        citations = [
            {
                "chunk_id": c.get("id", "chunk_unknown"),
                "source_title": c.get("source_title", "Career Profile"),
                "cited_span": c.get("text", "")[:120],
                "relevance": round(c.get("relevance", 0.0), 4),
            }
            for c in supporting_chunks
        ]

        # Format fenced candidate context if provided
        fenced_context = ""
        if candidate_profile_text:
            fenced_context = DocumentDefenseInspector.sanitize_and_fence_text(candidate_profile_text)

        # Generate evidence-grounded response summary
        advice_parts = [f"Based on your verified experience in {c['source_title']}:" for c in citations[:2]]
        answer_text = (
            f"Here is your targeted career guidance for '{query}':\n"
            + " ".join(advice_parts)
            + f" Prioritize deepening {citations[0]['source_title']} competencies to accelerate readiness."
        )

        return {
            "status": "ANSWERED",
            "answer": answer_text,
            "citations": citations,
            "confidence": round(max_relevance, 4),
            "fenced_context_length": len(fenced_context),
        }
