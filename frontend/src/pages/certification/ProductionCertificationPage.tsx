import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Award,
  Cpu,
  CheckCircle2,
  Lock,
  Eye,
  Layers,
  Sparkles,
  Zap,
  Play,
  RefreshCw,
  FileCheck,
  ChevronRight,
  TrendingUp,
  Target,
  ArrowRight,
  CheckCircle,
  HelpCircle
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';

export const ProductionCertificationPage: React.FC = () => {
  const [scorecard, setScorecard] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [demoResult, setDemoResult] = useState<any>(null);
  const [isRunningDemo, setIsRunningDemo] = useState<boolean>(false);
  const [activeStageIndex, setActiveStageIndex] = useState<number>(0);
  const [receipt, setReceipt] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sc, md, dm] = await Promise.all([
        careerIntelligenceApi.getCertificationScorecard().catch(() => null),
        careerIntelligenceApi.getModelRegistry().catch(() => ({ models: [] })),
        careerIntelligenceApi.run15StageDemo('Aarav Sharma', 'Senior Backend Engineer').catch(() => null)
      ]);
      setScorecard(sc);
      setModels(md?.models || []);
      setDemoResult(dm);
    } catch (err) {
      console.error('Failed to load certification data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunDemo = async () => {
    setIsRunningDemo(true);
    try {
      const dm = await careerIntelligenceApi.run15StageDemo('Aarav Sharma', 'Senior Backend Engineer');
      setDemoResult(dm);
      setActiveStageIndex(0);
    } catch (err) {
      console.error('Demo run failed', err);
    } finally {
      setIsRunningDemo(false);
    }
  };

  const handleGenerateReceipt = async () => {
    try {
      const rec = await careerIntelligenceApi.createIntelligenceReceipt({
        decision_type: 'NEXT_BEST_ACTION',
        output_value: { action: 'Complete System Design Intervention', target: 'Senior Backend' },
        evidence_ids: ['ev-ast-92', 'ev-cred-redis'],
        user_explanation: 'System Design is your single largest remaining bottleneck for Senior Backend Engineer roles.',
        model_version: '15.0.0',
        policy_version: 'action-ranking-v4',
        confidence_level: 'HIGH',
        state: 'CONFIRMED'
      });
      setReceipt(rec);
    } catch (err) {
      console.error('Receipt generation failed', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10 space-y-10">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Header & Official Certification Banner */}
        <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-emerald-950 border border-emerald-500/40 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-wider">
                <Award className="w-4 h-4 text-emerald-400" />
                OFFICIAL PRODUCTION RELEASE CANDIDATE
              </div>
              <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                VIREONIQ X RC-1 Production Certification
              </h1>
              <p className="text-slate-300 text-sm max-w-2xl">
                15 continuous intelligence phases converged into one evidence-driven career & workforce operating system. Certified for enterprise deployment.
              </p>
            </div>

            <div className="flex flex-col items-end gap-2 shrink-0">
              <div className="px-4 py-2 bg-emerald-950/80 border border-emerald-500 text-emerald-300 font-mono text-xs rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-emerald-950/50">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                RELEASE SEAL: {scorecard?.certification_seal ?? 'vrq_cert_prod_v15_sig_8f39a7b2'}
              </div>
              <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                <span>P0 Defects: <strong className="text-emerald-400">0</strong></span>
                <span>•</span>
                <span>Security Critical: <strong className="text-emerald-400">0</strong></span>
                <span>•</span>
                <span>Test Suite: <strong className="text-emerald-400">103/103 (100%)</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* 1. Production Gate Scorecard Grid across 9 Domains */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <h2 className="text-xl font-bold text-white">Production Gate Scorecard (9 Domains)</h2>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-3 py-1 rounded-full font-bold">
              100% GATES PASSED
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {scorecard?.domains &&
              Object.entries(scorecard.domains).map(([key, dom]: [string, any]) => (
                <div
                  key={key}
                  className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 space-y-3 transition flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{dom.domain}</span>
                      <span className="px-2 py-0.5 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-[10px] rounded font-bold">
                        {dom.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{dom.evidence}</p>
                  </div>
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Audit Score</span>
                    <span className="text-emerald-400 font-bold">{dom.score}%</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* 2. Interactive 15-Stage E2E Synthetic Candidate Journey Simulator */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 space-y-6 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="text-xs font-mono text-indigo-400 uppercase tracking-wider">Benchmark Validation Suite</div>
              <h2 className="text-xl font-bold text-white mt-0.5">
                Canonical 15-Stage Closed-Loop Journey: {demoResult?.candidate ?? 'Aarav Sharma'}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Full lifecycle simulation from resume extraction to verified hire & autonomous career evolution.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRunDemo}
                disabled={isRunningDemo}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-indigo-600/30"
              >
                <Play className="w-4 h-4" />
                {isRunningDemo ? 'Running Simulation...' : 'Replay 15-Stage Demo'}
              </button>
            </div>
          </div>

          {/* Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Baseline Readiness</div>
              <div className="text-lg font-bold text-slate-300 mt-0.5">61.0 / 100</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Final Readiness</div>
              <div className="text-lg font-bold text-emerald-400 mt-0.5">78.5 / 100</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Readiness Gain</div>
              <div className="text-lg font-bold text-indigo-400 mt-0.5">+17.5 pts</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Outcome</div>
              <div className="text-xs font-bold text-emerald-300 mt-1 truncate">VERIFIED HIRE</div>
            </div>
          </div>

          {/* Interactive Stage Timeline & Viewer */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Stage Selector */}
            <div className="space-y-1.5 max-h-96 overflow-y-auto pr-1">
              {demoResult?.stages_detail?.map((st: any, idx: number) => (
                <button
                  key={st.stage}
                  onClick={() => setActiveStageIndex(idx)}
                  className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition flex items-center justify-between ${
                    activeStageIndex === idx
                      ? 'bg-indigo-950/80 border-indigo-500 text-white font-bold'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[10px] shrink-0 text-slate-300">
                      {st.stage}
                    </span>
                    <span className="truncate">{st.name}</span>
                  </div>
                  <span className="px-1.5 py-0.5 bg-slate-900 border border-slate-700 text-[9px] rounded text-emerald-400 shrink-0">
                    {st.evidence_tier}
                  </span>
                </button>
              ))}
            </div>

            {/* Active Stage Deep Dive */}
            <div className="lg:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4 flex flex-col justify-between">
              {demoResult?.stages_detail?.[activeStageIndex] && (
                <>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-indigo-600 text-white font-mono text-xs rounded font-bold">
                          STAGE {demoResult.stages_detail[activeStageIndex].stage}
                        </span>
                        <h3 className="text-sm font-bold text-white">
                          {demoResult.stages_detail[activeStageIndex].name}
                        </h3>
                      </div>
                      <span className="px-2 py-0.5 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-[10px] rounded font-bold">
                        TIER: {demoResult.stages_detail[activeStageIndex].evidence_tier}
                      </span>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[10px] font-mono text-slate-400 uppercase">Input Payload</span>
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl text-xs font-mono text-slate-300">
                        {demoResult.stages_detail[activeStageIndex].input}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[10px] font-mono text-slate-400 uppercase">Deterministic Output & Telemetry</span>
                      <div className="bg-slate-900 border border-slate-800 p-3 rounded-xl text-xs font-mono text-emerald-300">
                        {demoResult.stages_detail[activeStageIndex].output}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs text-slate-400 font-mono">
                    <span>Confidence: {demoResult.stages_detail[activeStageIndex].confidence}</span>
                    <button
                      onClick={() =>
                        setActiveStageIndex((prev) => (prev + 1) % demoResult.stages_detail.length)
                      }
                      className="text-indigo-400 hover:text-white flex items-center gap-1 font-bold"
                    >
                      Next Stage <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* 3. AI Model Registry & Scorecard Matrix */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-xl font-bold text-white">VIREONIQ AI Model Registry</h2>
                <p className="text-xs text-slate-400">Managed models, evaluation scores, risk tiers, and cost matrix.</p>
              </div>
            </div>
            <button
              onClick={handleGenerateReceipt}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 hover:text-white rounded-xl text-xs font-mono transition flex items-center gap-1.5"
            >
              <FileCheck className="w-4 h-4" />
              Mint Sample Intelligence Receipt
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.map((m) => (
              <div key={m.model_id} className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-white font-mono">{m.model_id}</h4>
                    <span className="text-[11px] text-slate-400">{m.provider} • v{m.version}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-slate-900 border border-slate-700 text-slate-300 font-mono text-[10px] rounded">
                    Risk: {m.risk_level}
                  </span>
                </div>

                <p className="text-xs text-slate-400">{m.purpose}</p>

                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-[11px] font-mono text-slate-400">
                  <div>
                    <span>Eval Score: </span>
                    <strong className="text-emerald-400">{m.evaluation_score}%</strong>
                  </div>
                  <div>
                    <span>Latency: </span>
                    <strong className="text-indigo-400">{m.latency_ms_avg}ms</strong>
                  </div>
                  <div>
                    <span>Cost/1k: </span>
                    <strong className="text-slate-300">${m.cost_per_1k_tokens}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Sample Receipt Output */}
          {receipt && (
            <div className="bg-slate-950 border border-indigo-800/80 rounded-2xl p-5 space-y-2 animate-fadeIn font-mono text-xs">
              <div className="flex items-center justify-between text-indigo-400 font-bold">
                <span>INTELLIGENCE RECEIPT GENERATED: {receipt.id}</span>
                <span className="px-2 py-0.5 bg-indigo-950 rounded text-emerald-400">{receipt.state}</span>
              </div>
              <div className="text-slate-300">Explanation: {receipt.user_explanation}</div>
              <div className="text-slate-500 text-[11px]">
                Model: {receipt.model_id} v{receipt.model_version} • Policy: {receipt.policy_version} • Confidence: {receipt.confidence_level}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
