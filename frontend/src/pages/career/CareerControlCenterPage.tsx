import React, { useState, useEffect } from 'react';
import {
  Compass,
  Sparkles,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Shield,
  ShieldAlert,
  ArrowRight,
  Flame,
  Layers,
  HelpCircle,
  XCircle,
  RefreshCw,
  BellRing,
  Activity,
  FileQuestion,
  Power
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';

export const CareerControlCenterPage: React.FC = () => {
  const [brief, setBrief] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [goals, setGoals] = useState<any>(null);
  const [preferences, setPreferences] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showWhyModal, setShowWhyModal] = useState<boolean>(false);
  const [showDisputeModal, setShowDisputeModal] = useState<boolean>(false);
  const [disputeReason, setDisputeReason] = useState<string>('');
  const [disputeSuccess, setDisputeSuccess] = useState<boolean>(false);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [b, s, g, p] = await Promise.all([
        careerIntelligenceApi.getDailyCareerBrief().catch(() => null),
        careerIntelligenceApi.getCareerSignals().catch(() => []),
        careerIntelligenceApi.getCareerGoalsAndDrift('Backend Engineer').catch(() => null),
        careerIntelligenceApi.getAutomationPreferences().catch(() => null)
      ]);
      setBrief(b);
      setSignals(s || []);
      setGoals(g);
      setPreferences(p);
    } catch (err) {
      console.error('Failed to load career control data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDismissSignal = async (sigId: string) => {
    try {
      await careerIntelligenceApi.dismissCareerSignal(sigId);
      setSignals(signals.filter(s => s.id !== sigId));
    } catch (err) {
      console.error('Failed to dismiss signal', err);
    }
  };

  const handleExecuteAction = async (actionType: string) => {
    try {
      const res = await careerIntelligenceApi.executeCareerAction(actionType, true);
      setActionSuccessMessage(`Action executed: ${res.execution_status}`);
      setTimeout(() => setActionSuccessMessage(null), 4000);
      loadData();
    } catch (err) {
      console.error('Failed to execute action', err);
    }
  };

  const handleFileDispute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disputeReason.trim()) return;
    try {
      await careerIntelligenceApi.submitEvidenceDispute('00000000-0000-0000-0000-000000000001', disputeReason);
      setDisputeSuccess(true);
      setDisputeReason('');
      setTimeout(() => {
        setDisputeSuccess(false);
        setShowDisputeModal(false);
      }, 2500);
    } catch (err) {
      console.error('Failed to submit dispute', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4 text-emerald-400" />
              VIREONIQ Autonomous Career OS v14.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Your Career Control Center
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Proactive continuous intelligence, signal detection, next best actions, and goal evolution under strict user control.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-xs rounded-full font-bold flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-emerald-400" />
              AUTONOMY LEVEL 3 (USER-CONFIRMED)
            </span>
            <button
              onClick={loadData}
              className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white rounded-xl transition"
              title="Refresh Intelligence"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Action Success Toast */}
        {actionSuccessMessage && (
          <div className="bg-emerald-950 border border-emerald-800 text-emerald-300 px-4 py-3 rounded-xl text-sm flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            {actionSuccessMessage}
          </div>
        )}

        {/* 1. Hero: Goal & Longitudinal Trajectory */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Primary Career Goal</span>
              <Target className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              {goals?.primary_goal ?? 'Senior Backend Engineer'}
            </div>
            <p className="text-[11px] text-emerald-400 font-mono">
              Status: {goals?.health_status ?? 'ON_TRACK'}
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Verified Readiness</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-bold text-emerald-400 tracking-tight">
              78.5 <span className="text-sm font-normal text-slate-400">/ 100</span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Trajectory: ↑ Improving (+4.0 pts 7d)
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Verified Competencies</span>
              <CheckCircle2 className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-bold text-white tracking-tight">
              {brief?.progress_telemetry?.verified_competencies_count ?? 3} Badges
            </div>
            <p className="text-[11px] text-indigo-400 font-mono">
              Cryptographically signed proof
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Active Career Signals</span>
              <BellRing className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-bold text-amber-400 tracking-tight">
              {signals.length} Moments
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Filtered for high actionability
            </p>
          </div>
        </div>

        {/* Goal Drift Alert Banner */}
        {goals?.drift_detected && (
          <div className="bg-amber-950/40 border border-amber-800 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-bold text-amber-300">Career Goal Drift Detected</h3>
                <p className="text-xs text-slate-300 mt-0.5">{goals?.drift_details?.observation}</p>
                <p className="text-xs text-amber-200/80 mt-1 font-mono">{goals?.drift_details?.prompt}</p>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              <button
                onClick={() => handleExecuteAction('SWITCH_GOAL_CYBERSECURITY')}
                className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold transition"
              >
                Update Goal
              </button>
              <button
                onClick={() => setGoals({ ...goals, drift_detected: false })}
                className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-400 rounded-lg text-xs transition"
              >
                Keep Current
              </button>
            </div>
          </div>
        )}

        {/* 2. Today's Priority: Next Best Action Card */}
        <div className="bg-gradient-to-br from-slate-900 via-indigo-950/30 to-slate-900 border border-indigo-900/60 rounded-3xl p-6 lg:p-8 space-y-6 shadow-xl relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-indigo-800/40 pb-4">
            <div className="flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-indigo-400" />
              <div>
                <div className="text-xs font-mono text-indigo-300 uppercase tracking-wider">Today's Single Priority</div>
                <h2 className="text-xl font-bold text-white mt-0.5">
                  {brief?.today_priority?.title ?? 'Complete System Design Benchmark Assessment'}
                </h2>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 font-mono text-xs rounded-full">
                Action Score: {brief?.today_priority?.action_value_score ?? '85.0'}/100
              </span>
              <span className="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-xs rounded-full flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {brief?.today_priority?.estimated_minutes ?? 45} mins
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-1">Why This Action?</h4>
                <p className="text-sm text-slate-200 leading-relaxed">
                  {brief?.today_priority?.why_explanation ?? 'System Design is your single largest remaining bottleneck for Senior Backend Engineer roles.'}
                </p>
              </div>

              <div>
                <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-1">Evidence Basis</h4>
                <p className="text-xs text-slate-400 font-mono bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
                  {brief?.today_priority?.evidence_basis ?? 'Current System Design assessment is at Level 2 (CLAIMED); Level 4 (ASSESSED) is required.'}
                </p>
              </div>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
              <div>
                <div className="text-xs font-mono text-slate-400">Feasibility Rating</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {brief?.today_priority?.feasibility ?? 'HIGHLY_FEASIBLE'}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Matches your scheduled daily 45m learning budget.
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <button
                  onClick={() => handleExecuteAction('START_SYSTEM_DESIGN_ASSESSMENT')}
                  className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30"
                >
                  Start Assessment Now
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setShowWhyModal(true)}
                  className="w-full py-1.5 text-indigo-300 hover:text-white text-xs font-mono transition"
                >
                  Inspect Math & Scoring Formula
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Real-Time Career Signals Feed */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Active Career Signals & Moments</h2>
                <p className="text-xs text-slate-400">Filtered events requiring your attention or career validation.</p>
              </div>
            </div>
            <button
              onClick={() => setShowDisputeModal(true)}
              className="text-xs font-mono text-slate-400 hover:text-indigo-300 flex items-center gap-1.5"
            >
              <FileQuestion className="w-3.5 h-3.5" />
              Dispute Evidence
            </button>
          </div>

          <div className="space-y-3">
            {signals.length === 0 ? (
              <p className="text-xs text-slate-500 font-mono">No active signals requiring attention.</p>
            ) : (
              signals.map((sig) => (
                <div key={sig.id} className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 font-mono text-[10px] rounded font-bold">
                        {sig.signal_type}
                      </span>
                      <span className="text-sm font-bold text-white">{sig.recommended_action}</span>
                    </div>
                    <p className="text-xs text-slate-400 font-mono">
                      Confidence: {sig.confidence} • Severity: {sig.severity}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    <button
                      onClick={() => handleExecuteAction(sig.signal_type)}
                      className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white rounded-lg text-xs font-bold transition"
                    >
                      Act
                    </button>
                    <button
                      onClick={() => handleDismissSignal(sig.id)}
                      className="p-1.5 text-slate-500 hover:text-slate-300 hover:bg-slate-900 rounded-lg transition"
                      title="Dismiss Signal"
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 4. Autonomy Settings & Emergency Kill Switch */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <Power className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Autonomous Safety Settings</h2>
                <p className="text-xs text-slate-400">Configure autonomy levels and emergency AI stop controls.</p>
              </div>
            </div>
            <span className="px-2.5 py-1 bg-slate-950 border border-slate-800 text-emerald-400 font-mono text-xs rounded-lg">
              Kill Switch: STANDBY
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 font-mono">Proactive Suggestions</span>
              <div className="text-white font-bold">Enabled (Level 3 Guard)</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 font-mono">High-Impact Actions</span>
              <div className="text-amber-400 font-bold">User Confirmation Required</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 font-mono">Low-Risk Recalculation</span>
              <div className="text-emerald-400 font-bold">Automatic with Audit Trail</div>
            </div>
          </div>
        </div>

        {/* Dispute Evidence Modal */}
        {showDisputeModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 animate-fadeIn">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white">File Evidence Dispute</h3>
                <button onClick={() => setShowDisputeModal(false)} className="text-slate-400 hover:text-white">✕</button>
              </div>

              {disputeSuccess ? (
                <div className="bg-emerald-950 border border-emerald-800 text-emerald-300 p-4 rounded-xl text-sm flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  Dispute filed successfully! Our verification team will review without data loss.
                </div>
              ) : (
                <form onSubmit={handleFileDispute} className="space-y-4">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Reason for Dispute</label>
                    <textarea
                      value={disputeReason}
                      onChange={(e) => setDisputeReason(e.target.value)}
                      placeholder="Explain why this assessment score or skill evidence requires review..."
                      rows={4}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500"
                      required
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setShowDisputeModal(false)}
                      className="px-4 py-2 bg-slate-800 text-slate-400 rounded-xl text-xs"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold"
                    >
                      Submit Dispute
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Why This Math Modal */}
        {showWhyModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 animate-fadeIn">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white">Next Best Action Scoring Formula</h3>
                <button onClick={() => setShowWhyModal(false)} className="text-slate-400 hover:text-white">✕</button>
              </div>
              <div className="text-xs font-mono space-y-2 text-slate-300">
                <p className="text-indigo-400 font-bold">Action Value = (GoalAlign * 0.35 + CapImpact * 0.30 + EvImpact * 0.25 + OppImpact * 0.10) * 100 - EffortPenalty</p>
                <div className="bg-slate-950 p-3 rounded-xl space-y-1 text-slate-400">
                  <div>• Goal Alignment Weight: 35%</div>
                  <div>• Capability Impact Weight: 30%</div>
                  <div>• Evidence Elevation Weight: 25%</div>
                  <div>• Immediate Opportunity Relevance: 10%</div>
                  <div>• Effort Penalty: -5 pts (45 mins)</div>
                </div>
                <p className="text-emerald-400">Score: 85.0 / 100 (HIGHLY_FEASIBLE)</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
