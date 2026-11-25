# VIREONIQ AI Governance, Legal Readiness & Compliance Architecture

> **Engineering Readiness Notice**: This document details technical capabilities, logging infrastructures, bias audit metrics, and consent architectures designed to facilitate legal conformity. It does not constitute formal legal advice. A list of items requiring qualified counsel review is provided in Section 5.

---

## 1. Algorithmic Risk Classification by Feature

| Subsystem / Feature | Risk Level | Regulatory Scope | Governance Rationale |
|---|---|---|---|
| **Recruiter Candidate Discovery & Ranking** (`/api/v1/recruiter-intel/*`) | **High Risk** | EU AI Act (Annex III, point 4); NYC Local Law 144 | Directly impacts candidate selection, recruitment opportunities, and shortlisting. Mandates annual independent bias audits and human oversight. |
| **Skill Assessment & Credential Minting** (`/api/v1/credentials/*`) | **High Risk** | EU AI Act (Annex III, point 4) | Evaluates candidate competency for employment opportunities. |
| **Candidate ATS Studio & Career Coach** (`/api/v1/resume-builder/*`, RAG Coach) | **Low / Minimal Risk** | EU AI Act (General Transparency) | Self-directed candidate preparation tool; candidate retains full editing agency over their own resume. |
| **High School / Minor Career Exploration** (`/api/v1/earn-to-learn/*`) | **Special Protected** | India DPDP Act 2025; COPPA / GDPR-K | Serves minors; mandates verifiable parental consent and strict data minimization. |

---

## 2. EU AI Act Technical Readiness (Annex III Employment AI)

*Enforcement Timeline: High-risk employment systems apply December 2, 2027 (per European Commission implementation timeline).*

- **Risk Management System (Art. 9)**: Continuous automated testing of prompt injection defenses, bias disparities, and model calibration (`eval/model_gate.py`).
- **Data Governance (Art. 10)**: Strict entity-level splits, provenance tracking, and representation audit documentation (`docs/DATA_SOURCES.md`).
- **Technical Documentation (Art. 11)**: Architecture diagrams, Model Gate scorecards, and reproducible evaluation manifests in `docs/evals/`.
- **Automatic Logging & Record-Keeping (Art. 12)**: Relational audit log (`SecurityAuditLog`) recording timestamp, model version, input hash, output scores, and user IDs.
- **Human Oversight (Art. 14)**: Level 3 autonomy guard requires human confirmation for job applications; substantive reviewer telemetry records override frequencies (`services/responsible_ai.py`).
- **Accuracy, Robustness & Cybersecurity (Art. 15)**: Defense against document prompt injection and supply chain tampering (`core/model_safety.py`, `services/document_defense.py`).

---

## 3. NYC Local Law 144 (AEDT Bias Audit Readiness)

For employers deploying Automated Employment Decision Tools (AEDTs) in New York City:
- **Independent Bias Audit Exporter**: The system computes and exports selection rates, scoring rates, and Impact Ratios across protected gender and race/ethnicity categories.
- **Impact Ratio ($IR$) Formula**:
  $$IR = \frac{\text{Selection Rate}_{\text{Evaluated Group}}}{\text{Selection Rate}_{\text{Most Favored Group}}}$$
- **10-Business-Day Advance Notice**: Standard notice template:
  > *"Notice to Candidates: An automated employment decision tool will be used to assess qualifications for this position. You have the right to request an alternative evaluation process or reasonable accommodation by contacting [Designated HR Contact]."*

---

## 4. India Digital Personal Data Protection (DPDP) Act & Rules 2025

*Notified November 14, 2025; core obligations rolling out through mid-2027.*

- **Consent Notice**: Plain language consent notices presented prior to document ingestion, clearly identifying the data fiduciary and specific processing purposes.
- **Verifiable Parental Consent**: For users under 18 years of age engaging with career guidance features, the system requires parent/guardian verification tokens before enabling data sharing.
- **Right to Erasure & Export**: Candidates can export all profile, assessment, and credential data (`GET /api/v1/privacy-security/export`) or permanently delete their account and associated vectors (`POST /api/v1/privacy-security/account/delete`).
- **Data Retention Schedule**: Raw uploaded documents are purged after 90 days of inactivity; aggregated anonymized skill graph nodes are retained for model calibration.

---

## 5. Open Legal Questions Requiring Qualified Counsel Review

1. **AEDT Scope Determination**: Formal legal confirmation of whether candidate-facing ATS scoring functions fall within NYC Local Law 144 when results are visible to recruiter portal users.
2. **Minor Age Verification Standard**: Formal approval of the verifiable parental consent mechanism under the India DPDP Rules for Indian high-school internship programs.
3. **Cross-Border Talent Data Transfers**: Legal evaluation of EU-to-India / US data flow agreements regarding cloud vector embeddings.
4. **License Reconcilement**: Legal confirmation from repository ownership regarding the formal adoption of the software license.
