# VIREONIQ — Human-Only Tasks Ledger (Launch Dependencies)

This document tracks all operational, legal, financial, and administrative dependencies that **cannot be automated by an AI agent** and require human execution by the product owner or legal/business stakeholders prior to global public traffic routing.

---

## 1. Summary Overview

| Category | Total Tasks | Blockers for Public Beta | Owner Role |
| :--- | :---: | :---: | :--- |
| **Legal & Compliance** | 4 | 2 (Counsel Review, DPO Appointment) | Legal Counsel / Founder |
| **Financial & Banking** | 3 | 2 (Gateway Production KYC, Tax ID) | Founder / Finance Lead |
| **Infrastructure & Cloud** | 4 | 1 (Domain & DNS Provisioning) | DevOps / Cloud Admin |
| **Vendor Enterprise DPAs** | 3 | 1 (LLM Enterprise Privacy DPA) | Operations Lead |
| **Security & Audits** | 2 | 0 (Post-Launch Formal Pen-Test) | Security Lead |
| **Support & Operations** | 3 | 1 (Designated Support Inbox) | Customer Success Lead |

---

## 2. Detailed Task Breakdown

### A. Legal & Regulatory Compliance

| Task ID | Task Description | Owner | Estimated Effort | Blocker Status | Notes & Action Items |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **HT-LEG-01** | **Legal Counsel Review of Terms of Service & Privacy Policy** | Legal Counsel | 3–5 days | **BLOCKER for Public Launch** | Submit [docs/TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md) and [docs/PRIVACY.md](PRIVACY.md) to qualified SaaS/tech counsel for review under local consumer protection and GDPR/CCPA regulations. |
| **HT-LEG-02** | **Formal Appointment of Data Protection & Grievance Officer** | Founder | 1 day | **BLOCKER for India / EU** | Under India IT Rules and GDPR, designate statutory contact name and email (`privacy@vireoniq.com`, `grievance@vireoniq.com`). |
| **HT-LEG-03** | **Commercial Entity & Trademark Registration** | Founder | 1–2 weeks | Non-blocking for Beta | File trademark application for "VIREONIQ" and register operating legal entity (LLC / Private Limited). |
| **HT-LEG-04** | **Commercial Cyber & Errors/Omissions Insurance** | Founder / Broker | 1 week | Non-blocking for Beta | Obtain standard commercial technology liability and cyber incident insurance coverage. |

---

### B. Financial, Banking & Payment Gateway

| Task ID | Task Description | Owner | Estimated Effort | Blocker Status | Notes & Action Items |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **HT-FIN-01** | **Payment Gateway Merchant KYC (Razorpay / Stripe)** | Finance / Founder | 3–7 business days | **BLOCKER for Monetization** | Complete live business onboarding, bank account linking, and submit website URL with published Terms, Privacy, and Refund policies. |
| **HT-FIN-02** | **Live Gateway API Secret Generation** | Founder | 1 hour | **BLOCKER for Live Payments** | Generate production `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`; store directly in cloud secret manager. |
| **HT-FIN-03** | **Tax ID & GST/VAT Configuration** | Finance Lead | 2–3 days | Non-blocking for Free Tier | Configure automated tax calculation / invoicing rules in merchant portal. |

---

### C. Domain, DNS & Cloud Infrastructure

| Task ID | Task Description | Owner | Estimated Effort | Blocker Status | Notes & Action Items |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **HT-INF-01** | **Domain Registration & DNS Management** | DevOps / Founder | 2 hours | **BLOCKER for Public Beta** | Register `vireoniq.com` (or primary production domain) and point Cloudflare nameservers. |
| **HT-INF-02** | **Production Cloud Account & Billing Setup** | Cloud Admin | 1 day | **BLOCKER for Production** | Create dedicated production AWS, GCP, or Render account with budget alerts and automated payment method. |
| **HT-INF-03** | **SSL/TLS & CDN Configuration** | DevOps | 2 hours | **BLOCKER for HTTPS** | Provision Cloudflare / Let's Encrypt managed wild-card certificates with HSTS (`max-age=31536000`). |
| **HT-INF-04** | **Managed Database & Redis Backups** | DBA / DevOps | 1 day | **BLOCKER for Production** | Provision managed PostgreSQL 16 (RDS / Supabase / Cloud SQL) and Redis 7 with automated 24h point-in-time recovery (PITR). |

---

### D. Vendor Agreements & Enterprise Privacy DPAs

| Task ID | Task Description | Owner | Estimated Effort | Blocker Status | Notes & Action Items |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **HT-VEN-01** | **OpenAI / Anthropic Enterprise Zero-Retention DPA** | Operations Lead | 2–4 days | **BLOCKER for Public AI** | Confirm Enterprise API terms with AI providers ensuring zero model training on user prompt data and 30-day zero-retention where eligible. |
| **HT-VEN-02** | **Transactional Email Delivery (AWS SES / SendGrid)** | DevOps | 1–2 days | **BLOCKER for Email Verification** | Complete domain verification (SPF, DKIM, DMARC) and request removal from AWS SES sandbox mode to send to arbitrary recipient addresses. |
| **HT-VEN-03** | **Judge0 Sandbox Dedicated Cluster** | DevOps | 1–2 days | Non-blocking (Feature Gated) | Provision dedicated isolated Judge0 instance or enterprise plan if high-concurrency coding interviews are activated. |

---

### E. Support, Moderation & Public Handover

| Task ID | Task Description | Owner | Estimated Effort | Blocker Status | Notes & Action Items |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **HT-OPS-01** | **Dedicated Support Email & Helpdesk Ingestion** | Support Lead | 1 day | **BLOCKER for Public Launch** | Configure `support@vireoniq.com` routing to a shared ticketing inbox (Zendesk, Crisp, or Google Workspace Collaborative Inbox). |
| **HT-OPS-02** | **Grievance Triage & Escalation Procedures** | Operations Lead | 1 day | Non-blocking | Establish 24-hour turnaround response workflow for user account deletion or content dispute requests. |
| **HT-OPS-03** | **Third-Party External Penetration Testing** | Security Lead / Vendor | 2 weeks | Non-blocking for Beta (Recommended for GA) | Engage certified CREST or OSCP firm to perform gray-box penetration test against staging API endpoints. |
