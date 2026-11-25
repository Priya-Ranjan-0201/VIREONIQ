# VIREONIQ — Canonical API Reference

## 1. API Architecture

- **Base Prefix**: `/api/v1` (plus root `/health` probe)
- **Protocol**: HTTP/REST + JSON (`313` OpenAPI HTTP operations mounted across `75` endpoint modules) and WebSockets (`/api/v1/ws/matchmaker/{user_id}`, `/api/v1/advanced/adversarial/{session_id}/stream`)
- **Authentication**: Bearer JWT (`RS256`) in `Authorization: Bearer <token>` header; refresh tokens rotate via `HttpOnly` cookies

---

## 2. Core Endpoint Index (Verified Against Mounted Router)

### System Health (`/health`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/health` | Application liveness and database connectivity check | No |
| `GET` | `/api/v1/health` | API v1 status check | No |

### Authentication & Identity (`/api/v1/auth`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/auth/register` | Register standard candidate/user account (`User`, `student`, `candidate`) with Argon2id | No |
| `POST` | `/api/v1/auth/login` | Authenticate and issue RS256 access JWT + `HttpOnly` refresh cookie | No |
| `POST` | `/api/v1/auth/refresh` | Rotate `HttpOnly` refresh cookie and issue new access JWT | Cookie |
| `POST` | `/api/v1/auth/logout` | Blacklist access JTI and revoke refresh session | Yes |
| `GET` | `/api/v1/auth/me` | Return authenticated user profile | Yes |

### Career Digital Twin & Evidence (`/api/v1/career-twin`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/api/v1/career-twin` | Retrieve Career Digital Twin snapshot | Yes |
| `GET` | `/api/v1/career-twin/skills` | Retrieve candidate skill inventory, conflicts, and relationships | Yes |
| `GET` | `/api/v1/career-twin/evidence` | Retrieve evidence items or trace lineage by `skill_name` | Yes |
| `GET` | `/api/v1/career-twin/forecast` | Multi-horizon trajectory projection scenarios | Yes |
| `GET` | `/api/v1/career-twin/conflicts` | Structured evidence conflict checks | Yes |
| `GET` | `/api/v1/career-twin/transitions` | Ranked skill transfer bridges to alternative roles | Yes |
| `GET` | `/api/v1/career-twin/change-feed` | Diff-based snapshot change feed | Yes |

### Counterfactual Career Simulator (`/api/v1/career-simulator`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/career-simulator/what-if` | Simulate counterfactual "What if..." career action | Yes |
| `POST` | `/api/v1/career-simulator/compare-scenarios` | Compare counterfactual scenarios | Yes |
| `POST` | `/api/v1/career-simulator/simulate` | Execute non-mutating career simulation | Yes |
| `GET` | `/api/v1/career-simulator/scenarios` | List saved simulation scenarios | Yes |

### Career Readiness & Interventions (`/api/v1/readiness`, `/api/v1/interventions`, `/api/v1/roi-gaps`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/api/v1/readiness` | Compute Career Readiness Index for a target role | Yes |
| `GET` | `/api/v1/readiness/bottlenecks` | Isolate priority capability bottlenecks | Yes |
| `GET` | `/api/v1/roi-gaps/prioritized` | Compute ROI-prioritized skill gaps | Yes |
| `GET` | `/api/v1/interventions/next-best-actions` | Retrieve prioritized Next Best Actions | Yes |
| `GET` | `/api/v1/interventions/explainable-recommendations` | Generate structured decision explanations | Yes |

### Assessments & Code Execution (`/api/v1/assessments`, `/api/v1/advanced`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/assessments/start` | Initialize adaptive assessment session | Yes |
| `GET` | `/api/v1/assessments/{session_id}/next-question` | Fetch next adaptive question | Yes |
| `POST` | `/api/v1/assessments/{session_id}/respond` | Submit assessment response | Yes |
| `POST` | `/api/v1/assessments/{session_id}/complete` | Finalize assessment and compute evaluation | Yes |
| `POST` | `/api/v1/advanced/code/execute` | Submit code to configured sandbox + deterministic Python AST review | Yes |

