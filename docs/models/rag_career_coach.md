# Model Card: RAG Career Coach

## Model Details
- **Component**: `RAGCareerCoach` (`backend/services/rag_coach.py`)
- **Version / Status**: `v1.0` — **Shipped**
- **Evaluation Unit**: Grounded Q&A response `(query, retrieved_chunks -> answer + chunk citations | ABSTAIN)`.

## Intended Use & Safety Controls
- **Intended Use**: Evidence-grounded interview and skill-gap coaching citing retrieved source chunk IDs.
- **Abstention & Selective Prediction**: Automatically returns `status="ABSTAIN"` when top chunk relevance falls below threshold (`0.40`) or retrieved chunks are empty.
- **Injection Defense**: Wraps untrusted candidate text inside `<candidate_untrusted_document_data>` fences via `DocumentDefenseInspector`.

## Limitations
- Evaluator agreement with human career coaches can be modest (Part C, F4); outputs are guidance only and never employment determinations.
- Live external LLM providers are disabled in default CI; CI exercises deterministic fake provider fixtures.
