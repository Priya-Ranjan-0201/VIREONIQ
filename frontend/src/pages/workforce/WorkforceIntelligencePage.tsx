import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Layers,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  GitPullRequest,
  BarChart3,
  Search,
  Briefcase,
  Play
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type {
  OrganizationCapabilitiesData,
  WorkforceCriticalGapItem,
  WorkforceConcentrationRiskItem
} from '@/api/careerIntelligenceApi';

export const WorkforceIntelligencePage: React.FC = () => {
  const [capabilities, setCapabilities] = useState<OrganizationCapabilitiesData | null>(null);
  const [matrixData, setMatrixData] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCompetency, setSelectedCompetency] = useState<string>('Kubernetes');
  const [tradeoffs, setTradeoffs] = useState<any | null>(null);
  const [mobilityData, setMobilityData] = useState<any | null>(null);

  // Counterfactual Simulation state
  const [upskillCount, setUpskillCount] = useState<number>(3);
  const [hireCount, setHireCount] = useState<number>(1);
  const [simResult, setSimResult] = useState<any | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [capRes, matRes, mobRes] = await Promise.all([
        careerIntelligenceApi.getOrganizationCapabilities(),
        careerIntelligenceApi.getWorkforceCapabilityMatrix(),
        careerIntelligenceApi.getInternalTalentMobility('Platform Engineer')
      ]);
      setCapabilities(capRes);
      setMatrixData(matRes);
      setMobilityData(mobRes);

      if (capRes.critical_gaps.length > 0) {
        const firstComp = capRes.critical_gaps[0].competency;
        setSelectedCompetency(firstComp);
        const tradeRes = await careerIntelligenceApi.getHiringVsUpskillingTradeoffs(firstComp);
        setTradeoffs(tradeRes);
      }
    } catch (err) {
      console.error('Failed to load workforce intelligence data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectCompetency = async (comp: string) => {
    setSelectedCompetency(comp);
    try {
      const res = await careerIntelligenceApi.getHiringVsUpskillingTradeoffs(comp);
      setTradeoffs(res);
    } catch (err) {
      console.error('Failed to load tradeoffs', err);
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    try {
      const res = await careerIntelligenceApi.simulateWorkforceChange(null, {
        target_skill: selectedCompetency,
        upskill_count: upskillCount,
        hire_count: hireCount
      });
      setSimResult(res);
    } catch (err) {
      console.error('Simulation failed', err);
    } finally {
      setSimulating(false);
    }
  };

  if (loading || !capabilities) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 font-mono text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-indigo-400" />
        Synthesizing Organizational Digital Twin & Capability Mapping...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Building2 className="w-4 h-4 text-emerald-400" />
              VIREONIQ Employer Intelligence v8.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Workforce Skills & Capability Mapping
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Organizational digital twin measuring credible workforce capabilities, critical bottlenecks, and hiring vs. upskilling decision support.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => careerIntelligenceApi.takeOrganizationSnapshot()}
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3.5 py-2 rounded-lg border border-slate-700 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Capture Snapshot
            </button>
          </div>
        </div>

        {/* 1. Hero Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
            <span className="text-[11px] font-mono text-slate-400">Capability Coverage</span>
            <div className="text-3xl font-bold text-white">{capabilities.overall_coverage_pct}%</div>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> {capabilities.confidence} CONFIDENCE
            </span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
            <span className="text-[11px] font-mono text-slate-400">Critical Capability Gaps</span>
            <div className="text-3xl font-bold text-rose-400">{capabilities.critical_gaps_count}</div>
            <span className="text-[10px] font-mono text-slate-500">Requires Strategic Action</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
            <span className="text-[11px] font-mono text-slate-400">Concentration Risks</span>
            <div className="text-3xl font-bold text-amber-400">{capabilities.concentration_risks_count}</div>
            <span className="text-[10px] font-mono text-amber-500">Key-Person Dependencies</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
            <span className="text-[11px] font-mono text-slate-400">Evidence Coverage</span>
            <div className="text-3xl font-bold text-indigo-400">{capabilities.evidence_coverage_pct}%</div>
            <span className="text-[10px] font-mono text-slate-500">Assessed Competencies</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1 col-span-2 md:col-span-1">
            <span className="text-[11px] font-mono text-slate-400">Primary Bottleneck</span>
            <div className="text-lg font-bold text-amber-300 truncate">{capabilities.primary_bottleneck}</div>
            <span className="text-[10px] font-mono text-slate-500">Restricts Team Velocity</span>
          </div>
        </div>

        {/* 2. Critical Gaps & Concentration Risks */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Critical Capability Gaps */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                Critical Capability Gaps
              </h3>
              <span className="text-xs font-mono text-slate-400">High Criticality (&gt;85)</span>
            </div>

            <div className="space-y-3">
              {capabilities.critical_gaps.map((gap) => (
                <div
                  key={gap.competency}
                  onClick={() => handleSelectCompetency(gap.competency)}
                  className={`p-4 rounded-xl border transition cursor-pointer ${
                    selectedCompetency === gap.competency
                      ? 'bg-rose-950/20 border-rose-500/50'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-sm text-white">{gap.competency}</h4>
                      <p className="text-xs text-slate-400 mt-0.5">{gap.diagnosis}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-rose-400">{gap.coverage_pct}%</div>
                      <div className="text-[10px] font-mono text-slate-500">{gap.shortage_type}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key-Person & Concentration Risks */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Single-Point Concentration Risks
              </h3>
              <span className="text-xs font-mono text-slate-400">Resilience Invariant</span>
            </div>

            <div className="space-y-3">
              {capabilities.concentration_risks.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  No single-point concentration risks detected across active teams.
                </div>
              ) : (
                capabilities.concentration_risks.map((risk) => (
                  <div key={risk.competency} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-sm text-white">{risk.competency}</h4>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-amber-950 border border-amber-800 text-amber-300 rounded font-semibold">
                        {risk.risk_level} RISK
                      </span>
                    </div>
                    <p className="text-xs text-slate-300">{risk.diagnosis}</p>
                    <div className="text-[11px] font-mono text-slate-500">
                      Recommendation: Cross-train 2-3 engineers to eliminate single-point bottleneck.
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 3. Decision Support: Hiring vs. Upskilling Tradeoffs */}
        {tradeoffs && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <div className="text-xs font-mono text-indigo-400">Decision Support Engine</div>
                <h3 className="text-lg font-bold text-white">
                  Strategy Tradeoffs for: <span className="text-indigo-300">{selectedCompetency}</span>
                </h3>
              </div>
              <span className="text-xs font-mono text-slate-400">
                Evidence-driven qualitative feasibility
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {tradeoffs.strategies.map((strat: any) => (
                <div
                  key={strat.strategy}
                  className={`p-4 rounded-xl border space-y-3 ${
                    strat.suitability === 'RECOMMENDED'
                      ? 'bg-indigo-950/30 border-indigo-500/60'
                      : 'bg-slate-950 border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-white">{strat.strategy}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                      strat.suitability === 'RECOMMENDED'
                        ? 'bg-indigo-900 text-indigo-200'
                        : 'bg-slate-800 text-slate-300'
                    }`}>
                      {strat.suitability}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-300">
                    <div><strong className="text-slate-400">Impact:</strong> {strat.projected_impact}</div>
                    <div><strong className="text-slate-400">Timeframe:</strong> {strat.estimated_timeframe}</div>
                    <div><strong className="text-slate-400">Effort:</strong> {strat.effort_level}</div>
                  </div>

                  <p className="text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                    {strat.tradeoffs}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 4. Counterfactual Simulation Sandbox */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <div className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" />
                Zero-Mutation Simulation Sandbox
              </div>
              <h3 className="text-lg font-bold text-white">
                Workforce Capability What-If Simulator
              </h3>
            </div>

            <button
              onClick={handleRunSimulation}
              disabled={simulating}
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition"
            >
              <Play className="w-3.5 h-3.5" />
              {simulating ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="text-slate-400 font-mono">Target Competency</label>
              <select
                value={selectedCompetency}
                onChange={(e) => setSelectedCompetency(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              >
                {capabilities.competencies.map(c => (
                  <option key={c.competency} value={c.competency}>{c.competency}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 font-mono">Engineers to Upskill</label>
              <input
                type="number"
                min="0"
                max="20"
                value={upskillCount}
                onChange={(e) => setUpskillCount(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              >
              </input>
            </div>

            <div>
              <label className="text-slate-400 font-mono">External Hires to Inject</label>
              <input
                type="number"
                min="0"
                max="10"
                value={hireCount}
                onChange={(e) => setHireCount(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
              >
              </input>
            </div>
          </div>

          {simResult && (
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="flex items-center justify-between font-bold">
                <span className="text-white">Simulation Projected Results:</span>
                <span className="text-emerald-400 font-mono">
                  +{simResult.projected_coverage_delta}% Overall Delta
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-[11px]">
                <div className="p-3 bg-slate-900 rounded-lg">
                  <div className="text-slate-500">Current Overall</div>
                  <div className="text-white font-bold">{simResult.current_overall_coverage}%</div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg">
                  <div className="text-slate-500">Projected Overall</div>
                  <div className="text-emerald-400 font-bold">{simResult.projected_overall_coverage}%</div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg col-span-2">
                  <div className="text-slate-500">Assumptions</div>
                  <div className="text-slate-300 truncate">{simResult.assumptions}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 5. Internal Talent Mobility & Project Staffing */}
        {mobilityData && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-indigo-400" />
                  Internal Talent Mobility Explorer
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Surfacing qualified internal candidates for: <strong className="text-slate-200">{mobilityData.target_role}</strong>
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {mobilityData.eligible_internal_candidates_count} Eligible Employees
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {mobilityData.top_internal_matches.map((cand: any) => (
                <div key={cand.employee_id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-sm text-white">{cand.name}</h4>
                      <span className="text-xs text-slate-400">{cand.current_role}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-base font-bold text-indigo-400">{cand.internal_match_score}%</div>
                      <div className="text-[10px] font-mono text-emerald-400">{cand.confidence} CONF</div>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300">{cand.readiness_recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
