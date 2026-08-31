# VIREONIQ X — Canonical API Reference

## 1. API Architecture

- **Base URL**: `/api/v1`
- **Protocol**: HTTP/REST + JSON (RFC 8259)
- **Authentication**: Bearer JWT (RS256) in `Authorization: Bearer <token>` header
- **Error Format**:
```json
{
  "detail": "Error description message",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2026-08-25T01:00:00Z"
}
```

---

## 2. Core Endpoint Index

### Authentication & Identity (`/auth`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/auth/register` | Register new user account with Argon2id | No |
| `POST` | `/auth/login` | Authenticate and issue RS256 JWT | No |
| `POST` | `/auth/refresh` | Exchange secure refresh cookie for new access token | No |
| `POST` | `/auth/logout` | Revoke session and blacklist JWT in Redis | Yes |

### Career Digital Twin & Evidence (`/career-twin`, `/evidence-graph`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/career-twin/snapshot` | Retrieve 10-state evidence graph, 6 capabilities, and readiness | Yes |
| `GET` | `/career-twin/change-feed` | Retrieve "What Changed?" lightweight feed powered by twin diffs | Yes |
| `GET` | `/career-twin/forecast` | 3, 6, 12-month trajectory projection scenarios | Yes |
| `GET` | `/career-twin/conflicts` | Structured Evidence Conflict cards with neutral terminology | Yes |
| `GET` | `/career-twin/transitions` | Ranked skill transfer bridges to alternative target roles | Yes |
| `POST` | `/career-twin/diff` | Calculate explainable diff between two twin states | Yes |
| `POST` | `/evidence/ingest` | Ingest external signal into evidence graph (starts as OBSERVED) | Yes |

### Counterfactual Career Simulator (`/career-simulator`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/career-simulator/what-if` | Simulates individual counterfactual "What if I..." decision | Yes |
| `POST` | `/career-simulator/compare-scenarios` | Side-by-side ROI comparison matrix across paths | Yes |
| `POST` | `/career-simulator/simulate` | Execute zero-mutation sandbox simulation | Yes |

### 9D Career Readiness & Interventions (`/readiness`, `/interventions`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/readiness/calculate` | Compute 9D Readiness Index with critical bottleneck | Yes |
| `GET` | `/readiness/bottleneck` | Isolate top priority capability blocker | Yes |
| `POST` | `/readiness/roi-gap` | Optimize learning investment for target role | Yes |
| `GET` | `/interventions/next-best-actions` | Prioritize actions resolving conflicts & prerequisite bottlenecks | Yes |
| `GET` | `/interventions/explainable-recommendations` | Generate evidence-backed, transparent decision explanations (no false precision) | Yes |

### Assessments & Sandboxed Coding (`/assessments`, `/coding`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/assessments/start` | Initialize proctored assessment session | Yes |
| `POST` | `/assessments/{id}/respond` | Submit code attempt with deterministic AST complexity analysis | Yes |
| `GET` | `/assessments/{id}/report` | Retrieve itemized rubric score and Intelligence Receipt | Yes |

### MNC-Style Interview Studio (`/mnc-interview`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/mnc-interview/generate-blueprint` | Generate MNC-style 8-round company blueprint | Yes |
| `GET` | `/mnc-interview/memory` | Retrieve candidate's cross-session competency trend memory | Yes |
| `POST` | `/mnc-interview/adaptive-next` | Adaptively select next question blueprint by performance | Yes |
| `POST` | `/mnc-interview/turn` | Execute conversational interview turn with real-time feedback | Yes |
| `POST` | `/mnc-interview/evaluate-coding` | Validate candidate solution with deterministic AST & test cases | Yes |

### Talent Passport & Credentials (`/credentials`, `/passport`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/credentials/mint` | Mint HMAC-SHA256 cryptographically signed credential | Yes |
| `GET` | `/verify/{public_ref}` | Publicly verify digital talent credential authenticity | No |
| `POST` | `/passport/share-link` | Generate data-minimized public passport link | Yes |

### Recruiter & Workforce Intelligence (`/recruiter-intelligence`, `/workforce-intelligence`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/recruiter-intelligence/match` | Multi-tenant candidate search and evidence-weighted ranking | Yes (Recruiter) |
| `GET` | `/workforce-intelligence/matrix` | Organizational 2D capability heatmap and concentration risks | Yes (Org Admin) |

### Resume Studio & Real-Time ATS Scoring (`/resume-builder`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/resume-builder/parse-text` | Parse raw resume text into structured fields with baseline ATS score | Optional |
| `POST` | `/resume-builder/parse-file` | Parse uploaded PDF/DOCX resume file into structured fields | Optional |
| `POST` | `/resume-builder/calculate-ats` | Real-time 6-dimension deterministic ATS scoring (90+ MNC tier target) | Optional |
| `POST` | `/resume-builder/optimize-mnc` | Supercharge bullets into Google XYZ format with quantified metrics & action verbs | Optional |
| `POST` | `/resume-builder/improve-section` | Target section rewriter (rewrite, expand, condense, ATS-optimize) | Optional |

### Privacy & Governance (`/privacy-security`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/privacy-security/export` | Export complete candidate profile under GDPR/CCPA | Yes |
| `POST` | `/privacy-security/delete-account` | Execute permanent cryptographic data erasure | Yes |
