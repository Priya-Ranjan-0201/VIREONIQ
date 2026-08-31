import { useState, useEffect } from 'react';
import { Activity, Cpu, AlertTriangle, CheckCircle2, Zap, Clock } from 'lucide-react';

const MOCK_EVENTS = [
  { session: 'Amazon Mock - Session 4', question: 3, load_score: 0.82, action: 'difficulty_reduced', before: 6.5, after: 6.0, signals: { long_pauses: 4, backspace_rate: 0.38 } },
  { session: 'Google Mock - Session 2', question: 7, load_score: 0.21, action: 'difficulty_increased', before: 5.0, after: 5.25, signals: { long_pauses: 0, backspace_rate: 0.05 } },
  { session: 'Flipkart Mock - Session 1', question: 5, load_score: 0.76, action: 'difficulty_reduced', before: 7.0, after: 6.5, signals: { long_pauses: 3, backspace_rate: 0.31 } },
  { session: 'TCS Mock - Session 3', question: 2, load_score: 0.18, action: 'difficulty_increased', before: 4.0, after: 4.25, signals: { long_pauses: 0, backspace_rate: 0.03 } },
];

const LOAD_COLOR = (score: number) => score >= 0.75 ? '#EF4444' : score >= 0.4 ? '#F59E0B' : '#10B981';
const LOAD_LABEL = (score: number) => score >= 0.75 ? 'Overloaded' : score >= 0.4 ? 'Moderate' : 'Underloaded';

export const CognitiveLoadMonitorPage = () => {
  const avgLoad = MOCK_EVENTS.reduce((a, e) => a + e.load_score, 0) / MOCK_EVENTS.length;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h2 className="text-3xl font-bold text-slate-50 flex items-center gap-3"><Activity className="w-8 h-8 text-cyan-400" /> Cognitive Load Monitor</h2>
        <p className="text-slate-400 mt-2">Real-time keystroke telemetry tracks your mental load and adapts difficulty automatically.</p>
      </header>

      {/* Avg load indicator */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Avg Load Score', value: `${Math.round(avgLoad * 100)}%`, icon: Cpu, color: 'text-cyan-400' },
          { label: 'High-Load Events', value: MOCK_EVENTS.filter(e => e.load_score >= 0.75).length, icon: AlertTriangle, color: 'text-red-400' },
          { label: 'Auto-Adjustments', value: MOCK_EVENTS.length, icon: Zap, color: 'text-yellow-400' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-950 border border-white/10 rounded-2xl p-5">
            <stat.icon className={`w-6 h-6 ${stat.color} mb-3`} />
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{stat.label}</p>
            <p className={`text-3xl font-black ${stat.color} mt-1`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-slate-950 border border-white/10 rounded-3xl p-8">
        <h3 className="font-bold text-slate-50 mb-6">Load Events Log</h3>
        <div className="space-y-4">
          {MOCK_EVENTS.map((ev, i) => (
            <div key={i} className="border border-white/5 rounded-2xl p-5 hover:bg-white/5 transition-all">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-bold text-slate-100 text-sm">{ev.session}</p>
                  <p className="text-xs text-slate-500 mt-1">Question #{ev.question}</p>
                </div>
                <span className="px-3 py-1 rounded-full text-[10px] font-bold" style={{ background: LOAD_COLOR(ev.load_score) + '20', color: LOAD_COLOR(ev.load_score) }}>
                  {LOAD_LABEL(ev.load_score)} — {Math.round(ev.load_score * 100)}%
                </span>
              </div>
              <div className="flex gap-6 text-xs text-slate-400">
                <span>Long Pauses: <strong className="text-slate-200">{ev.signals.long_pauses}</strong></span>
                <span>Backspace Rate: <strong className="text-slate-200">{Math.round(ev.signals.backspace_rate * 100)}%</strong></span>
                <span>Difficulty: <strong className="text-slate-200">{ev.before} → {ev.after}</strong></span>
                <span className="ml-auto">
                  {ev.action === 'difficulty_reduced' ? <span className="text-red-400">⬇ Reduced</span> : <span className="text-emerald-400">⬆ Increased</span>}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
