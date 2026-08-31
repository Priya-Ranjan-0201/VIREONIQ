import React, { useState, useEffect } from 'react';
import {
  Compass,
  Sparkles,
  TrendingUp,
  Clock,
  CheckCircle2,
  ArrowRight,
  Layers,
  BarChart3,
  Columns,
  RefreshCw,
  GitBranch,
  Shield,
  HelpCircle,
  Play,
  Check,
  ChevronRight
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { CareerScenarioData } from '@/api/careerIntelligenceApi';

export const CareerSimulatorPage: React.FC = () => {
  const [targetRole, setTargetRole] = useState<string>('Cybersecurity Engineer');
  const [simulationType, setSimulationType] = useState<string>('ROLE_SWITCH');
  const [dailyTimeMin, setDailyTimeMin] = useState<number>(60);
  const [targetSkill, setTargetSkill] = useState<string>('Threat Detection');
  const [targetScore, setTargetScore] = useState<number>(85);
  
  const [activeScenario, setActiveScenario] = useState<CareerScenarioData | null>(null);
  const [history, setHistory] = useState<CareerScenarioData[]>([]);
  const [pathComparisons, setPathComparisons] = useState<any | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [converting, setConverting] = useState<boolean>(false);
  const [convertedPlan, setConvertedPlan] = useState<any | null>(null);

  const loadScenarios = async () => {
    try {
      const [histRes, compRes] = await Promise.all([
        careerIntelligenceApi.listCareerScenarios(),
        careerIntelligenceApi.compareCareerPaths(['Backend Engineer', 'Cybersecurity Engineer', 'Platform Engineer', 'AI/ML Engineer'])
      ]);
      setHistory(histRes);
      setPathComparisons(compRes);
      if (histRes.length > 0) {
        setActiveScenario(histRes[0]);
      } else {
        // Run initial default scenario
        await handleRunSimulation();
      }
    } catch (err) {
      console.error('Failed to load scenarios', err);
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    setConvertedPlan(null);
    try {
      const res = await careerIntelligenceApi.runCareerScenario({
        target_role: targetRole,
        simulation_type: simulationType,
        scenario_actions: [
          { skill_name: targetSkill, action_type: 'ASSESSMENT', target_score: targetScore },
          { skill_name: 'Distributed Systems', action_type: 'BUILD_PROJECT', target_score: 80 }
        ],
        assumptions: { time_budget_daily_min: dailyTimeMin }
      });
      setActiveScenario(res);
      const hist = await careerIntelligenceApi.listCareerScenarios();
      setHistory(hist);
    } catch (err) {
      console.error('Simulation failed', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleConvertToPlan = async () => {
    if (!activeScenario) return;
    setConverting(true);
    try {
      const res = await careerIntelligenceApi.convertScenarioToPlan(activeScenario.simulation_id);
      setConvertedPlan(res);
    } catch (err) {
      console.error('Conversion failed', err);
    } finally {
      setConverting(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4 text-emerald-400" />
              VIREONIQ Career Simulator v9.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Counterfactual Career Planning
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Safely explore "What If" career decisions, role transitions, and skill investments in a zero-mutation isolated sandbox.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-amber-950 border border-amber-800 text-amber-300 font-mono text-xs rounded-full font-bold">
              ZERO-MUTATION SANDBOX
            </span>
          </div>
        </div>

        {/* 1. What If Scenario Builder */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Configure Counterfactual Scenario
            </h3>
            <span className="text-xs font-mono text-slate-400">Isolated Sandbox</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
            <div>
              <label className="text-slate-400">Target Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              >
                <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
                <option value="Platform Engineer">Platform Engineer</option>
                <option value="Cloud Engineer">Cloud Engineer</option>
                <option value="AI/ML Engineer">AI/ML Engineer</option>
                <option value="Backend Engineer">Backend Engineer (Deep Mastery)</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400">Simulation Mode</label>
              <select
                value={simulationType}
                onChange={(e) => setSimulationType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              >
                <option value="ROLE_SWITCH">Role Switch & Transfer</option>
                <option value="SKILL_INVESTMENT">Skill Investment</option>
                <option value="PROJECT_INVESTMENT">Project Investment</option>
                <option value="TIME_INVESTMENT">Time Availability Adaptation</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400">Time Budget (min/day)</label>
              <input
                type="number"
                min="15"
                max="180"
                step="15"
                value={dailyTimeMin}
                onChange={(e) => setDailyTimeMin(parseInt(e.target.value) || 60)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              />
            </div>

            <div>
              <label className="text-slate-400">Target Competency</label>
              <input
                type="text"
                value={targetSkill}
                onChange={(e) => setTargetSkill(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              />
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={simulating}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg text-sm transition shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4" />
            {simulating ? 'Computing Counterfactual Projection...' : 'Simulate Scenario Projection'}
          </button>
        </div>

        {/* 2. Side-by-Side Current vs. Projected Visualizer */}
        {activeScenario && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current Real Baseline */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-mono text-slate-400">REAL STATE (Production)</span>
                <span className="text-xs font-mono text-emerald-400">Active Career Twin v2.0.0</span>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-bold text-white">Current Career Readiness</div>
                  <div className="text-3xl font-bold text-white">
                    {activeScenario.projected_readiness.current_score}%
                  </div>
                </div>

                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs">
                  <div className="font-semibold text-slate-300">Transferable Capabilities:</div>
                  <div className="space-y-1">
                    {activeScenario.projected_gaps?.transferable_skills?.map((t) => (
                      <div key={t.skill_name} className="flex items-center justify-between text-emerald-400">
                        <span>{t.skill_name} ({t.current_tier})</span>
                        <span className="font-mono text-[10px]">{t.transfer_tier}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Projected Counterfactual Scenario */}
            <div className="bg-slate-900 border border-indigo-500/50 rounded-2xl p-6 space-y-6 bg-indigo-950/10">
              <div className="flex items-center justify-between border-b border-indigo-900/50 pb-3">
                <span className="text-xs font-mono text-indigo-400 font-bold flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  SIMULATED PROJECTION
                </span>
                <span className="px-2 py-0.5 bg-indigo-950 border border-indigo-700 text-indigo-300 font-mono text-[10px] rounded font-bold">
                  NOT VERIFIED
                </span>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-white">Projected Readiness Range</div>
                    <span className="text-xs font-mono text-slate-400">
                      {activeScenario.projected_readiness.confidence} Confidence
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-indigo-400">
                      {activeScenario.projected_readiness.projected_range[0]} - {activeScenario.projected_readiness.projected_range[1]}%
                    </div>
                  </div>
                </div>

                {/* Best / Base / Conservative Cases */}
                <div className="grid grid-cols-3 gap-2 font-mono text-center text-xs">
                  <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-500">Conservative</div>
                    <div className="font-bold text-slate-300">{activeScenario.projected_readiness.conservative_case}%</div>
                  </div>
                  <div className="p-2.5 bg-slate-950 rounded-lg border border-indigo-800">
                    <div className="text-[10px] text-indigo-400">Base Case</div>
                    <div className="font-bold text-white">{activeScenario.projected_readiness.base_case}%</div>
                  </div>
                  <div className="p-2.5 bg-slate-950 rounded-lg border border-emerald-800">
                    <div className="text-[10px] text-emerald-400">Best Case</div>
                    <div className="font-bold text-emerald-300">{activeScenario.projected_readiness.best_case}%</div>
                  </div>
                </div>

                {/* Timeline & Sensitivity */}
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Estimated Effort:</span>
                    <span className="text-white font-mono">{activeScenario.timeline_estimate?.estimated_effort_hours}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Timeline:</span>
                    <span className="text-indigo-300 font-mono">{activeScenario.timeline_estimate?.estimated_duration_days} Days</span>
                  </div>
                </div>

                {/* Turn Scenario to Plan Action */}
                <button
                  onClick={handleConvertToPlan}
                  disabled={converting}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 rounded-lg text-xs transition flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {converting ? 'Generating Roadmap...' : 'Turn This Scenario Into 14-Day Career Plan'}
                </button>

                {convertedPlan && (
                  <div className="p-3 bg-emerald-950/40 border border-emerald-800 rounded-xl text-xs text-emerald-300 font-mono">
                    ✓ Activated Intervention Plan: {convertedPlan.title} ({convertedPlan.tasks_count} tasks).
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 3. Career Path Comparison Matrix */}
        {pathComparisons && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Columns className="w-5 h-5 text-indigo-400" />
                  Multi-Path Career Decision Matrix
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Side-by-side strategic comparison of adjacent career pathways.
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400">
                Strongest Fit: {pathComparisons.decision_recommendation.strongest_current_fit}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
              {pathComparisons.comparison_matrix.map((p: any) => (
                <div key={p.target_role} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                  <div>
                    <h5 className="font-bold text-white text-sm">{p.target_role}</h5>
                    <div className="text-indigo-400 font-bold text-lg mt-1">{p.adjacency_score}% Adjacency</div>
                    <span className="text-[10px] text-slate-500">Current Fit: {p.current_fit}</span>
                  </div>

                  <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-[11px]">
                    <div>Current: {p.current_readiness}%</div>
                    <div>Projected: {p.projected_readiness_range[0]}-{p.projected_readiness_range[1]}%</div>
                    <div>Effort: {p.estimated_effort}</div>
                    <div className="text-emerald-400">Upside: {p.strategic_upside}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
