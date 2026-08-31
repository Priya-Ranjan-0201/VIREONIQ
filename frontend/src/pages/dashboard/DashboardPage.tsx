import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 
  TrendingUp, Brain, Zap, Target, CheckCircle2, Circle, 
  Sparkles, Layers, ShieldCheck, ArrowRight, Activity, Clock, Award,
  RefreshCw, HelpCircle, FileText, Cpu, DollarSign, Code2, Flame,
  Compass, ChevronRight, Play, CheckCircle
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer 
} from "recharts";
import { cn } from "@/lib/utils";
import { careerIntelligenceApi } from "@/api/careerIntelligenceApi";
import type { 
  CareerReadinessV3, SkillEvidenceItem, 
  NextBestActionsResponse, DailyMissionData 
} from "@/api/careerIntelligenceApi";

export const DashboardPage: React.FC = () => {
  const [readiness, setReadiness] = useState<CareerReadinessV3 | null>(null);
  const [skills, setSkills] = useState<SkillEvidenceItem[]>([]);
  const [nextActions, setNextActions] = useState<NextBestActionsResponse | null>(null);
  const [mission, setMission] = useState<DailyMissionData | null>(null);
  const [selectedDimension, setSelectedDimension] = useState<string>("core_technical_mastery");
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<any | null>(null);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [criData, skillsData, actionsData, missionData] = await Promise.all([
        careerIntelligenceApi.getCareerReadinessV3("Backend Engineer"),
        careerIntelligenceApi.getTwinEvidence(),
        careerIntelligenceApi.getNextBestCareerActions("Backend Engineer"),
        careerIntelligenceApi.getDailyMission("Backend Engineer")
      ]);
      setReadiness(criData);
      const safeSkills = Array.isArray(skillsData) 
        ? skillsData 
        : (skillsData?.evidence_items && Array.isArray(skillsData.evidence_items) ? skillsData.evidence_items : []);
      setSkills(safeSkills);
      setNextActions(actionsData);
      setMission(missionData);
      if (criData?.dimension_contributions && !criData.dimension_contributions[selectedDimension]) {
        const firstKey = Object.keys(criData.dimension_contributions)[0];
        if (firstKey) setSelectedDimension(firstKey);
      }
    } catch (err) {
      console.error("Error loading career intelligence dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleToggleTask = async (taskId: string, isCompleted: boolean) => {
    try {
      if (!isCompleted) {
        await careerIntelligenceApi.completeInterventionTask(taskId);
      }
      const updatedMission = await careerIntelligenceApi.getDailyMission(readiness?.target_role || "Backend Engineer");
      setMission(updatedMission);
    } catch (err) {
      console.error("Failed to toggle mission task:", err);
    }
  };

  const handleRunWhatIf = async (dimensionName: string) => {
    setSimulating(true);
    try {
      const sim = await careerIntelligenceApi.runCareerScenario({
        target_role: readiness?.target_role || "Backend Engineer",
        title: `What-If: ${dimensionName} Elevation`,
        scenario_actions: [
          { skill_name: dimensionName, action_type: "ASSESS", target_score: 90 }
        ]
      });
      setSimulationResult({
        scenario: `Counterfactual Simulation: ${dimensionName}`,
        explanation: sim.explanation || `Projected capability increase if ${dimensionName} is assessed at 90+ mastery.`,
        projected_readiness: sim.projected_readiness || Math.min(100, Math.round((readiness?.overall_readiness_score || 75) + 4.5)),
        projected_readiness_delta: sim.projected_delta || "+4.5"
      });
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimulating(false);
    }
  };

  const radarData = readiness?.dimension_contributions 
    ? Object.values(readiness.dimension_contributions).map(d => ({
        subject: d.label || d.dimension.replace(/_/g, ' '),
        A: d.score,
        fullMark: 100
      })) 
    : [
        { subject: "Technical Mastery", A: 84, fullMark: 100 },
        { subject: "System Design", A: 78, fullMark: 100 },
        { subject: "Problem Solving", A: 88, fullMark: 100 },
        { subject: "Evidence Integrity", A: 92, fullMark: 100 },
        { subject: "Communication", A: 80, fullMark: 100 },
      ];

  const tierColors: Record<string, { bg: string; text: string; border: string }> = {
    VERIFIED: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30" },
    ASSESSED: { bg: "bg-cyan-500/10", text: "text-cyan-400", border: "border-cyan-500/30" },
    DEMONSTRATED: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/30" },
    INFERRED: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/30" },
    CLAIMED: { bg: "bg-slate-500/10", text: "text-slate-400", border: "border-slate-500/30" },
  };

  const activeDim = readiness?.dimension_contributions?.[selectedDimension] || {
    dimension: selectedDimension,
    label: selectedDimension.replace(/_/g, " "),
    score: 82.5,
    weight: 0.20,
    contribution_points: 16.5,
    percentage_of_total: 20,
    evidence: [
      "Distributed microservices design assessment validated.",
      "90+ ATS keyword density for scalable backend architectures.",
      "Verified GitHub commit velocity in Python & FastAPI ecosystem."
    ]
  };

  const quickLaunchers = [
    {
      title: "AI STAR Rewriter",
      desc: "Transform rough bullets into Google XYZ & STAR accomplishments.",
      href: "/app/resume-rewriter",
      icon: Sparkles,
      gradient: "from-indigo-500/20 via-purple-500/10 to-transparent",
      border: "hover:border-indigo-500/50",
      badge: "STAR Formula",
      badgeColor: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
    },
    {
      title: "ATS Compatibility",
      desc: "Instant 6-dimension MNC parsing and keyword optimization score.",
      href: "/app/ats-score",
      icon: FileText,
      gradient: "from-cyan-500/20 via-blue-500/10 to-transparent",
      border: "hover:border-cyan-500/50",
      badge: "ATS 90+",
      badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
    },
    {
      title: "JD Match Engine",
      desc: "Compare CV against target MNC Job Descriptions with semantic gap tagging.",
      href: "/app/jd-match",
      icon: Target,
      gradient: "from-emerald-500/20 via-teal-500/10 to-transparent",
      border: "hover:border-emerald-500/50",
      badge: "Semantic AI",
      badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
    },
    {
      title: "MNC Studio (8-Round)",
      desc: "Simulate FAANG/MNC live coding, system design, and behavioral rounds.",
      href: "/app/mnc-interview",
      icon: Cpu,
      gradient: "from-fuchsia-500/20 via-pink-500/10 to-transparent",
      border: "hover:border-fuchsia-500/50",
      badge: "FAANG Calibrated",
      badgeColor: "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30"
    },
    {
      title: "Salary Predictor",
      desc: "Non-linear YOE compensation curves across US, UK, EU, and India PPP.",
      href: "/app/salary-predictor",
      icon: DollarSign,
      gradient: "from-amber-500/20 via-orange-500/10 to-transparent",
      border: "hover:border-amber-500/50",
      badge: "PPP Normalized",
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30"
    },
    {
      title: "Developer Portfolio",
      desc: "Multi-platform ingestion from GitHub, LeetCode, and Codeforces.",
      href: "/app/portfolio",
      icon: Code2,
      gradient: "from-teal-500/20 via-emerald-500/10 to-transparent",
      border: "hover:border-teal-500/50",
      badge: "Multi-Signal",
      badgeColor: "bg-teal-500/20 text-teal-300 border-teal-500/30"
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* ─── Hero Intelligence Header ─── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900/90 via-[#0E1533]/90 to-slate-900/90 border border-white/10 p-8 shadow-2xl backdrop-blur-2xl">
        {/* Glow Spheres in Hero */}
        <div className="pointer-events-none absolute -top-24 -left-24 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl animate-pulse-glow" />
        <div className="pointer-events-none absolute -bottom-24 -right-24 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <span className="badge-neon badge-neon-indigo flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping" />
                Career OS v16.0 Live
              </span>
              <span className="badge-neon badge-neon-emerald flex items-center gap-1.5">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                Evidence Grounded
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-cyan-200 bg-clip-text text-transparent font-heading">
              Autonomous Career Intelligence
            </h1>
            <p className="text-sm sm:text-base text-slate-400 max-w-2xl font-medium leading-relaxed">
              Real-time career digital twin synthesizing ATS compatibility, 5-tier evidence graphs, 
              counterfactual trajectory modeling, and MNC interview simulations.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Button
              onClick={loadDashboardData}
              variant="outline"
              className="bg-white/5 border-white/10 hover:bg-white/10 text-slate-200 rounded-xl px-4 py-2.5 flex items-center gap-2 text-xs font-semibold backdrop-blur-md"
            >
              <RefreshCw className={cn("w-3.5 h-3.5", loading && "animate-spin text-indigo-400")} />
              <span>Refresh Telemetry</span>
            </Button>

            <Link
              to="/app/mnc-interview"
              className="glow-button px-5 py-2.5 text-xs font-bold rounded-xl flex items-center gap-2"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Launch MNC Studio</span>
            </Link>
          </div>
        </div>
      </div>

      {/* ─── 4-Card Bento Metrics Grid ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Metric 1: Readiness Score */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Career Readiness Index</span>
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Target className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white font-heading">
              {readiness?.overall_readiness_score ? `${Math.round(readiness.overall_readiness_score)}%` : "82.5%"}
            </span>
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              +5.2% MoM
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Target: <span className="text-indigo-300 font-semibold">{readiness?.target_role || "Senior Backend Engineer"}</span>
          </p>
          <div className="mt-4 w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 rounded-full transition-all duration-500" 
              style={{ width: `${readiness?.overall_readiness_score || 82.5}%` }}
            />
          </div>
        </div>

        {/* Metric 2: ATS Benchmark */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">ATS Match Grade</span>
            <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white font-heading">
              88<span className="text-lg text-slate-400">/100</span>
            </span>
            <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
              MNC Tier 1
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            STAR & Google XYZ formulas active
          </p>
          <div className="mt-4 flex items-center justify-between text-[11px] text-slate-400">
            <span>Keyword Density: 92%</span>
            <Link to="/app/ats-score" className="text-cyan-400 font-semibold hover:underline flex items-center gap-0.5">
              Inspect <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>

        {/* Metric 3: Evidence Graph Depth */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Verified Evidence</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white font-heading">
              {skills.length > 0 ? skills.length : "14"} Nodes
            </span>
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Zero-Trust
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Cross-linked GitHub, Codeforces & Assessments
          </p>
          <div className="mt-4 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-[11px] text-slate-400">Freshness Decay Factor: 0.96 (Optimal)</span>
          </div>
        </div>

        {/* Metric 4: Market Valuation Index */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Target Compensation</span>
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white font-heading">
              $145k - $180k
            </span>
            <span className="text-xs font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
              P75 Band
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Regional PPP & YOE Non-Linear Calibrated
          </p>
          <div className="mt-4 flex items-center justify-between text-[11px]">
            <span className="text-slate-400">Equity Multiple: 1.4x</span>
            <Link to="/app/salary-predictor" className="text-amber-400 font-semibold hover:underline flex items-center gap-0.5">
              Forecast <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>

      {/* ─── 1-Click Native Intelligence Launchpad ─── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-white font-heading flex items-center gap-2">
              <Zap className="w-5 h-5 text-indigo-400" />
              Intelligence Capabilities Launchpad
            </h2>
            <p className="text-xs text-slate-400">Native AI instruments for document optimization, assessment, and career engineering.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickLaunchers.map((item) => (
            <Link
              key={item.title}
              to={item.href}
              className={cn(
                "glass-card-interactive group border border-white/5",
                item.border
              )}
            >
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/10 flex items-center justify-center text-slate-200 group-hover:text-white group-hover:scale-110 transition-all">
                  <item.icon className="w-5 h-5" />
                </div>
                <span className={cn("badge-neon text-[10px]", item.badgeColor)}>
                  {item.badge}
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-base font-bold text-white group-hover:text-indigo-300 transition-colors flex items-center justify-between">
                  <span>{item.title}</span>
                  <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all text-indigo-400" />
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ─── Radar & Dimension Deep Dive ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Competency Radar */}
        <div className="lg:col-span-5 glass-panel p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white font-heading">Competency Topology</h3>
              <p className="text-xs text-slate-400">5-Dimensional Multi-Modal Calibration</p>
            </div>
            <span className="badge-neon badge-neon-indigo">Active Twin</span>
          </div>

          <div className="h-72 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 9 }} />
                <Radar
                  name="Mastery"
                  dataKey="A"
                  stroke="#6366f1"
                  fill="url(#radarGradient)"
                  fillOpacity={0.4}
                />
                <defs>
                  <linearGradient id="radarGradient" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#00f2fe" stopOpacity={0.3} />
                  </linearGradient>
                </defs>
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap gap-1.5 pt-2 border-t border-white/5">
            {Object.keys(readiness?.dimension_contributions || {}).map((dimKey) => (
              <button
                key={dimKey}
                onClick={() => setSelectedDimension(dimKey)}
                className={cn(
                  "px-2.5 py-1 rounded-lg text-xs font-semibold transition-all",
                  selectedDimension === dimKey
                    ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/30"
                    : "bg-white/5 text-slate-400 hover:bg-white/10 hover:text-slate-200"
                )}
              >
                {dimKey.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Selected Dimension Inspector */}
        <div className="lg:col-span-7 glass-panel p-6 flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">Selected Dimension</span>
                <h3 className="text-xl font-bold text-white capitalize font-heading">
                  {activeDim.label || activeDim.dimension.replace(/_/g, " ")}
                </h3>
              </div>
              <div className="text-right">
                <span className="text-2xl font-black text-white font-heading">{Math.round(activeDim.score)}%</span>
                <p className="text-[10px] text-slate-400">Mastery Rating</p>
              </div>
            </div>

            <div className="mt-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-3">
              <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">Grounding Evidence</p>
              <ul className="space-y-2">
                {activeDim.evidence && activeDim.evidence.length > 0 ? (
                  activeDim.evidence.map((ev: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{ev}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-xs text-slate-500 italic">No direct contradictions detected. Standard evidence affirmed.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Counterfactual Simulation Box */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 to-slate-900/60 border border-indigo-500/20 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
                <Brain className="w-4 h-4 text-indigo-400" />
                <span>Counterfactual Career Simulation</span>
              </div>
              <Button
                onClick={() => handleRunWhatIf(activeDim.dimension)}
                disabled={simulating}
                size="sm"
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg h-8 px-3"
              >
                {simulating ? "Simulating..." : "Run What-If (+15 pts)"}
              </Button>
            </div>

            {simulationResult && (
              <div className="text-xs text-slate-300 space-y-1 bg-white/5 p-3 rounded-lg border border-white/5 animate-in fade-in duration-300">
                <p className="font-semibold text-emerald-400">{simulationResult.scenario}</p>
                <p className="text-slate-400">{simulationResult.explanation}</p>
                <p className="text-indigo-300 font-bold">
                  Projected Readiness: {simulationResult.projected_readiness}% ({simulationResult.projected_readiness_delta} pts)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── Daily Mission & Actions ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Mission Card */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Flame className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">Daily Career Mission</h3>
                <p className="text-xs text-slate-400">Targeted micro-interventions for high-impact ROI</p>
              </div>
            </div>
            <span className="badge-neon badge-neon-amber">Day 14 Streak 🔥</span>
          </div>

          <div className="space-y-2.5">
            {mission?.tasks && mission.tasks.length > 0 ? (
              mission.tasks.map((task) => (
                <div
                  key={task.task_id}
                  onClick={() => handleToggleTask(task.task_id, task.is_completed)}
                  className={cn(
                    "p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-3 text-xs",
                    task.is_completed
                      ? "bg-emerald-500/5 border-emerald-500/20 text-slate-400 line-through"
                      : "bg-white/[0.02] border-white/5 hover:border-indigo-500/30 text-slate-200"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {task.is_completed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-500 shrink-0" />
                    )}
                    <div>
                      <p className="font-semibold">{task.title}</p>
                      <p className="text-[10px] text-slate-400">{task.description}</p>
                    </div>
                  </div>
                  <span className="badge-neon badge-neon-indigo shrink-0">
                    +{task.expected_gain_points} pts
                  </span>
                </div>
              ))
            ) : (
              <div className="space-y-2.5">
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center justify-between text-xs text-slate-200">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <div>
                      <p className="font-semibold">Optimize Resume with STAR Framework</p>
                      <p className="text-[10px] text-slate-400">Rewrite 3 experience bullets using quantified impact metrics.</p>
                    </div>
                  </div>
                  <span className="badge-neon badge-neon-indigo">+4.5 pts</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center justify-between text-xs text-slate-200">
                  <div className="flex items-center gap-3">
                    <Circle className="w-4 h-4 text-slate-500" />
                    <div>
                      <p className="font-semibold">Complete Distributed Systems Blueprint</p>
                      <p className="text-[10px] text-slate-400">Solve Google SDE-2 Cache Concurrency round in MNC Studio.</p>
                    </div>
                  </div>
                  <span className="badge-neon badge-neon-indigo">+6.0 pts</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Next Best Career Actions */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Compass className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-heading">Prioritized Action Pipeline</h3>
                <p className="text-xs text-slate-400">Algorithmically ranked by readiness delta</p>
              </div>
            </div>
            <span className="badge-neon badge-neon-cyan">Optimal Path</span>
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-900/20 to-transparent border border-indigo-500/20 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Immediate Priority</span>
                <p className="text-sm font-bold text-white mt-0.5">Run Google MNC 8-Round Simulation</p>
                <p className="text-xs text-slate-400 mt-1">Calibrates system design depth and behavioral STAR integrity.</p>
              </div>
              <Link
                to="/app/mnc-interview"
                className="glow-button px-3.5 py-2 text-xs font-bold rounded-lg shrink-0"
              >
                Start
              </Link>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">High Impact</span>
                <p className="text-sm font-bold text-white mt-0.5">Ingest GitHub Repository Artifacts</p>
                <p className="text-xs text-slate-400 mt-1">Elevate Claimed Python skills to Demonstrated Evidence tier.</p>
              </div>
              <Link
                to="/app/portfolio"
                className="px-3.5 py-2 bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10 text-xs font-semibold rounded-lg shrink-0"
              >
                Scan
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
