import React, { useState, useEffect } from 'react';
import {
  Compass,
  Target,
  CheckCircle2,
  Circle,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Layers,
  Award,
  Zap,
  Calendar,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  BookOpen,
  Code,
  ShieldCheck,
  ExternalLink,
  Building2,
  Play,
  Pause,
  Copy,
  Check,
  X,
  Flame,
  FileCode2,
  SlidersHorizontal,
  Plus,
  CheckCheck,
  RefreshCcw,
  BarChart3,
  ChevronRight
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type {
  DailyMissionData,
  DailyMissionTask,
  InterventionPlanData,
  WeeklyCareerReviewData
} from '@/api/careerIntelligenceApi';
import {
  TOP_25_MNCS,
  normalizeRole,
  getRoleDailyMission,
  ROLE_MISSIONS_PRIMARY,
  ROLE_MISSIONS_ALT
} from './roleMissionsData';


// Curated Real-World Milestone Blueprints & Production Code Templates
const MILESTONE_BLUEPRINTS: Record<string, {
  mental_model: string;
  starter_code: string;
  rubric: string[];
  recommended_tools: string;
  lab_route: string;
}> = {
  "Master Networking & Socket Fundamentals (Prerequisite)": {
    mental_model: "TCP handshake, socket state machines (SYN, ACK, TIME_WAIT), epoll/kqueue event loops, and connection pool sizing to prevent socket exhaustion under high concurrent load.",
    starter_code: `import asyncio
import socket

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read(4096)
    message = data.decode('utf-8', errors='ignore')
    # Idempotent frame parsing
    response = f"ACK:{len(data)}".encode('utf-8')
    writer.write(response)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def run_server(host='127.0.0.1', port=9000):
    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(run_server())`,
    rubric: [
      "Handles socket disconnects gracefully without leaking file descriptors.",
      "Connection pooling configured with max_overflow and pool_timeout.",
      "Zero buffer overflows on variable payload frames."
    ],
    recommended_tools: "Wireshark / curl --raw / netstat / Linux epoll",
    lab_route: "/app/coding-interview"
  },
  "Implement Python Data Model & Standalone Scaffold": {
    mental_model: "Domain-Driven Design (DDD) with Pydantic v2 schemas and SQLAlchemy 2.0 async mapped classes. Ensuring strict type invariance and decoupled repository layers.",
    starter_code: `from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\\.[^@]+$")
    created_at: datetime`,
    rubric: [
      "Strict schema validation with Pydantic v2 regex and constraints.",
      "Async engine initialization with connection pool health checks.",
      "Docker Compose environment boots up with single 'docker-compose up -d'."
    ],
    recommended_tools: "VS Code / Docker / PostgreSQL 16 / Alembic",
    lab_route: "/app/micro-internships"
  },
  "Build High-Throughput Service Layer": {
    mental_model: "Asynchronous pipeline processing, resilient circuit breaker wrappers, exponential backoff retries with jitter, and dead-letter queue routing.",
    starter_code: `import asyncio
import random
import logging

logger = logging.getLogger(__name__)

async def call_external_dependency(payload: dict) -> dict:
    if random.random() < 0.15:
        raise ConnectionResetError("Transient network partition")
    return {"status": "SUCCESS", "data": payload}

async def execute_with_jitter_retry(payload: dict, max_retries: int = 3) -> dict:
    for attempt in range(1, max_retries + 1):
        try:
            return await call_external_dependency(payload)
        except ConnectionResetError as exc:
            if attempt == max_retries:
                logger.error("Circuit opened. Routing to Dead-Letter Queue (DLQ).")
                raise exc
            delay = (2 ** attempt) + random.uniform(0.1, 0.4)
            await asyncio.sleep(delay)`,
    rubric: [
      "Idempotent message handling with deduplication keys in Redis.",
      "Exponential backoff with randomized jitter prevents thundering herd.",
      "Graceful degradation when downstream dependencies fail."
    ],
    recommended_tools: "FastAPI / Redis Streams / Celery / Locust load testing",
    lab_route: "/app/mnc-studio"
  }
};

export const CareerOSPage: React.FC = () => {
  const [targetRole, setTargetRole] = useState<string>('AI/ML Engineer');
  const [strategy, setStrategy] = useState<string>('BALANCED');
  const [dailyMinutes, setDailyMinutes] = useState<number>(60);
  const [missionCycle, setMissionCycle] = useState<number>(0);
  const [isRefreshingMissions, setIsRefreshingMissions] = useState<boolean>(false);
  const [dailyMission, setDailyMission] = useState<DailyMissionData | null>(() => getRoleDailyMission('AI/ML Engineer', 0));
  const [activePlan, setActivePlan] = useState<InterventionPlanData | null>(null);
  const [weeklyReview, setWeeklyReview] = useState<WeeklyCareerReviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  const handleRoleChange = (newRole: string) => {
    setTargetRole(newRole);
    setMissionCycle(0);
    // Instant role calibration without waiting for network
    setDailyMission(getRoleDailyMission(newRole, 0));
  };

  // Completed Milestones Persistence (D1, D2, ...)
  const [completedMilestones, setCompletedMilestones] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem('vireoniq_completed_milestones');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Completed Daily Missions Persistence (aiml-1, aiml-2, aiml-3, ...)
  const [completedMissionIds, setCompletedMissionIds] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem('vireoniq_completed_daily_missions');
      return saved ? JSON.parse(saved) : { "aiml-3": true }; // aiml-3 pre-completed for realistic flow
    } catch {
      return { "aiml-3": true };
    }
  });

  // Milestone Detail Modal State
  const [selectedMilestone, setSelectedMilestone] = useState<any | null>(null);
  const [copiedMilestoneCode, setCopiedMilestoneCode] = useState<boolean>(false);
  const [blueprintLang, setBlueprintLang] = useState<string>(() => {
    try {
      return localStorage.getItem('vireoniq_preferred_coding_language') || 'python';
    } catch {
      return 'python';
    }
  });

  // Customize Pathway Modal State
  const [isCustomizeOpen, setIsCustomizeOpen] = useState<boolean>(false);
  const [customFocusSkill, setCustomFocusSkill] = useState<string>('Python');
  const [customDuration, setCustomDuration] = useState<string>('DEEP_MASTERY');
  const [customMinutes, setCustomMinutes] = useState<number>(75);

  // Adaptive Replan Modal State
  const [isReplanModalOpen, setIsReplanModalOpen] = useState<boolean>(false);
  const [replanTrigger, setReplanTrigger] = useState<string>('ASSESSMENT_PREREQUISITE_IDENTIFIED');
  const [replanningLoading, setReplanningLoading] = useState<boolean>(false);
  const [lastReplanDiff, setLastReplanDiff] = useState<any | null>(null);

  // Add Custom Milestone Modal State
  const [isAddMilestoneOpen, setIsAddMilestoneOpen] = useState<boolean>(false);
  const [newMilestoneTitle, setNewMilestoneTitle] = useState<string>('');
  const [newMilestoneDesc, setNewMilestoneDesc] = useState<string>('');
  const [newMilestoneType, setNewMilestoneType] = useState<string>('PRACTICE');
  const [newMilestoneDay, setNewMilestoneDay] = useState<number>(3);

  // Modal & Detailed Blueprint State for Daily Missions
  const [selectedTask, setSelectedTask] = useState<DailyMissionTask | null>(null);
  const [activeModalTab, setActiveModalTab] = useState<'HOW' | 'WHERE' | 'WHEN' | 'PROOF'>('HOW');
  const [copiedCode, setCopiedCode] = useState<boolean>(false);
  const [submissionProofText, setSubmissionProofText] = useState<string>('');

  // Interactive In-App Sprint Countdown Timer
  const [timerActive, setTimerActive] = useState<boolean>(false);
  const [timerSeconds, setTimerSeconds] = useState<number>(1500); // 25 min default
  const [timerTotal, setTimerTotal] = useState<number>(1500);

  // Timer Tick Effect
  useEffect(() => {
    let interval: any = null;
    if (timerActive && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev - 1);
      }, 1000);
    } else if (timerSeconds === 0) {
      setTimerActive(false);
    }
    return () => clearInterval(interval);
  }, [timerActive, timerSeconds]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleOpenTaskModal = (task: DailyMissionTask, defaultTab: 'HOW' | 'WHERE' | 'WHEN' | 'PROOF' = 'HOW') => {
    setSelectedTask(task);
    setActiveModalTab(defaultTab);
    const mins = task.estimated_minutes || 25;
    setTimerSeconds(mins * 60);
    setTimerTotal(mins * 60);
    setTimerActive(false);
    setCopiedCode(false);
    setSubmissionProofText('');
  };

  const handleCloseModal = () => {
    setSelectedTask(null);
    setTimerActive(false);
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2500);
  };

  const handleCopyMilestoneCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedMilestoneCode(true);
    setTimeout(() => setCopiedMilestoneCode(false), 2500);
  };

  const getFormattedMilestoneCode = (defaultCode: string, lang: string, title: string) => {
    if (lang === 'python') return defaultCode;
    if (lang === 'java') {
      return `// Production Java 21 Scaffold for ${title}
package com.vireoniq.milestone;

import java.util.concurrent.*;
import java.util.*;

public class MilestoneSolution {
    public static void main(String[] args) {
        System.out.println("Executing: ${title}");
        // High-concurrency invariants verified for Tier-1 MNC loops
    }
}`;
    }
    if (lang === 'cpp') {
      return `// Production C++20 Scaffold for ${title}
#include <iostream>
#include <vector>
#include <memory>

int main() {
    std::cout << "Executing: ${title}" << std::endl;
    // Zero-overhead memory allocation & RAII guarantees
    return 0;
}`;
    }
    if (lang === 'go') {
      return `// Production Go 1.22 Scaffold for ${title}
package main

import (
    "fmt"
    "context"
)

func main() {
    ctx := context.Background()
    fmt.Printf("Executing: %s (Context: %v)\\n", "${title}", ctx)
    // High-throughput goroutine worker pool
}`;
    }
    if (lang === 'typescript' || lang === 'javascript') {
      return `// Production TypeScript 5.4 Scaffold for ${title}
export interface MilestoneContext {
    milestone: string;
    timestamp: number;
}

export async function executeMilestone(): Promise<void> {
    console.log("Executing: ${title}");
    // Async event loop & non-blocking execution
}

executeMilestone();`;
    }
    if (lang === 'rust') {
      return `// Production Rust 1.77 Scaffold for ${title}
use std::sync::Arc;

#[tokio::main]
async fn main() {
    println!("Executing: {}", "${title}");
    // Zero-cost abstractions & thread safety verified
}`;
    }
    if (lang === 'csharp') {
      return `// Production C# (.NET 8) Scaffold for ${title}
using System;
using System.Threading.Tasks;

namespace Vireoniq.Milestones;

public class Solution {
    public static async Task Main(string[] args) {
        Console.WriteLine("Executing: ${title}");
        await Task.CompletedTask;
    }
}`;
    }
    return defaultCode;
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [missionData, planData, reviewData] = await Promise.all([
        careerIntelligenceApi.getDailyCareerMission(targetRole, false, missionCycle).catch(() => null),
        careerIntelligenceApi.getActiveInterventionPlan().catch(() => null),
        careerIntelligenceApi.getWeeklyCareerReview(targetRole).catch(() => null)
      ]);

      const matchedFallback = getRoleDailyMission(targetRole, missionCycle);
      setDailyMission(missionData || matchedFallback);

      // Ensure activePlan is never null so user always has an interactive roadmap
      const defaultActivePlan: InterventionPlanData = {
        plan_id: "plan-python-core-01",
        target_role: targetRole,
        title: "14-Day Python Mastery & Portfolio Acceleration",
        objective: "Eliminate primary bottleneck in Python through a verified project and adaptive assessment.",
        primary_gap: "Python",
        secondary_gaps: ["FastAPI", "Distributed Systems", "Networking"],
        strategy: "DEEP_MASTERY",
        duration_days: 14,
        daily_time_budget_minutes: 60,
        expected_readiness_delta_range: "+6 to +10",
        status: "IN_PROGRESS",
        progress_pct: 28.5,
        tasks: [
          {
            id: "m-1",
            day_number: 1,
            title: "Master Networking & Socket Fundamentals (Prerequisite)",
            description: "Foundational TCP/UDP and connection pool mental models.",
            task_type: "LEARN",
            estimated_minutes: 60,
            expected_evidence_type: "LEARNING_ACTIVITY",
            completion_criteria: "Complete socket architecture review."
          },
          {
            id: "m-2",
            day_number: 2,
            title: "Implement Python Data Model & Standalone Scaffold",
            description: "Bootstrap standalone repository scaffold with Docker Compose for Python.",
            task_type: "PRACTICE",
            estimated_minutes: 60,
            expected_evidence_type: "DEMONSTRATED",
            completion_criteria: "Repository running with automated healthcheck tests."
          },
          {
            id: "m-3",
            day_number: 3,
            title: "Build High-Throughput Service Layer in Python",
            description: "Implement resilient asynchronous workflows, connection pooling, and error boundaries.",
            task_type: "BUILD",
            estimated_minutes: 60,
            expected_evidence_type: "PROJECT_ARTIFACT",
            completion_criteria: "Service handling concurrent requests with sub-50ms latency."
          },
          {
            id: "m-4",
            day_number: 4,
            title: "Unit & Integration Benchmark Suite for Python",
            description: "Achieve >85% test coverage with automated mock suites and load testing.",
            task_type: "PRACTICE",
            estimated_minutes: 45,
            expected_evidence_type: "TEST_RESULTS",
            completion_criteria: "Test suite passing with zero regressions."
          },
          {
            id: "m-5",
            day_number: 7,
            title: "Adaptive Capability Assessment in Python",
            description: "Take 15-minute adaptive technical and architectural assessment for Python.",
            task_type: "ASSESS",
            estimated_minutes: 30,
            expected_evidence_type: "ASSESSED",
            completion_criteria: "Complete assessment with score >= 75/100."
          },
          {
            id: "m-6",
            day_number: 14,
            title: "Final Reassessment & Twin Elevation for " + targetRole,
            description: "Perform comprehensive capability measurement updating Career Digital Twin.",
            task_type: "REASSESS",
            estimated_minutes: 35,
            expected_evidence_type: "VERIFIED",
            completion_criteria: "Recalculate Career Readiness Index and verify bottleneck resolution."
          }
        ]
      };

      setActivePlan(planData || defaultActivePlan);
      setWeeklyReview(reviewData || {
        week_start_date: "Aug 18, 2026",
        target_role: targetRole,
        starting_readiness: 78,
        ending_readiness: 83,
        readiness_delta: 5,
        evidence_count_added: 6,
        gaps_closed: ["Prefix Sum Arrays", "Idempotency Architecture"],
        remaining_constraints: ["Distributed Concurrency", "System Latency Profiling"],
        attribution: { "DSA Practice": "+2.4 CRI", "System Design": "+2.6 CRI" },
        next_week_priority: "Complete 2 MNC Coding Studio rounds and achieve 90%+ AST correctness."
      });
    } catch (err) {
      console.warn('Using Career OS local fallback intelligence', err);
      setDailyMission(getRoleDailyMission(targetRole, missionCycle));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [targetRole]);

  // Milestone checkmark toggle
  const handleToggleMilestone = (mId: string) => {
    setCompletedMilestones((prev) => {
      const next = { ...prev, [mId]: !prev[mId] };
      try {
        localStorage.setItem('vireoniq_completed_milestones', JSON.stringify(next));
      } catch {}
      return next;
    });
    setFeedbackSuccess('Milestone status updated! +25 XP awarded');
    setTimeout(() => setFeedbackSuccess(null), 3000);
  };

  // Daily mission mark done toggle
  const handleToggleDailyMission = async (taskId: string) => {
    setCompletingTaskId(taskId);
    setCompletedMissionIds((prev) => {
      const next = { ...prev, [taskId]: !prev[taskId] };
      try {
        localStorage.setItem('vireoniq_completed_daily_missions', JSON.stringify(next));
      } catch {}
      return next;
    });

    try {
      await careerIntelligenceApi.completeInterventionTask(taskId).catch(() => null);
    } catch {}

    if (dailyMission) {
      setDailyMission({
        ...dailyMission,
        tasks: dailyMission.tasks.map((t) =>
          t.task_id === taskId
            ? { ...t, status: t.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED' }
            : t
        )
      });
    }

    setFeedbackSuccess('Mission verified & progress logged! +30 XP');
    setTimeout(() => setFeedbackSuccess(null), 3000);
    setCompletingTaskId(null);
  };

  // Direct link click handler
  const handleLaunchDirectLink = (platform: string, url?: string) => {
    if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }
    if (platform.includes('LeetCode')) {
      window.open('https://leetcode.com/problems/subarray-sum-equals-k/', '_blank');
      return;
    }
    if (platform.includes('Twin') || platform.includes('Studio')) {
      window.location.href = '/app/interview-twin';
      return;
    }
    if (platform.includes('System Design') || platform.includes('Excalidraw')) {
      window.open('https://excalidraw.com', '_blank');
      return;
    }
    window.location.href = '/app/coding-interview';
  };

  // Adaptive Replan execution with diff
  const handleAdaptiveReplanExecute = async () => {
    if (!activePlan) return;
    setReplanningLoading(true);
    try {
      const res = await careerIntelligenceApi.replanIntervention(activePlan.plan_id, replanTrigger);
      setLastReplanDiff(res?.plan_diff || {
        added_tasks: ["Master Networking & Socket Fundamentals (Prerequisite)"],
        retained_tasks: activePlan.tasks.map((t) => t.title)
      });
      await loadData();
      setFeedbackSuccess('Adaptive replanning applied! +35 XP');
      setTimeout(() => setFeedbackSuccess(null), 4000);
      setIsReplanModalOpen(false);
    } catch (err) {
      console.warn('Executing client adaptive reorganization', err);
      const skill = activePlan.primary_gap || 'Python';
      const adaptedTask = {
        id: `adapted-${Date.now()}`,
        day_number: 1,
        title: replanTrigger === "TIMELINE_ACCELERATION"
          ? `High-Impact ${skill} Algorithmic & System Design Drill (Accelerated)`
          : replanTrigger === "SYSTEM_DESIGN_PIVOT"
          ? `Distributed Systems Architecture & Low-Latency Trade-offs for ${skill}`
          : `Master ${skill} Networking & Socket Fundamentals (Prerequisite)`,
        description: replanTrigger === "TIMELINE_ACCELERATION"
          ? "Compressed high-yield drill covering Tier-1 MNC interview evaluation patterns."
          : replanTrigger === "SYSTEM_DESIGN_PIVOT"
          ? "High-level design (HLD), cache stampede mitigation, and event-driven pipelines."
          : "Foundational TCP/UDP, connection pool mental models, and memory invariants.",
        task_type: "LEARN",
        estimated_minutes: activePlan.daily_time_budget_minutes || 60,
        expected_evidence_type: "LEARNING_ACTIVITY",
        completion_criteria: `Complete ${skill} architecture review & rubric verification.`
      };
      const updatedTasks = [adaptedTask, ...activePlan.tasks.filter((t) => t.day_number !== 1)];
      setActivePlan({
        ...activePlan,
        tasks: updatedTasks
      });
      setLastReplanDiff({
        added_tasks: [adaptedTask.title],
        retained_tasks: updatedTasks.slice(1).map((t) => t.title)
      });
      setFeedbackSuccess('Adaptive replan activated! +35 XP');
      setTimeout(() => setFeedbackSuccess(null), 4000);
      setIsReplanModalOpen(false);
    } finally {
      setReplanningLoading(false);
    }
  };

  // Custom pathway generation
  const handleCustomPathwaySubmit = async () => {
    setLoading(true);
    setIsCustomizeOpen(false);
    try {
      const generated = await careerIntelligenceApi.generateInterventionPlan(
        targetRole,
        customDuration,
        customMinutes,
        customFocusSkill
      );
      setActivePlan(generated);
      setFeedbackSuccess(`Generated new ${generated.duration_days}-Day pathway for ${customFocusSkill}!`);
      setTimeout(() => setFeedbackSuccess(null), 4000);
    } catch (err) {
      console.warn('Fallback generation for custom pathway', err);
      const durationMap: Record<string, number> = {
        FASTEST: 10,
        BALANCED: 14,
        HIGH_EVIDENCE: 18,
        DEEP_MASTERY: 30
      };
      const dDays = durationMap[customDuration] || 14;
      const customPlan: InterventionPlanData = {
        plan_id: `custom-plan-${Date.now()}`,
        target_role: targetRole,
        title: `${dDays}-Day ${customFocusSkill} Mastery & Portfolio Acceleration`,
        objective: `Eliminate primary bottleneck in ${customFocusSkill} through verified engineering projects and adaptive assessments.`,
        primary_gap: customFocusSkill,
        secondary_gaps: ["Distributed Systems", "API Performance", "System Design"],
        strategy: customDuration,
        duration_days: dDays,
        daily_time_budget_minutes: customMinutes,
        expected_readiness_delta_range: customDuration === "DEEP_MASTERY" ? "+8 to +12" : "+5 to +8",
        status: "IN_PROGRESS",
        progress_pct: 0,
        tasks: [
          {
            id: `m-custom-1`,
            day_number: 1,
            title: `Master ${customFocusSkill} Core Fundamentals & Architecture Invariants`,
            description: `Study deep internals, memory lifecycle, and design tradeoffs for ${customFocusSkill}.`,
            task_type: "LEARN",
            estimated_minutes: Math.min(45, customMinutes),
            expected_evidence_type: "LEARNING_ACTIVITY",
            completion_criteria: `Document 3 core architecture tradeoffs in ${customFocusSkill}.`
          },
          {
            id: `m-custom-2`,
            day_number: 2,
            title: `Implement ${customFocusSkill} Data Model & Standalone Scaffold`,
            description: `Bootstrap standalone repository scaffold with Docker Compose for ${customFocusSkill}.`,
            task_type: "PRACTICE",
            estimated_minutes: customMinutes,
            expected_evidence_type: "DEMONSTRATED",
            completion_criteria: "Repository running with automated healthcheck tests."
          },
          {
            id: `m-custom-3`,
            day_number: 3,
            title: `Build High-Throughput Service Layer in ${customFocusSkill}`,
            description: "Implement resilient asynchronous workflows, connection pooling, and error boundaries.",
            task_type: "BUILD",
            estimated_minutes: customMinutes,
            expected_evidence_type: "PROJECT_ARTIFACT",
            completion_criteria: "Service handling concurrent requests with sub-50ms latency."
          },
          {
            id: `m-custom-4`,
            day_number: 4,
            title: `Unit & Integration Benchmark Suite for ${customFocusSkill}`,
            description: "Achieve >85% test coverage with automated mock suites and load testing.",
            task_type: "PRACTICE",
            estimated_minutes: Math.min(45, customMinutes),
            expected_evidence_type: "TEST_RESULTS",
            completion_criteria: "Test suite passing with zero regressions."
          },
          {
            id: `m-custom-5`,
            day_number: Math.min(7, dDays),
            title: `Adaptive Capability Assessment in ${customFocusSkill}`,
            description: `Take 15-minute adaptive technical and architectural assessment for ${customFocusSkill}.`,
            task_type: "ASSESS",
            estimated_minutes: 30,
            expected_evidence_type: "ASSESSED",
            completion_criteria: "Complete assessment with score >= 75/100."
          },
          {
            id: `m-custom-6`,
            day_number: dDays,
            title: `Final Reassessment & Twin Elevation for ${targetRole}`,
            description: "Perform comprehensive capability measurement updating Career Digital Twin.",
            task_type: "REASSESS",
            estimated_minutes: 35,
            expected_evidence_type: "VERIFIED",
            completion_criteria: "Recalculate Career Readiness Index and verify bottleneck resolution."
          }
        ]
      };
      setActivePlan(customPlan);
      setFeedbackSuccess(`Custom ${dDays}-Day pathway generated for ${customFocusSkill}!`);
      setTimeout(() => setFeedbackSuccess(null), 4000);
    } finally {
      setLoading(false);
    }
  };

  // Add Custom Milestone
  const handleAddCustomMilestone = () => {
    if (!newMilestoneTitle.trim() || !activePlan) return;
    const newTask = {
      id: `custom-milestone-${Date.now()}`,
      day_number: newMilestoneDay || 3,
      title: newMilestoneTitle.trim(),
      description: newMilestoneDesc.trim() || "Custom candidate preparation task.",
      task_type: newMilestoneType,
      estimated_minutes: 45,
      expected_evidence_type: "DEMONSTRATED",
      completion_criteria: "Candidate self-verified deliverables."
    };
    const updatedTasks = [...activePlan.tasks, newTask].sort((a, b) => a.day_number - b.day_number);
    setActivePlan({
      ...activePlan,
      tasks: updatedTasks
    });
    setIsAddMilestoneOpen(false);
    setNewMilestoneTitle('');
    setNewMilestoneDesc('');
    setFeedbackSuccess('Custom milestone added to pathway!');
    setTimeout(() => setFeedbackSuccess(null), 3000);
  };

  const handleRefreshDailyMissions = async () => {
    setIsRefreshingMissions(true);
    const nextCycle = missionCycle + 1;
    setMissionCycle(nextCycle);
    try {
      const data = await careerIntelligenceApi.getDailyCareerMission(targetRole, true, nextCycle);
      setDailyMission(data);
      setFeedbackSuccess(`✨ Quests Refreshed for ${targetRole}! Tier-1 MNC challenge set ${nextCycle % 2 === 1 ? 'B' : 'A'} loaded.`);
      setTimeout(() => setFeedbackSuccess(null), 3500);
    } catch {
      const fallback = getRoleDailyMission(targetRole, nextCycle);
      setDailyMission(fallback);
      setFeedbackSuccess(`✨ Quests Rotated for ${targetRole}! New challenge set loaded.`);
      setTimeout(() => setFeedbackSuccess(null), 3500);
    } finally {
      setIsRefreshingMissions(false);
    }
  };

  const getTaskTypeStyle = (type: string) => {
    switch (type) {
      case 'CODING_DRILL':
        return {
          badge: 'bg-sky-500/10 border-sky-500/30 text-sky-300',
          cardGlow: 'hover:border-sky-500/40 hover:shadow-sky-500/5',
          label: 'Coding Drill',
          icon: <Code className="w-3 h-3 text-sky-400" />
        };
      case 'SYSTEM_DESIGN':
        return {
          badge: 'bg-purple-500/10 border-purple-500/30 text-purple-300',
          cardGlow: 'hover:border-purple-500/40 hover:shadow-purple-500/5',
          label: 'System Design',
          icon: <Layers className="w-3 h-3 text-purple-400" />
        };
      case 'BEHAVIORAL_STAR':
        return {
          badge: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
          cardGlow: 'hover:border-amber-500/40 hover:shadow-amber-500/5',
          label: 'Behavioral STAR',
          icon: <Sparkles className="w-3 h-3 text-amber-400" />
        };
      default:
        return {
          badge: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
          cardGlow: 'hover:border-emerald-500/40 hover:shadow-emerald-500/5',
          label: type,
          icon: <Zap className="w-3 h-3 text-emerald-400" />
        };
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-sm uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4" />
              Continuous Improvement Engine v5.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Daily Career Operating System
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Turn intelligence into measurable daily progress through structured milestones, tasks, and verified proof.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 rounded-xl p-1.5 pl-3 shadow-inner">
            <label className="text-xs text-slate-400 font-medium whitespace-nowrap flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-indigo-400" />
              <span>Target Role:</span>
            </label>
            <select
              value={targetRole}
              onChange={(e) => handleRoleChange(e.target.value)}
              className="bg-slate-950 border border-slate-700/80 text-white font-medium text-xs rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none cursor-pointer hover:border-slate-600 transition"
            >
              <option value="AI/ML Engineer">AI/ML Engineer</option>
              <option value="Backend Engineer">Backend Engineer</option>
              <option value="Full Stack Engineer">Full Stack Engineer</option>
              <option value="Data Engineer">Data Engineer</option>
              <option value="DevOps / SRE">DevOps / SRE</option>
              <option value="Cloud Architect">Cloud Architect</option>
              <option value="Mobile Engineer">Mobile Engineer</option>
              <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
            </select>
          </div>
        </div>

        {/* 1. Today's Career Mission Card */}
        {dailyMission && (() => {
          const completedDailyCount = dailyMission.tasks.filter(
            (t) => t.status === 'COMPLETED' || !!completedMissionIds[t.task_id]
          ).length;
          const dynamicProgressPct = Math.round((completedDailyCount / dailyMission.tasks.length) * 100);

          return (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 lg:p-8 space-y-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 uppercase tracking-wide flex-wrap">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5" />
                      Today's Mission • {dailyMission.mission_date}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                      {dailyMission.target_role || targetRole} Track
                    </span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-purple-500/10 border border-purple-500/30 text-purple-300">
                      <Sparkles className="w-3 h-3 text-purple-400" />
                      Set {missionCycle % 2 === 1 ? 'B (Advanced)' : 'A (Core)'}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-white tracking-tight mt-1.5">
                    {dailyMission.active_plan_title}
                  </h2>
                  <p className="text-slate-400 text-xs mt-1 leading-relaxed max-w-2xl">
                    {dailyMission.rationale}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs font-mono shrink-0">
                  <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-slate-400">Time Budget</span>
                    <strong className="text-white">{dailyMission.total_estimated_minutes} mins</strong>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
                    <Flame className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-slate-400">Plan Progress</span>
                    <strong className="text-emerald-400">{dynamicProgressPct}%</strong>
                  </div>

                  <button
                    onClick={handleRefreshDailyMissions}
                    disabled={isRefreshingMissions}
                    className="flex items-center gap-1.5 bg-gradient-to-r from-indigo-600/30 to-purple-600/30 hover:from-indigo-600/50 hover:to-purple-600/50 border border-indigo-500/40 text-indigo-200 hover:text-white text-xs px-3.5 py-2 rounded-xl transition shadow-md shadow-indigo-600/10 cursor-pointer disabled:opacity-50"
                    title="Rotate and refresh daily quests"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isRefreshingMissions ? 'animate-spin text-indigo-300' : ''}`} />
                    <span className="font-semibold">Refresh Quests</span>
                  </button>
                </div>
              </div>

              {/* Task Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {dailyMission.tasks.map((task, idx) => {
                  const isCompleted = task.status === 'COMPLETED' || !!completedMissionIds[task.task_id];
                  const mncCompanies = task.where?.mnc_companies || TOP_25_MNCS.slice(0, 5);
                  const style = getTaskTypeStyle(task.task_type);

                  return (
                    <div
                      key={task.task_id}
                      className={`border rounded-2xl p-5 flex flex-col justify-between transition-all duration-200 group relative ${
                        isCompleted
                          ? 'bg-emerald-950/20 border-emerald-800/40 shadow-sm'
                          : `bg-slate-950/90 border-slate-800 hover:shadow-lg ${style.cardGlow}`
                      }`}
                    >
                      <div className="space-y-3">
                        <div className="flex items-center justify-between gap-2">
                          <span className={`inline-flex items-center gap-1.5 text-[11px] font-mono px-2 py-0.5 rounded-md border ${style.badge}`}>
                            {style.icon}
                            <span>Task {idx + 1} • {style.label}</span>
                          </span>
                          <span className="text-xs text-indigo-400 font-mono font-semibold bg-indigo-950/40 border border-indigo-800/30 px-2 py-0.5 rounded-md shrink-0">
                            {task.projected_delta} CRI
                          </span>
                        </div>

                        <div>
                          <h4 className={`text-sm font-semibold tracking-tight leading-snug line-clamp-2 min-h-[2.85rem] transition ${
                            isCompleted ? 'text-slate-300 line-through' : 'text-white group-hover:text-indigo-300'
                          }`}>
                            {task.title}
                          </h4>
                          <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 min-h-[2.5rem] leading-relaxed">
                            {task.why}
                          </p>
                        </div>

                        {/* Top MNC Badges & When Chip */}
                        <div className="space-y-2 pt-1 border-t border-slate-900">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <div className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                              <Building2 className="w-3 h-3 text-indigo-400 shrink-0" />
                              <span>Top MNCs:</span>
                            </div>
                            {mncCompanies.slice(0, 3).map((comp: string) => (
                              <span key={comp} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                                {comp}
                              </span>
                            ))}
                            {mncCompanies.length > 3 && (
                              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/40 text-indigo-300 font-semibold">
                                +{mncCompanies.length - 3} more
                              </span>
                            )}
                          </div>

                          {task.when?.recommended_time && (
                            <div className="flex items-center gap-1.5 text-[10px] text-amber-400/90 font-mono">
                              <Clock className="w-3 h-3 text-amber-400 shrink-0" />
                              <span className="truncate">{task.when.recommended_time.split('—')[0]}</span>
                            </div>
                          )}
                        </div>

                        {/* Action Links & Guide Button */}
                        <div className="pt-2 grid grid-cols-5 gap-2">
                          <button
                            onClick={() => handleOpenTaskModal(task, 'HOW')}
                            className="col-span-3 flex items-center justify-center gap-1.5 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-xs font-semibold px-2.5 py-2 rounded-xl transition shadow-md shadow-indigo-600/20 cursor-pointer"
                          >
                            <BookOpen className="w-3.5 h-3.5 text-indigo-200" />
                            <span>Guide & Code</span>
                          </button>

                          <button
                            onClick={() => handleLaunchDirectLink(task.where?.platform || '', task.where?.url)}
                            className="col-span-2 flex items-center justify-center gap-1 text-xs text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-850 border border-slate-700/80 hover:border-slate-600 px-2 py-2 rounded-xl transition font-medium cursor-pointer"
                            title={`Practice on ${task.where?.platform || 'Practice Studio'}`}
                          >
                            <ExternalLink className="w-3.5 h-3.5 text-indigo-400" />
                            <span className="truncate">Practice</span>
                          </button>
                        </div>
                      </div>

                      <div className="pt-3 flex items-center justify-between border-t border-slate-800/80 mt-4">
                        <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          {task.estimated_minutes} min
                        </span>

                        {isCompleted ? (
                          <button
                            onClick={() => handleToggleDailyMission(task.task_id)}
                            className="text-xs text-emerald-400 font-medium flex items-center gap-1.5 bg-emerald-950/60 hover:bg-emerald-900/40 border border-emerald-800/50 px-3 py-1.5 rounded-lg transition cursor-pointer shadow-sm"
                            title="Click to toggle status"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Completed</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleToggleDailyMission(task.task_id)}
                            disabled={completingTaskId === task.task_id}
                            className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3.5 py-1.5 rounded-lg transition shadow-md shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
                          >
                            {completingTaskId === task.task_id ? 'Completing...' : 'Mark Done'}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })()}

        {/* 2. Active Intervention Timeline or Plan Generator */}
        {activePlan ? (() => {
          const completedCount = activePlan.tasks.filter((t) => !!completedMilestones[t.id]).length;
          const totalMilestones = activePlan.tasks.length || 1;
          const progressPct = Math.round((completedCount / totalMilestones) * 100);
          const normalizedTitle = activePlan.title.replace(/\d+-Day/, `${activePlan.duration_days}-Day`);

          return (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 lg:p-8 space-y-6 shadow-xl">
              {/* Pathway Header */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-indigo-400 uppercase tracking-wide">
                      Active {activePlan.duration_days}-Day Pathway • Strategy: {activePlan.strategy.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800/50">
                      Target: {activePlan.primary_gap || 'Python'}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
                    {normalizedTitle}
                    <span className="text-[11px] font-mono font-normal px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Live Dynamic Vector
                    </span>
                  </h3>
                  <p className="text-slate-400 text-xs mt-1 max-w-2xl">
                    {activePlan.objective}
                  </p>
                </div>

                {/* Pathway Controls */}
                <div className="flex flex-wrap items-center gap-2.5">
                  <button
                    onClick={() => setIsCustomizeOpen(true)}
                    className="flex items-center gap-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 text-xs font-semibold px-3.5 py-2 rounded-lg transition"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                    Customize Pathway
                  </button>

                  <button
                    onClick={() => setIsReplanModalOpen(true)}
                    className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium px-3.5 py-2 rounded-lg transition border border-slate-700"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                    Adaptive Replan
                  </button>

                  <button
                    onClick={() => setIsAddMilestoneOpen(true)}
                    className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium px-3 py-2 rounded-lg transition border border-slate-700"
                    title="Add Custom Milestone"
                  >
                    <Plus className="w-3.5 h-3.5 text-emerald-400" />
                    Add Milestone
                  </button>
                </div>
              </div>

              {/* Pathway Velocity Progress Bar */}
              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1.5">
                  <div className="text-xs font-mono text-slate-400 flex items-center gap-2">
                    <Flame className="w-3.5 h-3.5 text-amber-400" />
                    <span>Pathway Velocity:</span>
                    <strong className="text-white">{completedCount} of {totalMilestones} Milestones Cleared</strong>
                    <span className="text-emerald-400 font-bold">({progressPct}%)</span>
                  </div>
                  <div className="w-64 sm:w-80 bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full transition-all duration-500"
                      style={{ width: `${progressPct}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 font-mono">Progress Rewards:</span>
                  <span className="text-xs font-bold text-indigo-300 bg-indigo-950/60 border border-indigo-800/40 px-2.5 py-1 rounded-lg flex items-center gap-1">
                    <Zap className="w-3 h-3 text-amber-400" />
                    +{completedCount * 25} XP Earned
                  </span>
                </div>
              </div>

              {/* Milestones List */}
              <div className="space-y-3">
                {activePlan.tasks.map((t, idx) => {
                  const isDone = !!completedMilestones[t.id];

                  // Type styling badge
                  const typeColors: Record<string, string> = {
                    LEARN: 'bg-indigo-950/80 text-indigo-300 border-indigo-800/50',
                    PRACTICE: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/50',
                    BUILD: 'bg-amber-950/80 text-amber-300 border-amber-800/50',
                    ASSESS: 'bg-purple-950/80 text-purple-300 border-purple-800/50',
                    REASSESS: 'bg-rose-950/80 text-rose-300 border-rose-800/50'
                  };
                  const badgeColor = typeColors[t.task_type] || 'bg-slate-800 text-slate-300 border-slate-700';

                  return (
                    <div
                      key={t.id || idx}
                      className={`border rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 transition group ${
                        isDone
                          ? 'bg-slate-950/50 border-emerald-800/40'
                          : 'bg-slate-950/80 border-slate-800/90 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-start gap-3.5">
                        {/* Interactive Checkbox */}
                        <button
                          onClick={() => handleToggleMilestone(t.id)}
                          className="mt-0.5 text-slate-500 hover:text-emerald-400 transition shrink-0"
                          title="Toggle Milestone Completion"
                        >
                          {isDone ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                          ) : (
                            <Circle className="w-5 h-5 text-slate-600 hover:text-slate-400" />
                          )}
                        </button>

                        <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-mono text-slate-300 shrink-0 mt-0.5">
                          D{t.day_number}
                        </div>

                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${badgeColor}`}>
                              [{t.task_type}]
                            </span>
                            <h5 className={`text-sm font-semibold transition ${
                              isDone ? 'text-slate-400 line-through' : 'text-white group-hover:text-indigo-300'
                            }`}>
                              {t.title}
                            </h5>
                            {isDone && (
                              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 font-medium">
                                COMPLETED (+25 XP)
                              </span>
                            )}
                          </div>

                          <p className="text-xs text-slate-400 mt-1">{t.description}</p>
                          <div className="text-[11px] text-slate-500 font-mono mt-1 flex items-center gap-1.5">
                            <span className="text-slate-400 font-semibold">Criteria:</span>
                            <span>{t.completion_criteria}</span>
                          </div>
                        </div>
                      </div>

                      {/* Right controls: Evidence Pill & Actions */}
                      <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                        <span className="text-xs font-mono bg-slate-900 border border-slate-800 px-2.5 py-1 rounded text-slate-400 whitespace-nowrap">
                          {t.expected_evidence_type}
                        </span>

                        <button
                          onClick={() => setSelectedMilestone(t)}
                          className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium px-3 py-1.5 rounded-lg border border-slate-700 transition"
                        >
                          <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Blueprint</span>
                        </button>

                        <button
                          onClick={() => handleToggleMilestone(t.id)}
                          className={`text-xs font-medium px-3 py-1.5 rounded-lg transition ${
                            isDone
                              ? 'bg-slate-800 text-slate-400 hover:text-white'
                              : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/20'
                          }`}
                        >
                          {isDone ? 'Undo' : 'Done'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })() : (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6 text-center">
            <h3 className="text-xl font-bold text-white">Generate Personalized Intervention Plan</h3>
            <p className="text-slate-400 text-sm max-w-xl mx-auto">
              Configure your daily time budget and desired strategy to generate an actionable 14/30-day roadmap targeting your largest bottleneck.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2"
              >
                <option value="BALANCED">Strategy: BALANCED (14 days, 60m/day)</option>
                <option value="FASTEST">Strategy: FASTEST (10 days, 90m/day)</option>
                <option value="HIGH_EVIDENCE">Strategy: HIGH_EVIDENCE (18 days, 75m/day)</option>
                <option value="LOWEST_EFFORT">Strategy: LOWEST_EFFORT (21 days, 30m/day)</option>
                <option value="DEEP_MASTERY">Strategy: DEEP_MASTERY (30 days, 75m/day)</option>
              </select>

              <button
                onClick={handleCustomPathwaySubmit}
                disabled={loading}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition shadow-lg shadow-indigo-500/20"
              >
                <Sparkles className="w-4 h-4" />
                Generate Plan
              </button>
            </div>
          </div>
        )}

        {/* 3. Weekly Review Summary */}
        {weeklyReview && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 lg:p-8 space-y-6 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-wide">
                  <BarChart3 className="w-3.5 h-3.5" />
                  Weekly Readiness Review • Week of {weeklyReview.week_start_date}
                </div>
                <h3 className="text-xl font-bold text-white mt-1">
                  Readiness Velocity & Proof Attribution
                </h3>
                <p className="text-slate-400 text-xs mt-1">
                  Measurable delta tracked against Tier-1 MNC hiring bars for {weeklyReview.target_role}.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-slate-950 border border-emerald-800/40 px-4 py-2 rounded-xl text-center">
                  <span className="text-[10px] font-mono text-slate-400 block">Readiness Delta</span>
                  <strong className="text-emerald-400 font-mono text-base font-bold">
                    +{weeklyReview.readiness_delta}% CRI
                  </strong>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[11px] font-mono text-slate-500">Starting Readiness</span>
                <div className="text-xl font-bold text-white font-mono">{weeklyReview.starting_readiness}%</div>
                <span className="text-[10px] text-slate-400">Baseline before current sprints</span>
              </div>

              <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[11px] font-mono text-slate-500">Ending Readiness</span>
                <div className="text-xl font-bold text-emerald-400 font-mono">{weeklyReview.ending_readiness}%</div>
                <span className="text-[10px] text-emerald-500/90 font-medium">Verified by AI Rubric</span>
              </div>

              <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[11px] font-mono text-slate-500">Evidence Verified</span>
                <div className="text-xl font-bold text-indigo-300 font-mono">+{weeklyReview.evidence_count_added} Artifacts</div>
                <span className="text-[10px] text-slate-400">Git commits & code reviews</span>
              </div>

              <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[11px] font-mono text-slate-500">Next Priority</span>
                <div className="text-xs font-semibold text-amber-300 line-clamp-2 mt-1">
                  {weeklyReview.next_week_priority}
                </div>
              </div>
            </div>

            {/* Gaps Closed & Constraints */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="bg-slate-950/90 border border-slate-800 p-4 rounded-xl space-y-2">
                <span className="text-xs font-mono text-emerald-400 font-semibold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Gaps Closed This Sprint:
                </span>
                <div className="flex flex-wrap gap-2">
                  {weeklyReview.gaps_closed.map((gap, gIdx) => (
                    <span
                      key={gIdx}
                      className="text-xs bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 px-2.5 py-1 rounded-md font-mono"
                    >
                      ✓ {gap}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-slate-950/90 border border-slate-800 p-4 rounded-xl space-y-2">
                <span className="text-xs font-mono text-amber-400 font-semibold flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4" />
                  Primary Remaining Constraints:
                </span>
                <div className="flex flex-wrap gap-2">
                  {weeklyReview.remaining_constraints.map((con, cIdx) => (
                    <span
                      key={cIdx}
                      className="text-xs bg-amber-950/40 border border-amber-800/40 text-amber-300 px-2.5 py-1 rounded-md font-mono"
                    >
                      • {con}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FEEDBACK SUCCESS TOAST */}
        {feedbackSuccess && (
          <div className="fixed bottom-6 right-6 z-50 bg-indigo-600 text-white text-xs font-medium px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2 border border-indigo-400/40 animate-bounce">
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>{feedbackSuccess}</span>
          </div>
        )}

        {/* MODAL 1: DAILY MISSION BLUEPRINT */}
        {selectedTask && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
              {/* Modal Header */}
              <div className="p-5 border-b border-slate-800 flex items-start justify-between gap-4">
                <div>
                  <span className="text-[11px] font-mono text-indigo-400 uppercase tracking-wide">
                    Daily Task Blueprint • {selectedTask.task_type}
                  </span>
                  <h3 className="text-base font-bold text-white mt-1">
                    {selectedTask.title}
                  </h3>
                </div>
                <button
                  onClick={handleCloseModal}
                  className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Nav Tabs */}
              <div className="flex border-b border-slate-800 px-5 bg-slate-950/40">
                {(['HOW', 'WHERE', 'WHEN', 'PROOF'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveModalTab(tab)}
                    className={`py-3 px-4 text-xs font-mono font-medium border-b-2 transition ${
                      activeModalTab === tab
                        ? 'border-indigo-500 text-indigo-400 font-bold'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {tab === 'HOW' && '1. Blueprint (HOW)'}
                    {tab === 'WHERE' && '2. Platform (WHERE)'}
                    {tab === 'WHEN' && '3. Schedule (WHEN)'}
                    {tab === 'PROOF' && '4. Evidence (PROOF)'}
                  </button>
                ))}
              </div>

              {/* Modal Body */}
              <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
                {activeModalTab === 'HOW' && (
                  <div className="space-y-5">
                    {selectedTask.how?.steps && (
                      <div className="space-y-3">
                        <span className="text-xs font-mono text-indigo-400 uppercase font-semibold block">
                          Phase-by-Phase Execution:
                        </span>
                        {selectedTask.how.steps.map((step, sIdx) => (
                          <div key={sIdx} className="bg-slate-950 border border-slate-800/80 p-3 rounded-lg space-y-1">
                            <span className="text-emerald-400 font-mono font-bold block">{step.phase}</span>
                            <p className="text-slate-300 leading-relaxed">{step.detail}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {selectedTask.how?.code_blueprint && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono text-slate-400 uppercase">Production Starter Code:</span>
                          <button
                            onClick={() => handleCopyCode(selectedTask.how?.code_blueprint || '')}
                            className="flex items-center gap-1 bg-slate-800 px-2.5 py-1 rounded text-slate-300 hover:text-white"
                          >
                            {copiedCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                            <span>{copiedCode ? 'Copied!' : 'Copy Code'}</span>
                          </button>
                        </div>
                        <pre className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl font-mono text-emerald-300 overflow-x-auto text-[11px]">
                          {selectedTask.how.code_blueprint}
                        </pre>
                      </div>
                    )}
                  </div>
                )}

                {activeModalTab === 'WHERE' && (
                  <div className="space-y-4">
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-3">
                      <span className="text-slate-400 font-mono">Platform: <strong className="text-white">{selectedTask.where?.platform || 'Practice Studio'}</strong></span>
                      <button
                        onClick={() => handleLaunchDirectLink(selectedTask.where?.platform || '', selectedTask.where?.url)}
                        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 px-4 rounded-lg transition"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Launch Problem on {selectedTask.where?.platform || 'Studio'}
                      </button>
                    </div>
                  </div>
                )}

                {activeModalTab === 'WHEN' && (
                  <div className="space-y-4 text-center">
                    <div className="text-4xl font-mono font-bold text-white py-2">
                      {formatTimer(timerSeconds)}
                    </div>
                    <div className="flex justify-center gap-3">
                      {!timerActive ? (
                        <button
                          onClick={() => setTimerActive(true)}
                          className="flex items-center gap-1.5 bg-indigo-600 text-white px-4 py-2 rounded-lg"
                        >
                          <Play className="w-3.5 h-3.5" /> Start Timer
                        </button>
                      ) : (
                        <button
                          onClick={() => setTimerActive(false)}
                          className="flex items-center gap-1.5 bg-amber-600 text-white px-4 py-2 rounded-lg"
                        >
                          <Pause className="w-3.5 h-3.5" /> Pause
                        </button>
                      )}
                      <button
                        onClick={() => { setTimerActive(false); setTimerSeconds(timerTotal); }}
                        className="bg-slate-800 text-slate-300 px-3 py-2 rounded-lg"
                      >
                        Reset
                      </button>
                    </div>
                  </div>
                )}

                {activeModalTab === 'PROOF' && (
                  <div className="space-y-4">
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                      <span className="text-cyan-400 font-mono font-semibold block">Deliverable Rubric:</span>
                      <p className="text-slate-300">{selectedTask.proof_criteria?.deliverable || 'Verified code solution'}</p>
                    </div>
                    <textarea
                      value={submissionProofText}
                      onChange={(e) => setSubmissionProofText(e.target.value)}
                      placeholder="Paste your LeetCode submission URL, GitHub commit link, or key architectural reflections..."
                      rows={4}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 focus:outline-none"
                    />
                    <button
                      onClick={() => {
                        handleToggleDailyMission(selectedTask.task_id);
                        handleCloseModal();
                      }}
                      className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl font-semibold flex items-center justify-center gap-2"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Verify & Claim {selectedTask.projected_delta} CRI
                    </button>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
                <span className="text-slate-400 font-mono">
                  Budget: <strong className="text-white">{selectedTask.estimated_minutes} mins</strong> • Delta: <strong className="text-indigo-400">{selectedTask.projected_delta} CRI</strong>
                </span>
                <button
                  onClick={handleCloseModal}
                  className="bg-slate-800 text-slate-300 px-3.5 py-1.5 rounded-lg"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL 2: MILESTONE BLUEPRINT INSPECTOR */}
        {selectedMilestone && (() => {
          const bp = MILESTONE_BLUEPRINTS[selectedMilestone.title] || {
            mental_model: `Architectural principles, algorithmic complexity, and production invariants for ${selectedMilestone.title}.`,
            starter_code: `# Production scaffold for ${selectedMilestone.title}
import asyncio

async def run_milestone():
    print("Executing ${selectedMilestone.title}...")

if __name__ == '__main__':
    asyncio.run(run_milestone())`,
            rubric: [
              "Zero regressions and passing automated health check.",
              "Documented architectural trade-offs.",
              "Verified under simulated load."
            ],
            recommended_tools: "VS Code / Docker / Python 3.12 / Pytest",
            lab_route: "/app/coding-interview"
          };

          return (
            <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
                <div className="p-5 border-b border-slate-800 flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                        Day {selectedMilestone.day_number} • {selectedMilestone.task_type}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        {selectedMilestone.estimated_minutes} mins
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white mt-1.5">
                      {selectedMilestone.title}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedMilestone(null)}
                    className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="p-6 overflow-y-auto space-y-5 flex-1 text-xs">
                  {/* Mental Model */}
                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                    <span className="text-indigo-400 font-mono font-semibold block flex items-center gap-1.5">
                      <Compass className="w-3.5 h-3.5" />
                      Engineering Mental Model & Architectural Principles:
                    </span>
                    <p className="text-slate-300 leading-relaxed">{bp.mental_model}</p>
                  </div>

                  {/* Starter Code */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <span className="text-xs font-mono text-slate-400 uppercase">Production Starter Blueprint:</span>
                      <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
                        {[
                          { key: 'python', name: 'Python' },
                          { key: 'java', name: 'Java' },
                          { key: 'cpp', name: 'C++' },
                          { key: 'javascript', name: 'JS' },
                          { key: 'typescript', name: 'TS' },
                          { key: 'go', name: 'Go' },
                          { key: 'rust', name: 'Rust' },
                          { key: 'csharp', name: 'C#' }
                        ].map((l) => (
                          <button
                            key={l.key}
                            onClick={() => {
                              setBlueprintLang(l.key);
                              try {
                                localStorage.setItem('vireoniq_preferred_coding_language', l.key);
                              } catch {}
                            }}
                            className={`px-2 py-0.5 rounded text-[10px] font-mono transition ${
                              blueprintLang === l.key
                                ? 'bg-indigo-600 text-white font-bold shadow-sm'
                                : 'bg-slate-800 text-slate-400 hover:text-white'
                            }`}
                          >
                            {l.name}
                          </button>
                        ))}
                      </div>
                      <button
                        onClick={() => {
                          const code = getFormattedMilestoneCode(bp.starter_code, blueprintLang, selectedMilestone.title);
                          handleCopyMilestoneCode(code);
                        }}
                        className="flex items-center gap-1 bg-slate-800 px-2.5 py-1 rounded text-slate-300 hover:text-white shrink-0 ml-auto"
                      >
                        {copiedMilestoneCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedMilestoneCode ? 'Copied!' : 'Copy Code'}</span>
                      </button>
                    </div>
                    <pre className="bg-slate-950 border border-slate-800 p-4 rounded-xl font-mono text-emerald-300 overflow-x-auto text-[11px] leading-relaxed">
                      {getFormattedMilestoneCode(bp.starter_code, blueprintLang, selectedMilestone.title)}
                    </pre>
                  </div>

                  {/* Rubric Criteria */}
                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                    <span className="text-emerald-400 font-mono font-semibold block flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Tier-1 MNC Verification Criteria:
                    </span>
                    <ul className="space-y-1.5 pl-4 list-disc text-slate-300">
                      {bp.rubric.map((r: string, rIdx: number) => (
                        <li key={rIdx}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
                  <button
                    onClick={() => {
                      window.location.href = bp.lab_route;
                    }}
                    className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium px-4 py-2 rounded-lg transition"
                  >
                    <ExternalLink className="w-3.5 h-3.5 text-indigo-400" />
                    Open in MNC Coding Sandbox
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        handleToggleMilestone(selectedMilestone.id);
                        setSelectedMilestone(null);
                      }}
                      className="flex items-center gap-1.5 text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg transition shadow-md shadow-indigo-600/30"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Mark Milestone Done (+25 XP)
                    </button>
                    <button
                      onClick={() => setSelectedMilestone(null)}
                      className="text-xs bg-slate-800 text-slate-300 px-3.5 py-2 rounded-lg"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })()}

        {/* MODAL 3: CUSTOMIZE PATHWAY */}
        {isCustomizeOpen && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold">
                  <SlidersHorizontal className="w-4 h-4" />
                  Customize Personalized Pathway
                </div>
                <button
                  onClick={() => setIsCustomizeOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4 text-xs">
                <div>
                  <label className="text-slate-300 font-semibold block mb-1.5">Target Focus Skill:</label>
                  <select
                    value={customFocusSkill}
                    onChange={(e) => setCustomFocusSkill(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5"
                  >
                    <option value="Python">Python & Async Architecture (FastAPI, Coroutines)</option>
                    <option value="System Design">System Design & Distributed Microservices (HLD/LLD)</option>
                    <option value="Data Structures & Algorithms">DSA & High-Frequency LeetCode Patterns</option>
                    <option value="Go Concurrency">Go Concurrency & High-Throughput Pipelines</option>
                    <option value="Redis Caching">Redis & In-Memory Distributed Caching</option>
                    <option value="PostgreSQL Internals">PostgreSQL & Relational Database Internals</option>
                    <option value="Docker & Kubernetes">DevOps, Docker & Kubernetes Cloud Infrastructure</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1.5">Sprint Strategy & Duration:</label>
                  <select
                    value={customDuration}
                    onChange={(e) => setCustomDuration(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5"
                  >
                    <option value="FASTEST">10-Day FASTEST Sprint (90 min/day) — Interview Cramming</option>
                    <option value="BALANCED">14-Day BALANCED Acceleration (60 min/day) — Recommended</option>
                    <option value="HIGH_EVIDENCE">18-Day HIGH_EVIDENCE (75 min/day) — Portfolio Heavy</option>
                    <option value="DEEP_MASTERY">30-Day DEEP_MASTERY (75 min/day) — Comprehensive Mastery</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1.5">Daily Time Budget:</label>
                  <select
                    value={customMinutes}
                    onChange={(e) => setCustomMinutes(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5"
                  >
                    <option value={30}>30 mins / day (Light)</option>
                    <option value={45}>45 mins / day (Focused)</option>
                    <option value={60}>60 mins / day (Standard Balanced)</option>
                    <option value={75}>75 mins / day (Accelerated)</option>
                    <option value={90}>90 mins / day (Intensive)</option>
                    <option value={120}>120 mins / day (Hardcore Bar-Raiser)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
                <button
                  onClick={() => setIsCustomizeOpen(false)}
                  className="px-4 py-2 text-xs bg-slate-800 text-slate-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCustomPathwaySubmit}
                  disabled={loading}
                  className="px-5 py-2 text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-600/30 flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Generate Custom Pathway
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL 4: ADAPTIVE REPLAN MODAL */}
        {isReplanModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-amber-400 font-mono text-xs font-semibold">
                  <RotateCcw className="w-4 h-4" />
                  Adaptive Replanning Engine
                </div>
                <button
                  onClick={() => setIsReplanModalOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4 text-xs">
                <div>
                  <label className="text-slate-300 font-semibold block mb-1.5">Select Replanning Trigger:</label>
                  <div className="space-y-2">
                    {[
                      {
                        id: 'ASSESSMENT_PREREQUISITE_IDENTIFIED',
                        label: '⚡ Foundational Prerequisite Gap',
                        desc: 'Insert foundational TCP/UDP socket programming and memory invariants on Day 1.'
                      },
                      {
                        id: 'TIMELINE_ACCELERATION',
                        label: '⏰ Upcoming Interview Within 5 Days',
                        desc: 'Compress high-frequency algorithmic and system design interview drills into Day 1.'
                      },
                      {
                        id: 'SYSTEM_DESIGN_PIVOT',
                        label: '🎯 Shift Focus to Distributed System Architecture',
                        desc: 'Pivot to High-Level Design (HLD), low-latency caching, and event-driven microservices.'
                      }
                    ].map((trig) => (
                      <div
                        key={trig.id}
                        onClick={() => setReplanTrigger(trig.id)}
                        className={`p-3 rounded-xl border cursor-pointer transition ${
                          replanTrigger === trig.id
                            ? 'bg-indigo-950/40 border-indigo-500/80 text-white'
                            : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                        }`}
                      >
                        <div className="font-semibold text-xs text-white">{trig.label}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{trig.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Preview Diff */}
                <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">Live Diff Preview:</span>
                  <div className="text-emerald-400 text-xs font-mono">
                    + Insert: {
                      replanTrigger === 'TIMELINE_ACCELERATION'
                        ? 'High-Impact Algorithmic & System Design Drill (Accelerated)'
                        : replanTrigger === 'SYSTEM_DESIGN_PIVOT'
                        ? 'Distributed Systems Architecture & Low-Latency Trade-offs'
                        : 'Master Networking & Socket Fundamentals (Prerequisite)'
                    }
                  </div>
                  <div className="text-slate-400 text-[11px]">
                    All downstream portfolio milestones retained with zero penalty.
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
                <button
                  onClick={() => setIsReplanModalOpen(false)}
                  className="px-4 py-2 text-xs bg-slate-800 text-slate-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAdaptiveReplanExecute}
                  disabled={replanningLoading}
                  className="px-5 py-2 text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-600/30 flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  {replanningLoading ? 'Adapting Plan...' : 'Apply Adaptive Replan (+35 XP)'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL 5: ADD CUSTOM MILESTONE */}
        {isAddMilestoneOpen && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 w-full max-w-md rounded-2xl overflow-hidden shadow-2xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold">
                  <Plus className="w-4 h-4" />
                  Add Custom Milestone
                </div>
                <button
                  onClick={() => setIsAddMilestoneOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Milestone Title:</label>
                  <input
                    type="text"
                    value={newMilestoneTitle}
                    onChange={(e) => setNewMilestoneTitle(e.target.value)}
                    placeholder="e.g. Implement Distributed Rate Limiter in Redis"
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5"
                  />
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Description:</label>
                  <textarea
                    value={newMilestoneDesc}
                    onChange={(e) => setNewMilestoneDesc(e.target.value)}
                    placeholder="Brief description of the deliverable or study topic..."
                    rows={2}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">Task Type:</label>
                    <select
                      value={newMilestoneType}
                      onChange={(e) => setNewMilestoneType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2"
                    >
                      <option value="LEARN">LEARN</option>
                      <option value="PRACTICE">PRACTICE</option>
                      <option value="BUILD">BUILD</option>
                      <option value="ASSESS">ASSESS</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">Target Day:</label>
                    <input
                      type="number"
                      min={1}
                      max={30}
                      value={newMilestoneDay}
                      onChange={(e) => setNewMilestoneDay(Number(e.target.value))}
                      className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
                <button
                  onClick={() => setIsAddMilestoneOpen(false)}
                  className="px-4 py-2 text-xs bg-slate-800 text-slate-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddCustomMilestone}
                  disabled={!newMilestoneTitle.trim()}
                  className="px-5 py-2 text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-lg shadow-emerald-600/30 disabled:opacity-50"
                >
                  Insert Milestone
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
