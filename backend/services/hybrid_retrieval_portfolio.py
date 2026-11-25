"""
Hybrid Retrieval and Ranking Portfolio.

Implements:
1. Lexical Retrieval (Okapi BM25).
2. Dense Vector Retrieval (Cosine similarity).
3. Reciprocal Rank Fusion (RRF) combining dense and sparse candidate streams.
"""

import math
from typing import Any, Dict, List, Sequence, Tuple


class BM25Retriever:
    """
    Okapi BM25 Lexical Scorer.
    """

    def __init__(self, corpus: Sequence[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_lens = [len(doc.get("text", "").split()) for doc in corpus]
        self.avg_doc_len = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1.0

        # Term frequencies and document frequencies
        self.doc_freqs: Dict[str, int] = {}
        for doc in corpus:
            tokens = set(doc.get("text", "").lower().split())
            for t in tokens:
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q_tokens = query.lower().split()
        scores: List[Tuple[str, float]] = []

        n_docs = len(self.corpus)
        for idx, doc in enumerate(self.corpus):
            doc_id = str(doc.get("id", f"doc_{idx}"))
            doc_words = doc.get("text", "").lower().split()
            doc_len = self.doc_lens[idx] if idx < len(self.doc_lens) else len(doc_words)

            score = 0.0
            for t in q_tokens:
                if t not in self.doc_freqs:
                    continue
                df = self.doc_freqs[t]
                idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))

                tf = doc_words.count(t)
                tf_norm = (tf * (self.k1 + 1.0)) / (tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len)))
                score += idf * tf_norm

            scores.append((doc_id, round(score, 4)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Computes cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return round(dot / (norm_a * norm_b), 4)


def reciprocal_rank_fusion(
    ranked_lists: Sequence[List[Tuple[str, float]]],
    c: int = 60,
    top_k: int = 10,
) -> List[Tuple[str, float]]:
    """
    Combines multiple rankings (e.g. dense + lexical) using standard Reciprocal Rank Fusion.
    RRF_score(d) = sum(1 / (c + rank_m(d)))
    """
    scores: Dict[str, float] = {}

    for r_list in ranked_lists:
        for rank, (doc_id, _) in enumerate(r_list, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (c + rank))

    fused = [(doc_id, round(score, 6)) for doc_id, score in scores.items()]
    fused.sort(key=lambda x: x[1], reverse=True)
    return fused[:top_k]
