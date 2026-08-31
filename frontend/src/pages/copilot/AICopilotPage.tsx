import React, { useState, useEffect } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Terminal,
  Activity,
  DollarSign,
  Clock,
  User,
  Building2,
  Briefcase,
  Cpu,
  RefreshCw,
  EyeOff
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { CopilotChatResponse, AIObservabilityData } from '@/api/careerIntelligenceApi';

export const AICopilotPage: React.FC = () => {
  const [roleMode, setRoleMode] = useState<'CANDIDATE' | 'RECRUITER' | 'EMPLOYER'>('CANDIDATE');
  const [targetRole, setTargetRole] = useState<string>('Backend Engineer');
  const [inputMessage, setInputMessage] = useState<string>('Why am I not ready for Backend Engineer?');
  const [messages, setMessages] = useState<Array<{ sender: 'USER' | 'AI'; data: any }>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<AIObservabilityData | null>(null);

  const loadTelemetry = async () => {
    try {
      const data = await careerIntelligenceApi.getAIObservabilityMetrics();
      setTelemetry(data);
    } catch (err) {
      console.error('Failed to load telemetry', err);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;
    const userMsg = inputMessage;
    setInputMessage('');
    setMessages(prev => [...prev, { sender: 'USER', data: { text: userMsg } }]);
    setLoading(true);

    try {
      const res: CopilotChatResponse = await careerIntelligenceApi.sendCopilotMessage(userMsg, roleMode, targetRole);
      setMessages(prev => [...prev, { sender: 'AI', data: res }]);
      await loadTelemetry();
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'AI',
        data: {
          status: 'ERROR',
          answer: 'An unexpected error occurred while communicating with the AI Orchestrator.'
        }
      }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
    // Default welcome message
    setMessages([
      {
        sender: 'AI',
        data: {
          status: 'SUCCESS',
          answer: `Welcome to the VIREONIQ AI Copilot (v10.0.0). Operating in ${roleMode} Mode with tool grounding and authorization guards.`,
          confidence: 'HIGH',
          structured_response: {
            facts: ['Authorized tool execution enabled.'],
            inferences: ['Operating under strict role permission matrix.'],
            recommendations: ['Ask about your readiness, gaps, or request candidate/workforce evaluations.'],
            projections: ['Real-time evidence synthesis active.']
          }
        }
      }
    ]);
  }, [roleMode]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Bot className="w-4 h-4 text-emerald-400" />
              VIREONIQ AI Orchestration Fabric v10.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              AI Intelligence Copilot & Operations
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Tool-grounded, evidence-aware, and authorization-scoped conversational intelligence.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-xs rounded-full font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              ORCHESTRATOR ONLINE
            </span>
          </div>
        </div>

        {/* Mode Selector & Telemetry Banner */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Mode Selector */}
          <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-400 uppercase">Actor Role:</span>
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-mono">
                <button
                  onClick={() => setRoleMode('CANDIDATE')}
                  className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
                    roleMode === 'CANDIDATE' ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <User className="w-3.5 h-3.5" /> Candidate
                </button>
                <button
                  onClick={() => setRoleMode('RECRUITER')}
                  className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
                    roleMode === 'RECRUITER' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Briefcase className="w-3.5 h-3.5" /> Recruiter
                </button>
                <button
                  onClick={() => setRoleMode('EMPLOYER')}
                  className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
                    roleMode === 'EMPLOYER' ? 'bg-amber-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Building2 className="w-3.5 h-3.5" /> Employer
                </button>
              </div>
            </div>

            <div className="text-xs font-mono text-slate-400">
              Target Blueprint: <span className="text-white font-bold">{targetRole}</span>
            </div>
          </div>

          {/* Telemetry Stat */}
          {telemetry && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between font-mono text-xs">
              <div>
                <div className="text-slate-500">Latency / Success</div>
                <div className="text-white font-bold text-sm mt-0.5">{telemetry.average_latency_ms}ms · {telemetry.success_rate_pct}%</div>
              </div>
              <Activity className="w-6 h-6 text-indigo-400" />
            </div>
          )}
        </div>

        {/* Chat Stream & Response Cards */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 min-h-[480px] flex flex-col justify-between">
          <div className="space-y-6 overflow-y-auto max-h-[560px] pr-2">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex ${m.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
                {m.sender === 'USER' ? (
                  <div className="max-w-xl bg-indigo-600 text-white p-4 rounded-2xl rounded-tr-none text-sm shadow-lg shadow-indigo-600/10">
                    {m.data.text}
                  </div>
                ) : (
                  <div className="max-w-2xl bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none p-5 space-y-4 shadow-xl">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-2">
                        <Bot className="w-4 h-4 text-indigo-400" />
                        <span className="text-xs font-mono font-bold text-white">VIREONIQ Orchestrator</span>
                      </div>
                      {m.data.status === 'DENIED' ? (
                        <span className="px-2 py-0.5 bg-rose-950 border border-rose-800 text-rose-300 font-mono text-[10px] rounded font-bold">
                          SECURITY RESTRICTION
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-[10px] rounded font-bold">
                          GROUNDED EVIDENCE
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-slate-200 leading-relaxed">
                      {m.data.answer}
                    </p>

                    {/* Structured Response Tags */}
                    {m.data.structured_response && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-slate-800/80 text-xs font-mono">
                        {m.data.structured_response.facts?.length > 0 && (
                          <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1">
                            <span className="text-emerald-400 font-bold flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> [FACT]
                            </span>
                            {m.data.structured_response.facts.map((f: string, i: number) => (
                              <div key={i} className="text-slate-300 text-[11px]">{f}</div>
                            ))}
                          </div>
                        )}

                        {m.data.structured_response.inferences?.length > 0 && (
                          <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1">
                            <span className="text-indigo-400 font-bold flex items-center gap-1">
                              <Sparkles className="w-3.5 h-3.5" /> [INFERENCE]
                            </span>
                            {m.data.structured_response.inferences.map((inf: string, i: number) => (
                              <div key={i} className="text-slate-300 text-[11px]">{inf}</div>
                            ))}
                          </div>
                        )}

                        {m.data.structured_response.recommendations?.length > 0 && (
                          <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1">
                            <span className="text-amber-400 font-bold flex items-center gap-1">
                              <Layers className="w-3.5 h-3.5" /> [RECOMMENDATION]
                            </span>
                            {m.data.structured_response.recommendations.map((r: string, i: number) => (
                              <div key={i} className="text-slate-300 text-[11px]">{r}</div>
                            ))}
                          </div>
                        )}

                        {m.data.structured_response.projections?.length > 0 && (
                          <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1">
                            <span className="text-purple-400 font-bold flex items-center gap-1">
                              <Activity className="w-3.5 h-3.5" /> [PROJECTION]
                            </span>
                            {m.data.structured_response.projections.map((p: string, i: number) => (
                              <div key={i} className="text-slate-300 text-[11px]">{p}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Message Input Box */}
          <div className="flex items-center gap-3 pt-4 border-t border-slate-800">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={`Ask ${roleMode.toLowerCase()} copilot (e.g. Why am I weak in System Design?)...`}
              className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !inputMessage.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-medium text-sm transition flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Executing...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
