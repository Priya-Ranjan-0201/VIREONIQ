import React, { useEffect, useState } from "react";
import { 
  Brain, ShieldCheck, Target, AlertTriangle, Layers, ArrowRight,
  TrendingUp, Activity, CheckCircle2, Circle, Clock, Sparkles,
  HelpCircle, Eye, GitBranch, Compass, RefreshCw, X, ChevronRight,
  Zap, Code, Flame, Sliders, Calendar, DollarSign, Award, Check, BarChart3
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { careerIntelligenceApi } from "@/api/careerIntelligenceApi";
import type { 
  CareerTwinSnapshot, 
  SkillEvidenceItem 
} from "@/api/careerIntelligenceApi";

export interface RoleTwinProfile {
  targetRole: string;
  readinessScore: number;
  skills: SkillEvidenceItem[];
  evidence: any[];
  timeline: any[];
  criticalGap: string;
  gapDesc: string;
  actionQuest: string;
  nextStep: string;
}

export const ROLE_TWIN_PROFILES: Record<string, RoleTwinProfile> = {
  "Full Stack Engineer": {
    targetRole: "Full Stack Engineer",
    readinessScore: 82,
    criticalGap: "Micro-Frontend State Sync",
    gapDesc: "Zustand & Server-Side Event Synchronization across isolated bundle boundaries.",
    actionQuest: "Architect Event-Driven Store",
    nextStep: "Build distributed state sync with SSE",
    skills: [
      {
        skill_name: "React 19 & Next.js",
        evidence_tier: "VERIFIED",
        score: 88,
        proficiency_level: "L4",
        proficiency_label: "Advanced",
        confidence: "HIGH",
        freshness_score: 98,
        evidence_count: 5,
        explanation: "Verified server actions, streaming Suspense boundaries, and zero-bundle server components.",
        multidimensional_mastery: {
          evidence_coverage_pct: 92,
          weakest_dimension: "Hydration Mismatch Mitigation",
          dimensions: [
            { dimension_name: "Server Actions & Mutate", score: 94 },
            { dimension_name: "Streaming Suspense", score: 90 },
            { dimension_name: "State Architecture", score: 88 },
            { dimension_name: "Web Performance Profiling", score: 85 }
          ]
        }
      },
      {
        skill_name: "TypeScript",
        evidence_tier: "VERIFIED",
        score: 86,
        proficiency_level: "L4",
        proficiency_label: "Advanced",
        confidence: "HIGH",
        freshness_score: 96,
        evidence_count: 4,
        explanation: "Strict compiler flags, discriminated unions, utility types, and AST transformations.",
        multidimensional_mastery: {
          evidence_coverage_pct: 90,
          weakest_dimension: "Conditional Type Distributivity",
          dimensions: [
            { dimension_name: "Generics & Constraints", score: 92 },
            { dimension_name: "Discriminated Unions", score: 90 },
            { dimension_name: "Type Narrowing & Guards", score: 88 },
            { dimension_name: "Module Declarations", score: 82 }
          ]
        }
      },
      {
        skill_name: "FastAPI & Node.js",
        evidence_tier: "ASSESSED",
        score: 80,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 92,
        evidence_count: 3,
        explanation: "Asynchronous route handlers, Pydantic V2 validation, and dependency injection.",
        multidimensional_mastery: {
          evidence_coverage_pct: 84,
          weakest_dimension: "High-Concurrency Profiling",
          dimensions: [
            { dimension_name: "Async REST Handlers", score: 88 },
            { dimension_name: "Pydantic Schema Validation", score: 90 },
            { dimension_name: "Auth & JWT Middleware", score: 82 },
            { dimension_name: "Database Connection Pool", score: 76 }
          ]
        }
      },
      {
        skill_name: "PostgreSQL & Redis",
        evidence_tier: "DEMONSTRATED",
        score: 76,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "MEDIUM",
        freshness_score: 90,
        evidence_count: 3,
        explanation: "Composite B-tree indexing, cache-aside invalidation, and transactional consistency.",
        multidimensional_mastery: {
          evidence_coverage_pct: 78,
          weakest_dimension: "Read Replica Lag Balancing",
          dimensions: [
            { dimension_name: "Schema Design & 3NF", score: 84 },
            { dimension_name: "Redis Cache Patterns", score: 82 },
            { dimension_name: "Query Optimization", score: 74 },
            { dimension_name: "Distributed Locks", score: 72 }
          ]
        }
      },
      {
        skill_name: "Docker & CI/CD",
        evidence_tier: "DEMONSTRATED",
        score: 75,
        proficiency_level: "L2",
        proficiency_label: "Intermediate",
        confidence: "HIGH",
        freshness_score: 88,
        evidence_count: 2,
        explanation: "Multi-stage alpine builds and automated GitHub Actions test matrix.",
        multidimensional_mastery: {
          evidence_coverage_pct: 76,
          weakest_dimension: "BuildKit Cache Mounts",
          dimensions: [
            { dimension_name: "Multi-stage Builds", score: 82 },
            { dimension_name: "GitHub Actions CI", score: 80 },
            { dimension_name: "Docker Compose", score: 75 },
            { dimension_name: "Security Scanning", score: 70 }
          ]
        }
      }
    ],
    evidence: [
      { id: "ev-fs-01", skill_name: "React 19 & Next.js", evidence_type: "PROJECT_REPO", source: "GitHub Repository Analysis", source_span: "Next.js App Router with Server Actions and optimistic updates", source_group: "CAPSTONE_PROJECT", status: "VERIFIED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-30T10:15:00Z" },
      { id: "ev-fs-02", skill_name: "TypeScript", evidence_type: "CODE_SUBMISSION", source: "Diagnostic Studio", source_span: "Full type-safe API client generation from OpenAPI schemas", source_group: "DIAGNOSTIC_LAB", status: "VERIFIED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-29T14:30:00Z" },
      { id: "ev-fs-03", skill_name: "FastAPI", evidence_type: "ASSESSMENT", source: "Technical Assessment", source_span: "Asynchronous dependency injection with connection pooling", source_group: "TECHNICAL_INTERVIEW", status: "ASSESSED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-28T09:00:00Z" },
      { id: "ev-fs-04", skill_name: "PostgreSQL", evidence_type: "CODE_SUBMISSION", source: "Database Lab", source_span: "EXPLAIN ANALYZE index scan verification on composite keys", source_group: "DIAGNOSTIC_LAB", status: "DEMONSTRATED", confidence: "MEDIUM", freshness_state: "FRESH", observed_at: "2026-08-27T16:20:00Z" }
    ],
    timeline: [
      { id: "ev-fs-t1", event_type: "CANONICAL_TWIN_ESTABLISHED", actor: "Career Intelligence Engine", created_at: "2026-08-31T10:00:00Z", event_data: { twin_version: "v2.0.0", target_role: "Full Stack Engineer" } },
      { id: "ev-fs-t2", event_type: "SKILL_EVIDENCE_VERIFIED", actor: "Coding Evaluation Engine", created_at: "2026-08-29T14:30:00Z", event_data: { skill: "React 19 & Next.js", tier: "VERIFIED", score: 88 } }
    ]
  },
  "Backend Engineer": {
    targetRole: "Backend Engineer",
    readinessScore: 76,
    criticalGap: "Distributed Concurrency & Locking",
    gapDesc: "Redlock consensus, distributed transactions, and dead-letter queue architectures.",
    actionQuest: "Solve Distributed Locking Sandbox",
    nextStep: "Implement Redis Redlock in Python",
    skills: [
      {
        skill_name: "Python & Go",
        evidence_tier: "VERIFIED",
        score: 84,
        proficiency_level: "L3",
        proficiency_label: "Proficient",
        confidence: "HIGH",
        freshness_score: 95,
        evidence_count: 4,
        explanation: "Demonstrated in proctored diagnostic coding sandbox & AST evaluation.",
        multidimensional_mastery: {
          evidence_coverage_pct: 88,
          weakest_dimension: "Async Concurrency Under Contention",
          dimensions: [
            { dimension_name: "Core Syntax & AST", score: 92 },
            { dimension_name: "Asynchronous Event Loops", score: 85 },
            { dimension_name: "Memory & Object Lifecycles", score: 80 },
            { dimension_name: "Type Hinting & Pydantic V2", score: 89 }
          ]
        }
      },
      {
        skill_name: "FastAPI & Microservices",
        evidence_tier: "ASSESSED",
        score: 80,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 92,
        evidence_count: 3,
        explanation: "Verified through microservice RESTful route implementation with dependency injection.",
        multidimensional_mastery: {
          evidence_coverage_pct: 82,
          weakest_dimension: "Middleware Latency Profiling",
          dimensions: [
            { dimension_name: "Route Handlers & DI", score: 86 },
            { dimension_name: "Validation Schemas", score: 90 },
            { dimension_name: "Background Tasks", score: 75 },
            { dimension_name: "OAuth2 & JWT Auth", score: 80 }
          ]
        }
      },
      {
        skill_name: "PostgreSQL",
        evidence_tier: "DEMONSTRATED",
        score: 75,
        proficiency_level: "L2",
        proficiency_label: "Intermediate",
        confidence: "MEDIUM",
        freshness_score: 88,
        evidence_count: 2,
        explanation: "Validated through B-tree indexing, foreign key constraints, and join query profiling.",
        multidimensional_mastery: {
          evidence_coverage_pct: 74,
          weakest_dimension: "Deadlock Detection & Isolation Levels",
          dimensions: [
            { dimension_name: "Relational Modeling", score: 82 },
            { dimension_name: "Index Optimization", score: 76 },
            { dimension_name: "Query Cost Analysis", score: 72 },
            { dimension_name: "Transactions & Locking", score: 66 }
          ]
        }
      },
      {
        skill_name: "Redis & Caching",
        evidence_tier: "ASSESSED",
        score: 78,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 90,
        evidence_count: 2,
        explanation: "Assessed in caching strategies, TTL invalidation, distributed locking, and pub/sub.",
        multidimensional_mastery: {
          evidence_coverage_pct: 78,
          weakest_dimension: "Redis Cluster Sharding",
          dimensions: [
            { dimension_name: "Key-Value & Data Structures", score: 84 },
            { dimension_name: "Cache-Aside Patterns", score: 80 },
            { dimension_name: "Distributed Locks (Redlock)", score: 74 },
            { dimension_name: "Memory Eviction Policies", score: 70 }
          ]
        }
      },
      {
        skill_name: "System Design",
        evidence_tier: "INFERRED",
        score: 62,
        proficiency_level: "L2",
        proficiency_label: "Developing",
        confidence: "LOW",
        freshness_score: 75,
        evidence_count: 1,
        explanation: "Partial evidence detected; architectural tier assessment required to elevate beyond baseline.",
        multidimensional_mastery: {
          evidence_coverage_pct: 55,
          weakest_dimension: "High-Throughput Partitioning",
          dimensions: [
            { dimension_name: "Microservice Boundaries", score: 68 },
            { dimension_name: "Database Partitioning", score: 55 },
            { dimension_name: "Resilience & Circuit Breaking", score: 58 },
            { dimension_name: "Idempotency & Deduplication", score: 64 }
          ]
        }
      }
    ],
    evidence: [
      { id: "ev-be-01", skill_name: "Python", evidence_type: "CODE_SUBMISSION", source: "Coding Evaluation Engine", source_span: "asyncio.gather(..., return_exceptions=True) with TaskGroup error boundary", source_group: "DIAGNOSTIC_LAB", status: "VERIFIED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-28T10:15:00Z" },
      { id: "ev-be-02", skill_name: "FastAPI", evidence_type: "PROJECT_REPO", source: "GitHub Repository Analysis", source_span: "FastAPI Dependency Injection with async session generator & Pydantic V2 validation", source_group: "CAPSTONE_PROJECT", status: "ASSESSED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-27T14:30:00Z" },
      { id: "ev-be-03", skill_name: "PostgreSQL", evidence_type: "CODE_SUBMISSION", source: "Database Diagnostic Studio", source_span: "EXPLAIN ANALYZE index scan verification on composite foreign keys", source_group: "DIAGNOSTIC_LAB", status: "DEMONSTRATED", confidence: "MEDIUM", freshness_state: "FRESH", observed_at: "2026-08-26T09:00:00Z" }
    ],
    timeline: [
      { id: "ev-be-t1", event_type: "CANONICAL_TWIN_ESTABLISHED", actor: "Career Intelligence Engine", created_at: "2026-08-30T10:00:00Z", event_data: { twin_version: "v2.0.0", target_role: "Backend Engineer" } }
    ]
  },
  "AI/ML Engineer": {
    targetRole: "AI/ML Engineer",
    readinessScore: 74,
    criticalGap: "Real-Time Vector Indexing & Latency",
    gapDesc: "HNSW graph search tuning, vector quantization, and GPU inference batching.",
    actionQuest: "Launch Vector Retrieval Sandbox",
    nextStep: "Benchmark Qdrant with HNSW in Python",
    skills: [
      {
        skill_name: "PyTorch & Deep Learning",
        evidence_tier: "VERIFIED",
        score: 82,
        proficiency_level: "L3",
        proficiency_label: "Proficient",
        confidence: "HIGH",
        freshness_score: 96,
        evidence_count: 4,
        explanation: "Tensor operations, backpropagation pipelines, custom loss functions, and DataLoader tuning.",
        multidimensional_mastery: {
          evidence_coverage_pct: 86,
          weakest_dimension: "Distributed Data Parallel (DDP)",
          dimensions: [
            { dimension_name: "Tensor Math & Autograd", score: 92 },
            { dimension_name: "Model Architecture (CNN/Transformer)", score: 85 },
            { dimension_name: "Loss Functions & Optimizers", score: 80 },
            { dimension_name: "DDP Multi-GPU Scaling", score: 72 }
          ]
        }
      },
      {
        skill_name: "Transformers & LLMs",
        evidence_tier: "ASSESSED",
        score: 79,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 94,
        evidence_count: 3,
        explanation: "Hugging Face pipelines, tokenization, LoRA fine-tuning, and KV-cache optimization.",
        multidimensional_mastery: {
          evidence_coverage_pct: 82,
          weakest_dimension: "Speculative Decoding Latency",
          dimensions: [
            { dimension_name: "Self-Attention Mechanics", score: 88 },
            { dimension_name: "HuggingFace Pipelines", score: 86 },
            { dimension_name: "Parameter-Efficient Fine-Tuning (PEFT)", score: 76 },
            { dimension_name: "Quantization (GGUF/AWQ)", score: 72 }
          ]
        }
      },
      {
        skill_name: "Vector DBs (Qdrant/Milvus)",
        evidence_tier: "DEMONSTRATED",
        score: 74,
        proficiency_level: "L2",
        proficiency_label: "Intermediate",
        confidence: "MEDIUM",
        freshness_score: 90,
        evidence_count: 2,
        explanation: "Cosine similarity search, dense embedding indexing, and metadata payload filtering.",
        multidimensional_mastery: {
          evidence_coverage_pct: 75,
          weakest_dimension: "HNSW ef_search Parameter Optimization",
          dimensions: [
            { dimension_name: "Embedding Ingestion", score: 84 },
            { dimension_name: "Payload Filtering", score: 80 },
            { dimension_name: "Index Graph Calibration", score: 68 },
            { dimension_name: "Hybrid Search (Dense + BM25)", score: 72 }
          ]
        }
      },
      {
        skill_name: "FastAPI & Model Serving",
        evidence_tier: "ASSESSED",
        score: 77,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 92,
        evidence_count: 3,
        explanation: "Async inference endpoint handlers, request queue batching, and Dockerized deployment.",
        multidimensional_mastery: {
          evidence_coverage_pct: 80,
          weakest_dimension: "Triton Inference Server Pipelines",
          dimensions: [
            { dimension_name: "Streaming SSE Responses", score: 86 },
            { dimension_name: "Async Request Batching", score: 80 },
            { dimension_name: "Docker GPU Containers", score: 74 },
            { dimension_name: "Latency Profiling", score: 70 }
          ]
        }
      }
    ],
    evidence: [
      { id: "ev-ai-01", skill_name: "PyTorch", evidence_type: "PROJECT_REPO", source: "GitHub Repository Analysis", source_span: "Fine-tuning Mistral-7B with QLoRA on domain dataset with eval loss < 1.15", source_group: "CAPSTONE_PROJECT", status: "VERIFIED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-30T11:00:00Z" },
      { id: "ev-ai-02", skill_name: "Vector DBs", evidence_type: "CODE_SUBMISSION", source: "Semantic Search Lab", source_span: "Qdrant HNSW indexing over 500K 768-dim embeddings with <12ms p99 latency", source_group: "DIAGNOSTIC_LAB", status: "DEMONSTRATED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-28T15:00:00Z" }
    ],
    timeline: [
      { id: "ev-ai-t1", event_type: "CANONICAL_TWIN_ESTABLISHED", actor: "Career Intelligence Engine", created_at: "2026-08-30T10:00:00Z", event_data: { twin_version: "v2.0.0", target_role: "AI/ML Engineer" } }
    ]
  },
  "DevOps / SRE": {
    targetRole: "DevOps / SRE",
    readinessScore: 71,
    criticalGap: "Multi-Cluster Service Mesh & mTLS",
    gapDesc: "Istio routing rules, distributed telemetry with OpenTelemetry, and automated canary rollouts.",
    actionQuest: "Launch Kubernetes Canary Lab",
    nextStep: "Configure ArgoCD & Prometheus Metrics",
    skills: [
      {
        skill_name: "Kubernetes & Containers",
        evidence_tier: "VERIFIED",
        score: 80,
        proficiency_level: "L3",
        proficiency_label: "Proficient",
        confidence: "HIGH",
        freshness_score: 95,
        evidence_count: 4,
        explanation: "Deployments, StatefulSets, ingress controllers, HPA, and resource quotas.",
        multidimensional_mastery: {
          evidence_coverage_pct: 84,
          weakest_dimension: "Custom Resource Definitions (CRDs)",
          dimensions: [
            { dimension_name: "Pod Scheduling & Affinity", score: 88 },
            { dimension_name: "ConfigMaps & Secrets", score: 90 },
            { dimension_name: "Ingress & Network Policies", score: 78 },
            { dimension_name: "CRDs & Operator Pattern", score: 68 }
          ]
        }
      },
      {
        skill_name: "Terraform & AWS Cloud",
        evidence_tier: "ASSESSED",
        score: 76,
        proficiency_level: "L3",
        proficiency_label: "Competent",
        confidence: "HIGH",
        freshness_score: 91,
        evidence_count: 3,
        explanation: "IaC state management, VPC peering, IAM least-privilege, and EKS provisioning.",
        multidimensional_mastery: {
          evidence_coverage_pct: 78,
          weakest_dimension: "Remote State Locking with DynamoDB",
          dimensions: [
            { dimension_name: "VPC & Subnet Architecture", score: 84 },
            { dimension_name: "IAM Policy Definitions", score: 82 },
            { dimension_name: "Terraform Modules", score: 76 },
            { dimension_name: "State Invariance & Drift", score: 70 }
          ]
        }
      },
      {
        skill_name: "CI/CD & GitHub Actions",
        evidence_tier: "VERIFIED",
        score: 85,
        proficiency_level: "L4",
        proficiency_label: "Advanced",
        confidence: "HIGH",
        freshness_score: 98,
        evidence_count: 5,
        explanation: "Matrix builds, secret masking, artifact caching, and zero-downtime blue/green deployment.",
        multidimensional_mastery: {
          evidence_coverage_pct: 90,
          weakest_dimension: "Ephemeral Self-Hosted Runners",
          dimensions: [
            { dimension_name: "Workflow Trigger Logic", score: 94 },
            { dimension_name: "Artifact & Docker Caching", score: 88 },
            { dimension_name: "Environment Protection Rules", score: 84 },
            { dimension_name: "Runner Optimization", score: 80 }
          ]
        }
      }
    ],
    evidence: [
      { id: "ev-ops-01", skill_name: "Kubernetes", evidence_type: "PROJECT_REPO", source: "Infrastructure Repository", source_span: "Helm chart deployment with Horizontal Pod Autoscaler and automated healthchecks", source_group: "CAPSTONE_PROJECT", status: "VERIFIED", confidence: "HIGH", freshness_state: "FRESH", observed_at: "2026-08-29T16:00:00Z" }
    ],
    timeline: [
      { id: "ev-ops-t1", event_type: "CANONICAL_TWIN_ESTABLISHED", actor: "Career Intelligence Engine", created_at: "2026-08-30T10:00:00Z", event_data: { twin_version: "v2.0.0", target_role: "DevOps / SRE" } }
    ]
  }
};

export const CareerTwinPage: React.FC = () => {
  const [targetRole, setTargetRole] = useState<string>("Full Stack Engineer");
  const [twin, setTwin] = useState<CareerTwinSnapshot | null>(null);
  const [selectedSkill, setSelectedSkill] = useState<SkillEvidenceItem | null>(null);
  const [activeTab, setActiveTab] = useState<"KNOW" | "PROVE" | "MISSING" | "TRAJECTORY" | "FORECAST" | "TRANSFERS" | "INTERVIEW" | "CHANGES">("FORECAST");
  const [loading, setLoading] = useState<boolean>(true);

  const currentProfile = ROLE_TWIN_PROFILES[targetRole] || ROLE_TWIN_PROFILES["Full Stack Engineer"];
  const [evidenceList, setEvidenceList] = useState<any[]>(currentProfile.evidence);
  const [trajectoryList, setTrajectoryList] = useState<any[]>(currentProfile.timeline);

  // Trajectory Simulation State
  const [forecastWeeklyHours, setForecastWeeklyHours] = useState<number>(10);
  const [activeScenario, setActiveScenario] = useState<"MOST_LIKELY" | "OPTIMISTIC" | "RISK">("MOST_LIKELY");
  const [selectedHorizon, setSelectedHorizon] = useState<number>(3);

  const fetchTwinData = async (roleOverride?: string) => {
    setLoading(true);
    const role = roleOverride || targetRole;
    try {
      const [snapshot, evidenceData, trajectoryData] = await Promise.all([
        careerIntelligenceApi.getCareerDigitalTwin().catch(() => null),
        careerIntelligenceApi.getTwinEvidence().catch(() => null),
        careerIntelligenceApi.getTwinTrajectory().catch(() => null)
      ]);
      const prof = ROLE_TWIN_PROFILES[role] || ROLE_TWIN_PROFILES["Full Stack Engineer"];
      setTwin(snapshot);
      setEvidenceList(prof.evidence);
      setTrajectoryList(prof.timeline);
      
      const skills = prof.skills;
      if (skills.length > 0) {
        setSelectedSkill(skills[0]);
      }
    } catch (err) {
      console.error("Failed to load Career Digital Twin:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTwinData(targetRole);
  }, [targetRole]);

  const handleRoleSwitch = (newRole: string) => {
    setTargetRole(newRole);
    const prof = ROLE_TWIN_PROFILES[newRole] || ROLE_TWIN_PROFILES["Full Stack Engineer"];
    setEvidenceList(prof.evidence);
    setTrajectoryList(prof.timeline);
    if (prof.skills.length > 0) {
      setSelectedSkill(prof.skills[0]);
    }
  };

  const tierBadgeColors: Record<string, string> = {
    VERIFIED: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    ASSESSED: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    DEMONSTRATED: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    INFERRED: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    CLAIMED: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  };

  // Safe data accessors
  const effectiveSkills = currentProfile.skills;
  const verifiedCount = effectiveSkills.filter((s) => s.evidence_tier === "VERIFIED" || s.evidence_tier === "ASSESSED").length;
  const effectiveEvidence = evidenceList;
  const effectiveTimeline = trajectoryList;

  // Real-time Trajectory Forecast Simulator Calculation
  const currentReadiness = currentProfile.readinessScore;
  const baseScore = currentReadiness;
  const maxPossibleGain = Math.max(0, 96.0 - baseScore);
  const effortFactor = Math.max(0.3, Math.min(2.5, forecastWeeklyHours / 8.0));
  const historicalVelocity = 2.5;
  const kRate = 0.05 * (historicalVelocity / 2.5) * effortFactor;

  const calculateHorizon = (h: number) => {
    const expectedGain = maxPossibleGain * (1.0 - Math.exp(-kRate * h));
    const mostLikely = Math.min(98, Math.round(baseScore + expectedGain));
    const optimistic = Math.min(100, Math.round(baseScore + expectedGain * 1.25 + 2));
    const risk = Math.max(baseScore - 3, Math.round(baseScore + expectedGain * 0.45 - 0.5 * h));
    const effortHours = Math.round(h * 4.33 * forecastWeeklyHours);

    const getProficiency = (score: number) => {
      if (score >= 85) return { title: "L5 / Senior Software Engineer", market: "Top 8% Tier-1 MNC Ready", tier: "High Autonomy" };
      if (score >= 70) return { title: "L4 / Mid-Level Software Engineer", market: "Competitive for Tech Mid-Tier & Unicorns", tier: "Core Contributor" };
      if (score >= 55) return { title: "L3 / Associate Software Engineer", market: "Entry-Level Strong Contender", tier: "Supervised Practitioner" };
      return { title: "Foundational Apprentice", market: "Needs Acceleration Sprints", tier: "Developing" };
    };

    const getSalary = (score: number) => {
      const minSalary = Math.round(75 + Math.max(0, score - 45) * 2.2);
      const maxSalary = Math.round(95 + Math.max(0, score - 45) * 2.8);
      return `$${minSalary}k – $${maxSalary}k`;
    };

    const unlocks = h === 3 ? [
      "Idempotent message queues & cache-aside Redis invalidation",
      "Subarray sum & sliding window algorithmic optimization",
      "Verified evidence tier elevation via proctored sandbox"
    ] : h === 6 ? [
      "Database connection pooling & multi-shard horizontal scaling",
      "Asynchronous event-driven microservices architecture",
      "Production repository deployment with >85% AST test coverage"
    ] : [
      "Multi-region active-active distributed consensus",
      "Zero-downtime database schema migration pipelines",
      "Staff/Lead level system design interview clearance"
    ];

    return {
      horizonMonths: h,
      effortHours,
      mostLikely: {
        score: mostLikely,
        scoreRange: `${mostLikely - 2}–${mostLikely + 2}`,
        ...getProficiency(mostLikely),
        salary: getSalary(mostLikely)
      },
      optimistic: {
        score: optimistic,
        scoreRange: `${optimistic - 1}–${Math.min(100, optimistic + 2)}`,
        ...getProficiency(optimistic),
        salary: getSalary(optimistic)
      },
      risk: {
        score: risk,
        scoreRange: `${Math.max(0, risk - 3)}–${risk + 2}`,
        ...getProficiency(risk),
        salary: getSalary(risk)
      },
      unlocks,
      delta: Math.max(1, mostLikely - baseScore)
    };
  };

  const calculatedProjections = [3, 6, 12].map(calculateHorizon);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-16">
      {/* Top Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
              Career Digital Twin
            </h2>
            <span className="px-3 py-0.5 text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-full">
              {twin?.snapshot_metadata?.twin_version || "v2.0.0"}
            </span>
          </div>
          <p className="text-slate-400 mt-2 text-sm">
            Canonical Representation of Candidate Competency, Grounded Evidence Graph, and Role Alignment.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Target Role & Career Track Switcher */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-700/80 rounded-xl p-1.5 pl-3 shadow-inner">
            <label className="text-xs text-slate-400 font-medium whitespace-nowrap flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-indigo-400" />
              <span>Target Track:</span>
            </label>
            <select
              value={targetRole}
              onChange={(e) => handleRoleSwitch(e.target.value)}
              className="bg-slate-950 border border-slate-700/80 text-white font-semibold text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-indigo-500 focus:outline-none cursor-pointer hover:border-slate-600 transition"
            >
              <option value="Full Stack Engineer">Full Stack Engineer</option>
              <option value="Backend Engineer">Backend Engineer</option>
              <option value="AI/ML Engineer">AI/ML Engineer</option>
              <option value="DevOps / SRE">DevOps / SRE</option>
            </select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchTwinData(targetRole)}
            className="border-white/10 hover:bg-white/5 text-slate-300 rounded-xl h-9"
          >
            <RefreshCw className={cn("w-3.5 h-3.5 mr-1.5", loading && "animate-spin")} />
            Sync Twin
          </Button>
        </div>
      </header>

      {/* 5 Central Pillars: Interactive Quick-Action Diagnostic Hub */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {/* 1. WHERE AM I */}
        <div 
          onClick={() => setActiveTab("MISSING")}
          className="glass-panel p-4 rounded-2xl border border-indigo-500/20 bg-indigo-950/20 hover:border-indigo-500/50 hover:bg-indigo-950/40 transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-indigo-500/10"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">1. Where Am I?</p>
            <ChevronRight className="w-3.5 h-3.5 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-2xl font-black text-white mt-1">
            {currentProfile.readinessScore}
            <span className="text-xs font-normal text-slate-400">/100</span>
          </h4>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            <p className="text-[11px] text-slate-300 font-medium truncate">
              {currentProfile.targetRole}
            </p>
          </div>
          <p className="text-[10px] text-slate-400 mt-2 flex items-center gap-1">
            <span>Readiness Diagnostic</span>
            <span className="text-indigo-400 group-hover:translate-x-0.5 transition-transform">→</span>
          </p>
        </div>

        {/* 2. WHAT DO I KNOW */}
        <div 
          onClick={() => setActiveTab("KNOW")}
          className="glass-panel p-4 rounded-2xl border border-emerald-500/20 bg-emerald-950/20 hover:border-emerald-500/50 hover:bg-emerald-950/40 transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-emerald-500/10"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">2. What Do I Know?</p>
            <ChevronRight className="w-3.5 h-3.5 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-2xl font-black text-emerald-400 mt-1">
            {effectiveSkills.length}
            <span className="text-xs font-normal text-slate-400"> Skills</span>
          </h4>
          <p className="text-[11px] text-slate-300 font-medium mt-1">
            {verifiedCount} Verified / Assessed
          </p>
          <p className="text-[10px] text-slate-400 mt-2 flex items-center gap-1">
            <span>Inspect Taxonomy</span>
            <span className="text-emerald-400 group-hover:translate-x-0.5 transition-transform">→</span>
          </p>
        </div>

        {/* 3. WHAT CAN I PROVE */}
        <div 
          onClick={() => setActiveTab("PROVE")}
          className="glass-panel p-4 rounded-2xl border border-blue-500/20 bg-blue-950/20 hover:border-blue-500/50 hover:bg-blue-950/40 transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-blue-500/10"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">3. What Can I Prove?</p>
            <ChevronRight className="w-3.5 h-3.5 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-2xl font-black text-blue-400 mt-1">
            {effectiveEvidence.length}
            <span className="text-xs font-normal text-slate-400"> Proofs</span>
          </h4>
          <p className="text-[11px] text-slate-300 font-medium mt-1">
            {effectiveEvidence.length} Projects & Labs Verified
          </p>
          <p className="text-[10px] text-slate-400 mt-2 flex items-center gap-1">
            <span>Audit Lineage</span>
            <span className="text-blue-400 group-hover:translate-x-0.5 transition-transform">→</span>
          </p>
        </div>

        {/* 4. WHAT AM I MISSING */}
        <div 
          onClick={() => setActiveTab("MISSING")}
          className="glass-panel p-4 rounded-2xl border border-amber-500/20 bg-amber-950/20 hover:border-amber-500/50 hover:bg-amber-950/40 transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-amber-500/10"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] uppercase font-bold text-amber-400 tracking-wider">4. What Am I Missing?</p>
            <ChevronRight className="w-3.5 h-3.5 text-amber-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-2xl font-black text-amber-400 mt-1">
            1
            <span className="text-xs font-normal text-slate-400"> Critical Gap</span>
          </h4>
          <p className="text-[11px] text-amber-300 font-medium mt-1 truncate">
            {currentProfile.criticalGap}
          </p>
          <p className="text-[10px] text-slate-400 mt-2 flex items-center gap-1">
            <span>Gap Breakdown</span>
            <span className="text-amber-400 group-hover:translate-x-0.5 transition-transform">→</span>
          </p>
        </div>

        {/* 5. WHAT NEXT */}
        <div 
          onClick={() => window.location.href = '/app/career-os'}
          className="glass-panel p-4 rounded-2xl border border-cyan-500/20 bg-cyan-950/20 hover:border-cyan-500/50 hover:bg-cyan-950/40 transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-cyan-500/10"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">5. What Next?</p>
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 group-hover:rotate-12 transition-transform" />
          </div>
          <h4 className="text-sm font-bold text-cyan-300 mt-1 truncate">
            {currentProfile.actionQuest}
          </h4>
          <p className="text-[11px] text-slate-300 font-medium mt-1 truncate">
            {currentProfile.nextStep}
          </p>
          <p className="text-[10px] text-cyan-400 mt-2 flex items-center gap-1 font-semibold">
            <span>Launch Quest</span>
            <span className="group-hover:translate-x-0.5 transition-transform">⚡</span>
          </p>
        </div>
      </div>

      {/* Navigation Tabs with live synced counts */}
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveTab("KNOW")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "KNOW"
              ? "bg-indigo-600/30 border-indigo-500/50 text-white shadow-lg shadow-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <Brain className="w-3.5 h-3.5" />
          Skills ({effectiveSkills.length})
        </button>
        <button
          onClick={() => setActiveTab("PROVE")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "PROVE"
              ? "bg-blue-600/30 border-blue-500/50 text-white shadow-lg shadow-blue-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          Evidence Atoms ({effectiveEvidence.length})
        </button>
        <button
          onClick={() => setActiveTab("MISSING")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "MISSING"
              ? "bg-amber-600/30 border-amber-500/50 text-white shadow-lg shadow-amber-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <Target className="w-3.5 h-3.5" />
          Role Alignment
        </button>
        <button
          onClick={() => setActiveTab("FORECAST")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "FORECAST"
              ? "bg-purple-600/30 border-purple-500/50 text-white shadow-lg shadow-purple-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          Trajectory Forecast (3/6/12M)
        </button>
        <button
          onClick={() => setActiveTab("TRANSFERS")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "TRANSFERS"
              ? "bg-cyan-600/30 border-cyan-500/50 text-white shadow-lg shadow-cyan-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <GitBranch className="w-3.5 h-3.5" />
          Skill Transfer Bridges
        </button>
        <button
          onClick={() => setActiveTab("INTERVIEW")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "INTERVIEW"
              ? "bg-rose-600/30 border-rose-500/50 text-white shadow-lg shadow-rose-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <Layers className="w-3.5 h-3.5" />
          Interview Memory
        </button>
        <button
          onClick={() => setActiveTab("TRAJECTORY")}
          className={cn(
            "px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border flex items-center gap-1.5",
            activeTab === "TRAJECTORY"
              ? "bg-emerald-600/30 border-emerald-500/50 text-white shadow-lg shadow-emerald-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5"
          )}
        >
          <Activity className="w-3.5 h-3.5" />
          Events Timeline ({effectiveTimeline.length})
        </button>
      </div>


      {/* TAB 1: COMPETENCY & SKILL GRAPH */}
      {activeTab === "KNOW" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6 space-y-3">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
              Canonical Skills Inventory ({targetRole})
            </h3>
            {effectiveSkills.map((skill, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedSkill(skill)}
                className={cn(
                  "p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between",
                  selectedSkill?.skill_name === skill.skill_name
                    ? "bg-slate-900 border-indigo-500/50 shadow-lg shadow-indigo-500/10"
                    : "bg-slate-900/50 border-white/5 hover:border-white/20 hover:bg-slate-900/80"
                )}
              >
                <div>
                  <div className="flex items-center gap-2.5">
                    <h4 className="text-sm font-bold text-white">{skill.skill_name}</h4>
                    <span className={cn("px-2 py-0.5 rounded-full text-[10px] font-bold border", tierBadgeColors[skill.evidence_tier])}>
                      {skill.evidence_tier}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Proficiency: <strong className="text-indigo-300">{skill.proficiency_label || "Intermediate"}</strong>
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-base font-mono font-bold text-white">{skill.score}/100</div>
                  <div className="text-[10px] text-slate-400">{Math.round(skill.freshness_score)}% Freshness</div>
                </div>
              </div>
            ))}
          </div>

          {/* Selected Skill Detail Inspector */}
          <div className="lg:col-span-6 space-y-4">
            {/* Active Evidence Conflict Alert if detected on candidate */}
            {twin?.evidence_integrity?.active_conflicts_count ? (
              <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30">
                <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">
                  <AlertTriangle className="w-4 h-4" /> Evidence Inconsistency Detected ({twin.evidence_integrity.active_conflicts_count})
                </div>
                {twin.evidence_integrity.conflicts.map((conf: any, cidx: number) => (
                  <div key={cidx} className="p-3 rounded-xl bg-slate-900/80 border border-amber-500/20 text-xs mt-2">
                    <p className="font-bold text-white">{conf.what_conflicts}</p>
                    <p className="text-slate-400 mt-1 text-[11px]">{conf.why_it_matters}</p>
                    <div className="mt-2 text-emerald-400 text-[11px] font-mono bg-emerald-950/30 p-2 rounded-lg border border-emerald-500/20">
                      💡 <strong>Resolution:</strong> {conf.resolution_steps}
                    </div>
                  </div>
                ))}
              </div>
            ) : null}

            {selectedSkill ? (
              <Card className="glass-panel p-6 rounded-3xl sticky top-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
                      Skill Intelligence Inspector
                    </span>
                    <h3 className="text-2xl font-bold text-white mt-2">{selectedSkill.skill_name}</h3>
                  </div>
                  <span className={cn("px-3 py-1 rounded-full text-xs font-bold border", tierBadgeColors[selectedSkill.evidence_tier])}>
                    {selectedSkill.evidence_tier}
                  </span>
                </div>

                <div className="space-y-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
                    <p className="font-semibold text-slate-400 uppercase text-[10px]">Evidence Reasoning</p>
                    <p className="text-slate-200 mt-1 leading-relaxed">{selectedSkill.explanation}</p>
                  </div>

                  {/* Multidimensional Mastery Breakdown */}
                  {selectedSkill.multidimensional_mastery && (
                    <div className="p-3.5 rounded-xl bg-slate-900/80 border border-indigo-500/20">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-indigo-300 uppercase text-[10px]">Multidimensional Mastery Decomposition</span>
                        <span className="text-[10px] text-emerald-400 font-mono font-bold">
                          {selectedSkill.multidimensional_mastery.evidence_coverage_pct}% Evidence Coverage
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        {selectedSkill.multidimensional_mastery.dimensions?.map((dim: any, didx: number) => (
                          <div key={didx} className="p-2 rounded-lg bg-black/40 border border-white/5 flex justify-between items-center">
                            <span className="text-[11px] text-slate-300 truncate">{dim.dimension_name}</span>
                            <span className={cn(
                              "text-[10px] font-mono font-bold ml-1 shrink-0",
                              dim.score >= 80 ? "text-emerald-400" : dim.score >= 65 ? "text-cyan-400" : "text-amber-400"
                            )}>
                              {dim.score}
                            </span>
                          </div>
                        ))}
                      </div>
                      {selectedSkill.multidimensional_mastery.weakest_dimension && (
                        <p className="text-[10px] text-amber-400 mt-2.5">
                          ⚠️ Primary focus area: <strong>{selectedSkill.multidimensional_mastery.weakest_dimension}</strong>
                        </p>
                      )}
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                      <p className="text-slate-400 text-[10px] uppercase font-semibold">Confidence Tier</p>
                      <p className="text-sm font-bold text-emerald-400 mt-0.5">{selectedSkill.confidence}</p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                      <p className="text-slate-400 text-[10px] uppercase font-semibold">Freshness Score</p>
                      <p className="text-sm font-bold text-indigo-400 mt-0.5">{Math.round(selectedSkill.freshness_score)}%</p>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/20">
                    <p className="font-semibold text-indigo-300 uppercase text-[10px]">Next Recommended Action</p>
                    <p className="text-indigo-200 mt-1">
                      Complete a controlled sandbox challenge or update project documentation to elevate this competency to ASSESSED/VERIFIED.
                    </p>
                  </div>
                </div>
              </Card>
            ) : (
              <div className="p-12 text-center text-slate-500">Select a skill to inspect provenance</div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: EVIDENCE ATOMS */}
      {activeTab === "PROVE" && (
        <Card className="glass-panel p-6 rounded-3xl">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-blue-400" /> Granular Evidence Provenance
          </h3>
          <div className="space-y-3">
            {evidenceList.map((ev, i) => (
              <div key={i} className="p-4 rounded-2xl bg-slate-900/60 border border-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white">{ev.skill_name}</h4>
                    <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[10px] uppercase font-bold text-slate-300">
                      {ev.evidence_type}
                    </span>
                    <span className={cn(
                      "px-2 py-0.5 rounded-md text-[10px] font-bold uppercase",
                      ev.freshness_state === "FRESH" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
                    )}>
                      {ev.freshness_state}
                    </span>
                  </div>
                  {ev.source_span && (
                    <p className="text-xs text-slate-400 mt-1.5 font-mono italic bg-black/30 px-3 py-1.5 rounded-lg border border-white/5">
                      "{ev.source_span}"
                    </p>
                  )}
                  <p className="text-[11px] text-slate-500 mt-1">
                    Source: <strong className="text-slate-400">{ev.source}</strong> • Observed: {ev.observed_at ? new Date(ev.observed_at).toLocaleDateString() : "Recent"}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs font-semibold text-emerald-400">{ev.confidence} Confidence</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* TAB 3: ROLE ALIGNMENT & UNKNOWNS */}
      {activeTab === "MISSING" && (
        <Card className="glass-panel p-6 rounded-3xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-amber-400" /> Target Role Competency Alignment
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Target: <strong className="text-white">{currentProfile.targetRole}</strong> • Alignment: <strong className="text-emerald-400">{currentProfile.readinessScore}%</strong>
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {/* MATCHED */}
            <div>
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Matched Competencies ({effectiveSkills.filter(s => s.score >= 75).length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {effectiveSkills.filter(s => s.score >= 75).map((m, i) => (
                  <div key={i} className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-white">{m.skill_name}</span>
                      <span className="text-[10px] font-bold text-emerald-400">Score {m.score}/100 • {m.proficiency_label}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{m.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* GAPS */}
            <div>
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 mt-4">
                <AlertTriangle className="w-3.5 h-3.5" /> Priority Growth Bottleneck (1 Critical)
              </h4>
              <div className="grid grid-cols-1 gap-3">
                <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-white">{currentProfile.criticalGap}</span>
                    <span className="text-xs font-bold text-amber-400 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/30">Primary Deficit</span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1.5">{currentProfile.gapDesc}</p>
                  <div className="mt-3 flex items-center justify-between pt-2 border-t border-white/5">
                    <span className="text-[11px] text-slate-400">Recommended Action: <strong className="text-cyan-300">{currentProfile.actionQuest}</strong></span>
                    <button onClick={() => window.location.href = '/app/career-os'} className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                      <span>Launch In Career OS</span>
                      <span>→</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* UNKNOWNS - INSUFFICIENT EVIDENCE */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 mt-4">
                <HelpCircle className="w-3.5 h-3.5 text-slate-400" /> Developing Competencies (Next Horizons)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {effectiveSkills.filter(s => s.score < 75).map((u, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-300">{u.skill_name}</span>
                      <span className="text-[10px] font-bold text-slate-400">Current Score {u.score}/100</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{u.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* CAREER DECISION EXPLAINABILITY ("WHY THIS?") */}
            <div className="mt-8 p-5 rounded-2xl bg-indigo-950/20 border border-indigo-500/30">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Decision Explainability Engine
                  </span>
                  <span className="text-xs text-slate-400 font-mono">v16.0.0-rc1</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  HIGH CONFIDENCE
                </span>
              </div>

              <h4 className="text-base font-bold text-white mb-1">
                Recommendation: Complete {twin?.role_alignment.role_name || "Backend"} Architecture Assessment
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                <strong>Why this recommendation?</strong> Demonstrating end-to-end architecture elevates your Twin from INFERRED to ASSESSED tier, directly addressing the primary material constraint for {twin?.role_alignment.role_name || "Backend Engineer"} hiring bars.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Expected Impact Range</p>
                  <p className="text-sm font-bold text-emerald-400 mt-0.5">+6 to +11 pts</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Calibrated on 9D Readiness</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Estimated Effort Range</p>
                  <p className="text-sm font-bold text-indigo-400 mt-0.5">45–60 mins</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Proctored lab mode</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Market Signal</p>
                  <p className="text-sm font-bold text-amber-400 mt-0.5">High Demand (P1)</p>
                  <p className="text-slate-500 text-[10px] mt-0.5">Role requirement weight: 85%</p>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-black/40 border border-white/5 text-[11px] text-slate-400 space-y-1">
                <p>💡 <strong>Key Assumption:</strong> Candidate completes challenge under standard AST runtime limits without external code injection.</p>
                <p>🔄 <strong>Alternative:</strong> Submit verified GitHub repository with Dockerized microservices and automated tests (15–20h effort).</p>
                <p>⚠️ <strong>Limitation:</strong> Projected readiness is an empirical estimate calibrated against benchmark hiring bars, not a guaranteed employment offer.</p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* TAB 4: CAREER TRAJECTORY FORECAST */}
      {activeTab === "FORECAST" && (
        <Card className="glass-panel p-6 rounded-3xl space-y-6">
          {/* Header with Simulator Controls */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-white/10 pb-5">
            <div>
              <div className="flex items-center gap-2 text-xs font-mono text-purple-400 uppercase tracking-wide">
                <TrendingUp className="w-4 h-4" />
                Empirical Multi-Horizon Forecast Engine
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
                Career Trajectory Multi-Horizon Forecasting
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Target Track: <strong className="text-white">{twin?.candidate?.target_role || "Backend Engineer"}</strong> • Baseline: <strong className="text-indigo-400">{currentReadiness}/100 CRI</strong> • Velocity: <strong className="text-emerald-400">0.35 pts/hr</strong>
              </p>
            </div>

            {/* Interactive Simulation Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-xl p-1 shadow-inner">
                <span className="text-[11px] font-mono text-slate-400 px-2 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-purple-400" />
                  Effort:
                </span>
                {[5, 10, 20, 30].map((hrs) => (
                  <button
                    key={hrs}
                    onClick={() => setForecastWeeklyHours(hrs)}
                    className={cn(
                      "px-2.5 py-1 rounded-lg text-xs font-semibold font-mono transition cursor-pointer",
                      forecastWeeklyHours === hrs
                        ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                        : "text-slate-400 hover:text-white hover:bg-slate-800"
                    )}
                  >
                    {hrs}h/wk
                  </button>
                ))}
              </div>

              {/* Scenario Toggle */}
              <div className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 rounded-xl p-1 shadow-inner">
                <button
                  onClick={() => setActiveScenario("MOST_LIKELY")}
                  className={cn(
                    "px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1",
                    activeScenario === "MOST_LIKELY"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                      : "text-slate-400 hover:text-white"
                  )}
                >
                  <span>🎯 Most Likely</span>
                </button>
                <button
                  onClick={() => setActiveScenario("OPTIMISTIC")}
                  className={cn(
                    "px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1",
                    activeScenario === "OPTIMISTIC"
                      ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/20"
                      : "text-slate-400 hover:text-white"
                  )}
                >
                  <span>🚀 Optimistic</span>
                </button>
                <button
                  onClick={() => setActiveScenario("RISK")}
                  className={cn(
                    "px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1",
                    activeScenario === "RISK"
                      ? "bg-rose-600 text-white shadow-md shadow-rose-600/20"
                      : "text-slate-400 hover:text-white"
                  )}
                >
                  <span>🛡️ Risk-Adjusted</span>
                </button>
              </div>
            </div>
          </div>

          {/* 3 Multi-Horizon Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {calculatedProjections.map((proj) => {
              const scenarioData = activeScenario === "MOST_LIKELY" 
                ? proj.mostLikely 
                : activeScenario === "OPTIMISTIC" 
                  ? proj.optimistic 
                  : proj.risk;

              const progressPct = Math.min(100, Math.round((scenarioData.score / 100) * 100));

              return (
                <div 
                  key={proj.horizonMonths}
                  className="p-5 rounded-2xl bg-slate-900/80 border border-purple-500/20 hover:border-purple-500/50 hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-200 flex flex-col justify-between space-y-4 relative group"
                >
                  <div className="space-y-3.5">
                    {/* Horizon Header */}
                    <div className="flex justify-between items-center border-b border-white/10 pb-2.5">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold font-mono text-purple-300 uppercase tracking-wide bg-purple-950/60 border border-purple-800/40 px-2 py-0.5 rounded-md">
                          {proj.horizonMonths} Months Horizon
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-emerald-400 font-mono font-bold bg-emerald-950/40 border border-emerald-800/30 px-2 py-0.5 rounded-md">
                          +{proj.delta} CRI
                        </span>
                        <span className="text-[11px] text-slate-300 font-mono bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          {proj.effortHours}h Effort
                        </span>
                      </div>
                    </div>

                    {/* Visual Progress Bar */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between items-center text-[10px] font-mono">
                        <span className="text-slate-400">Baseline: <strong className="text-slate-200">{baseScore}</strong></span>
                        <span className="text-purple-300 font-bold">Target: {scenarioData.scoreRange}</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden border border-white/5">
                        <div 
                          className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 transition-all duration-500 rounded-full"
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>
                    </div>

                    {/* Active Scenario Box */}
                    <div className={cn(
                      "p-3.5 rounded-xl border transition-all",
                      activeScenario === "MOST_LIKELY" && "bg-indigo-950/30 border-indigo-500/30",
                      activeScenario === "OPTIMISTIC" && "bg-emerald-950/30 border-emerald-500/30",
                      activeScenario === "RISK" && "bg-rose-950/30 border-rose-500/30"
                    )}>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {activeScenario === "MOST_LIKELY" && "🎯 Most Likely"}
                          {activeScenario === "OPTIMISTIC" && "🚀 Optimistic Projection"}
                          {activeScenario === "RISK" && "🛡️ Risk-Adjusted Floor"}
                        </span>
                        <span className="text-sm font-mono font-bold text-cyan-300">
                          {scenarioData.scoreRange} CRI
                        </span>
                      </div>
                      <p className="text-xs text-white font-semibold mt-1">
                        {scenarioData.title}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {scenarioData.market}
                      </p>
                    </div>

                    {/* Compensation & Market Value */}
                    <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center justify-between">
                      <div>
                        <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                          <DollarSign className="w-3 h-3 text-emerald-400" />
                          Est. Market Package
                        </p>
                        <p className="text-xs font-mono font-bold text-emerald-400 mt-0.5">
                          {scenarioData.salary}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Hiring Tier</p>
                        <span className="text-[11px] text-indigo-300 font-medium">
                          {scenarioData.tier}
                        </span>
                      </div>
                    </div>

                    {/* Capability Breakthrough Unlocks */}
                    <div className="space-y-1.5 pt-1">
                      <p className="text-[10px] uppercase font-bold text-purple-300 tracking-wider flex items-center gap-1">
                        <Award className="w-3 h-3 text-purple-400" />
                        Milestone Unlocks
                      </p>
                      <ul className="space-y-1 text-[11px] text-slate-300">
                        {proj.unlocks.map((unlock, uidx) => (
                          <li key={uidx} className="flex items-start gap-1.5">
                            <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                            <span className="leading-tight">{unlock}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Action CTA */}
                  <div className="pt-3 border-t border-white/10">
                    <button
                      onClick={() => window.location.href = '/app/career-os'}
                      className="w-full flex items-center justify-center gap-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold py-2.5 rounded-xl transition shadow-md shadow-purple-600/20 cursor-pointer"
                    >
                      <Zap className="w-3.5 h-3.5 text-purple-200" />
                      <span>Activate {proj.horizonMonths}M Action Plan</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Scientific Transparency & Evidence Decay Defense */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <p className="font-bold text-indigo-300 flex items-center gap-1">
                <span>📐 Diminishing Returns Curve</span>
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Gain velocity scales as <code className="text-indigo-200">1 - exp(-k * t)</code>. Marginal readiness points require higher algorithmic rigor as score approaches 96/100.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <p className="font-bold text-amber-300 flex items-center gap-1">
                <span>🛡️ Evidence Decay Defense</span>
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Skills unbacked by fresh code commits decay at ~4%/month. Complete 1 proctored lab every 14 days to lock in gains and prevent floor collapse.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
              <p className="font-bold text-emerald-300 flex items-center gap-1">
                <span>⚡ Calibrated Velocity (0.35 pts/hr)</span>
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Empirically calibrated from AST complexity benchmarks and controlled MNC interview studios, avoiding fabricated timeline guarantees.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* TAB 5: SKILL TRANSFER INTELLIGENCE */}
      {activeTab === "TRANSFERS" && (
        <Card className="glass-panel p-6 rounded-3xl space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-cyan-400" /> Skill Transfer Intelligence & Minimal Learning Bridges
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Evaluates role transitions requiring the smallest realistic bridge from your verified foundational skills.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {twin?.skill_transfer_bridges?.map((bridge: any, bidx: number) => (
              <div key={bidx} className="p-5 rounded-2xl bg-slate-900/60 border border-cyan-500/20 space-y-3">
                <div className="flex justify-between items-center border-b border-white/5 pb-2">
                  <h4 className="text-sm font-bold text-white">{bridge.target_role}</h4>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    {bridge.transferability_percentage}% Match
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{bridge.explanations?.why_this_transition}</p>
                
                <div className="space-y-1.5 text-xs">
                  <p className="text-slate-400 text-[11px]">
                    ✅ <strong>Already Transfers:</strong> {bridge.transferable_skills?.map((s: any) => s.skill_name).join(", ")}
                  </p>
                  <p className="text-amber-400 text-[11px]">
                    ⚡ <strong>Missing Skills to Learn:</strong> {bridge.missing_critical_skills?.map((s: any) => s.skill_name).join(", ")}
                  </p>
                  <p className="text-slate-400 text-[11px]">
                    ⏱️ Estimated Bridge Effort: <strong>{bridge.estimated_bridge_weeks} weeks</strong> ({bridge.bridge_difficulty})
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* TAB 6: INTERVIEW MEMORY */}
      {activeTab === "INTERVIEW" && (
        <Card className="glass-panel p-6 rounded-3xl space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-rose-400" /> Cross-Session Interview Memory & Competency Progress
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Tracks performance evolution across historical mock sessions to dynamically adapt interview difficulty.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/5">
              <p className="text-[10px] uppercase font-bold text-slate-400">Total Completed Interviews</p>
              <h4 className="text-2xl font-bold text-white mt-1">
                {twin?.interview_memory?.total_interviews_completed || 0}
              </h4>
            </div>
            <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/20">
              <p className="text-[10px] uppercase font-bold text-emerald-400">Mastered Competencies</p>
              <p className="text-xs font-bold text-white mt-1">
                {twin?.interview_memory?.mastered_competencies?.join(", ") || "None yet"}
              </p>
            </div>
            <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/20">
              <p className="text-[10px] uppercase font-bold text-amber-400">Active Focus Areas</p>
              <p className="text-xs font-bold text-white mt-1">
                {twin?.interview_memory?.underperforming_competencies?.join(", ") || "None"}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* TAB 7: CAREER TRAJECTORY TIMELINE */}
      {activeTab === "TRAJECTORY" && (
        <Card className="glass-panel p-6 rounded-3xl">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" /> Progression Trajectory Timeline
          </h3>
          <div className="space-y-4 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
            {trajectoryList.map((item, idx) => (
              <div key={idx} className="flex items-start gap-4 relative pl-8">
                <div className="w-3 h-3 rounded-full bg-indigo-400 absolute left-2 top-1.5 border-2 border-slate-900" />
                <div className="flex-1 p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">{item.event_type.replace(/_/g, " ")}</span>
                    <span className="text-[10px] text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Actor: <strong className="text-slate-300">{item.actor}</strong>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default CareerTwinPage;
