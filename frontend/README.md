# 🎨 VIREONIQ X — Modern Frontend Architecture & UI Guide

The frontend for **VIREONIQ (PLACEIQ)** is a high-performance, single-page web application built with **React 18**, **TypeScript**, and **Vite 5**, styled using **Tailwind CSS 3.4** and **Radix UI** primitives, with smooth micro-animations powered by **Framer Motion**.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|:---|:---|:---|
| **Framework & Core** | React 18.2 + TypeScript 5.0+ | Strict type-safe UI component hierarchy |
| **Bundler & Dev Server** | Vite 5.0+ | Sub-second HMR and production bundle optimization |
| **Styling & Design System** | Tailwind CSS 3.4 | Utility-first responsive design and dark-mode styling |
| **Icons & Visuals** | Lucide React | Clean, modern iconography |
| **Micro-Animations** | Framer Motion | Fluid transitions, modal entries, and interactive gestures |
| **State Management** | Zustand | Lightweight, atomic client-side state stores |
| **Charts & Telemetry** | Recharts | 9D Readiness radars, capability heatmaps, and funnel graphs |
| **Code Execution Lab** | Monaco Editor | In-browser multi-language IDE with syntax highlighting |
| **Toasts & Notifications** | Sonner | Real-time interactive toast notifications |

---

## 📂 Frontend Directory Structure

```text
frontend/
├── src/
│   ├── api/
│   │   └── client.ts                   # Axios client with RS256 Bearer auth interceptors
│   ├── components/                     # Reusable UI component library
│   │   ├── ui/                         # Atomic primitives (Button, Modal, Input, Badge, Card)
│   │   ├── Navbar.tsx                  # Global navigation bar with role switcher
│   │   ├── Sidebar.tsx                 # Responsive collapsible app sidebar
│   │   └── ProtectedRoute.tsx          # Client-side authentication guard
│   ├── layouts/
│   │   └── DashboardLayout.tsx         # Unified dashboard shell with breadcrumbs & status
│   ├── pages/                          # Application pages and feature hubs
│   │   ├── ResumeBuilder.tsx           # MNC 90+ ATS AI Resume Builder with Google XYZ formula
│   │   ├── CareerRebirth.tsx           # Non-linear career transition roadmap & skill mapper
│   │   ├── TruthDatabase.tsx           # Verified salaries, interview logs & company transparency
│   │   ├── TalentPassport.tsx          # Cryptographically signed talent passport & badges
│   │   ├── EmployerTruthScore.tsx      # Crowdsourced employer culture and toxicity ratings
│   │   ├── HighSchoolTrajectory.tsx    # Early-career guidance & university pathway planner
│   │   ├── LabMode.tsx                 # In-browser Monaco coding sandbox & AST complexity lab
│   │   ├── MentorNetwork.tsx           # Peer & expert mentorship connection portal
│   │   ├── CommunityHub.tsx            # Placement discussions, interview tips & leaderboards
│   │   ├── EarnToLearn.tsx             # Skill-based micro-task earnings and bounty board
│   │   ├── OfflinePractice.tsx         # PWA-enabled offline mock questions and drills
│   │   ├── ParentConnect.tsx           # Parent progress visibility and placement insights
│   │   ├── FacultyDashboard.tsx        # Institutional placement tracking and batch analytics
│   │   ├── LanguageBridge.tsx          # Multilingual interview translation and phonetic coaching
│   │   ├── VernacularLibrary.tsx       # Regional vernacular learning resources
│   │   ├── CohortMode.tsx              # Batch study groups, peer code reviews & mock challenges
│   │   ├── auth/                       # Login, Register, Forgot Password, and SSO
│   │   ├── dashboard/                  # Candidate Career Control Center & Overview
│   │   ├── interview/                  # MNC Interview Studio, Voice Mode & Coding Room
│   │   ├── readiness/                  # 9-Dimensional Career Readiness Index & Bottlenecks
│   │   ├── assessment/                 # Adaptive coding, system design & proctored exams
│   │   ├── recruiter/                  # Recruiter candidate search, filters & talent pool
│   │   ├── workforce/                  # Enterprise 2D capability matrix & risk maps
│   │   ├── simulator/                  # Counterfactual career scenario planner
│   │   ├── developer/                  # Developer API keys, Webhooks & DLQ monitor
│   │   ├── certification/              # Production 9-Domain release gate scorecard
│   │   └── settings/                   # Profile, notifications & GDPR privacy settings
│   ├── store/                          # Zustand global state stores
│   │   ├── authStore.ts                # Session state, tokens, and active user profile
│   │   ├── careerStore.ts              # Career Twin, readiness scores, and signals
│   │   └── interviewStore.ts           # Active interview session, transcript, and proctoring
│   ├── App.tsx                         # Master React Router catalog
│   ├── main.tsx                        # Application mount point & providers
│   └── index.css                       # Global styles, Tailwind base, and dark mode tokens
├── public/                             # Static assets, logos, and favicon
├── package.json                        # Dependencies and npm scripts
└── vite.config.ts                      # Vite build plugins and path aliases
```

---

## ⚡ Development & Build Commands

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Development Server
```bash
npm run dev
```
- Local URL: **[http://localhost:5173](http://localhost:5173)**
- Includes Hot Module Replacement (HMR).

### 3. Production Build
```bash
npm run build
```
- Compiles TypeScript and packages assets into the `dist/` directory.
- Audited clean build: $6.22\text{s}$ with 0 errors.

### 4. Preview Production Build
```bash
npm run preview
```
- Serves the built `dist/` folder locally on [http://localhost:4173](http://localhost:4173).

---

## 🔑 Default Demonstration Accounts

| Role | Email | Password | Primary Route |
|:---|:---|:---|:---|
| **Candidate** | `test@example.com` | `password` | `/app/control-center` |
| **Demo Student** | `student@vireoniq.com` | `Pass@123` | `/app/control-center` |
| **Recruiter** | `recruiter@vireoniq.com` | `Pass@123` | `/app/recruiter` |
| **Enterprise Admin** | `admin@vireoniq.com` | `Pass@123` | `/app/certification` |

---

<div align="center">
  <sub>© 2026 VIREONIQ (PLACEIQ) — Frontend Engineering Guide</sub>
</div>
