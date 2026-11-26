# Model Card: RAG Career Coach

- **Component ID**: `rag_career_coach`
- **Status**: Shipped (Citation-Grounded + Selective Abstention)
- **Evaluation Unit**: Single career-coaching Q&A turn (`answer_career_inquiry`)

## 1. Intended Use & Scope
- Generates structured career preparation guidance grounded strictly in retrieved evidence chunks with explicit chunk citations.
- Abstains (`status = "ABSTAIN"`) whenever maximum retrieval relevance falls below `0.40` (configurable threshold).

## 2. Safety & Privacy Controls
- Candidate text is isolated inside inert XML fence delimiters (`<candidate_untrusted_document_data>`) after `DocumentDefenseInspector` inspection (`backend/services/document_defense.py`).
- PII redacted before logging or outbound provider calls (`core/pii_redactor.py`).
- Level-3 Autonomy Guard (`ResponsibleAIEngine.enforce_agency_guard`) blocks job applications, recruiter messaging, or goal mutations without explicit user confirmation.

## 3. Limitations
- Default CI tests run against a deterministic fake LLM/embedding provider; live hosted LLM behavior requires manual evaluation (`heavy-eval.yml`) with human judge validation.
- Judge calibration against human labels on real career coaching outputs remains limited (see `docs/RESEARCH.md` finding F4/F7).