### MNC-Style Interview Studio (`/api/v1/mnc-interview`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/mnc-interview/blueprint` | Generate MNC interview round blueprint | Yes |
| `GET` | `/api/v1/mnc-interview/memory` | Retrieve cross-session interview memory & competency trends | Yes |
| `POST` | `/api/v1/mnc-interview/adaptive-next` | Select next adaptive question | Yes |
| `POST` | `/api/v1/mnc-interview/sessions/start` | Start simulated interview session | Yes |
| `POST` | `/api/v1/mnc-interview/sessions/{session_id}/answer` | Submit interview turn answer | Yes |
| `POST` | `/api/v1/mnc-interview/sessions/{session_id}/code/submit` | Validate candidate coding submission | Yes |

### Talent Passport & Credentials (`/api/v1/credentials`, `/api/v1/passport`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/credentials/issue` | Issue HMAC-SHA256 signed credential when evidence criteria pass | Yes |
| `GET` | `/api/v1/credentials/verify/{public_reference}` | Publicly verify issued credential authenticity | No |
| `POST` | `/api/v1/passport/share` | Generate data-minimized public passport share link | Yes |
| `GET` | `/api/v1/passport/public/{share_token}` | Public read-only Talent Passport view | No |

### Recruiter & Workforce Intelligence (`/api/v1/recruiter-intel`, `/api/v1/org`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/recruiter-intel/discover` | Multi-tenant candidate search and evidence ranking | Yes (Recruiter/Admin) |
| `GET` | `/api/v1/recruiter-intel/jobs` | List organization job postings | Yes (Recruiter/Admin) |
| `GET` | `/api/v1/org/capabilities` | Organizational capability coverage breakdown | Yes (Org Admin/Recruiter) |
| `GET` | `/api/v1/org/matrix` | Organizational 2D capability matrix | Yes (Org Admin/Recruiter) |

### Resume Studio & ATS Scoring (`/api/v1/resume-builder`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/api/v1/resume-builder/metadata` | Retrieve 30 configured company profiles and 15 role taxonomies | No |
| `POST` | `/api/v1/resume-builder/parse-text` | Parse raw resume text into structured fields with ATS score | Optional |
| `POST` | `/api/v1/resume-builder/parse-file` | Parse uploaded PDF/DOCX resume (max 5 MB, MIME checked) | Yes |
| `POST` | `/api/v1/resume-builder/calculate-ats` | Compute 6-dimension ATS rubric score | Optional |
| `POST` | `/api/v1/resume-builder/optimize-mnc` | Rewrite bullets using action-verb/XYZ templates | Yes |
| `POST` | `/api/v1/resume-builder/improve-section` | Targeted section rewrite/condense/expand | Yes |

### Privacy, Payments & Analytics (`/api/v1/privacy-security`, `/api/v1/payments`, `/api/v1/analytics`)
| Method | Path | Summary | Auth Required |
|:---|:---|:---|:---:|
| `GET` | `/api/v1/privacy-security/preferences` | Retrieve candidate privacy opt-in preferences | Yes |
| `PUT` | `/api/v1/privacy-security/preferences` | Update candidate privacy opt-in preferences | Yes |
| `GET` | `/api/v1/privacy-security/export` | Export candidate profile, skills, projects, credentials, and simulations | Yes |
| `POST` | `/api/v1/privacy-security/account/delete` | Delete candidate profile/preferences/skills/user while keeping `SecurityAuditLog` | Yes |
| `GET` | `/api/v1/privacy-security/audit-logs` | List scoped security audit logs | Yes |
| `POST` | `/api/v1/payments/order` | Create pending Razorpay payment transaction | Yes |
| `POST` | `/api/v1/payments/verify` | Verify HMAC signature (fails closed without `RAZORPAY_KEY_SECRET`), ownership, and plan amount | Yes |
| `GET` | `/api/v1/analytics/overview` | DB-backed dashboard stats (ATS score, applications, cognitive archetype) | Yes |
