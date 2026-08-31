import { Eye, TrendingUp, CheckCircle2, AlertCircle, Calendar, Brain } from 'lucide-react';

const MOCK_DATA = {
  student_name: 'Priyansh Sharma',
  overall_placement_readiness: 8.4,
  completed_interviews_count: 6,
  strongest_topics: ['Data Structures', 'Dynamic Programming', 'Python Basics'],
  needs_review: ['System Design Scalability', 'Concurrency'],
  recent_activity: [
    { date: '2026-06-20', event: 'Completed Amazon Behavioral Mock', score: '8.8/10', positive: true },
    { date: '2026-06-18', event: 'Uploaded Resume — ATS Score 85%', score: 'High Match', positive: true },
    { date: '2026-06-15', event: 'Gap Analysis Updated — 3 Critical Gaps', score: 'Needs Work', positive: false },
  ],
};

export const ParentDashboard = () => (
  <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <header>
      <div className="flex items-center gap-3 mb-1">
        <Eye className="w-6 h-6 text-purple-400" />
        <span className="text-xs text-slate-500 font-bold uppercase tracking-widest">Read-Only Parent View</span>
      </div>
      <h2 className="text-3xl font-bold text-slate-50">Monitoring: <span className="text-indigo-400">{MOCK_DATA.student_name}</span></h2>
      <p className="text-slate-400 mt-1">You can view your child's placement preparation progress here.</p>
    </header>

    {/* Readiness Score */}
    <div className="bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-3xl p-8 flex items-center gap-8">
      <div className="relative w-28 h-28 shrink-0">
        <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
          <circle cx="18" cy="18" r="15" fill="none" stroke="#1e293b" strokeWidth="3" />
          <circle cx="18" cy="18" r="15" fill="none" stroke="#6366F1" strokeWidth="3" strokeDasharray={`${MOCK_DATA.overall_placement_readiness * 9.42} 100`} strokeLinecap="round" />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-2xl font-black text-white">{MOCK_DATA.overall_placement_readiness}</span>
      </div>
      <div>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Overall Placement Readiness</p>
        <p className="text-slate-200 mt-2 text-lg">Your child is performing <span className="text-emerald-400 font-bold">above average</span> with {MOCK_DATA.completed_interviews_count} mock interviews completed.</p>
      </div>
    </div>

    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-slate-950 border border-white/10 rounded-2xl p-6">
        <h3 className="font-bold text-slate-50 mb-4 flex items-center gap-2"><CheckCircle2 className="w-5 h-5 text-emerald-400" /> Strong Topics</h3>
        <div className="space-y-2">
          {MOCK_DATA.strongest_topics.map(t => <div key={t} className="flex items-center gap-3 text-sm text-slate-300"><CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />{t}</div>)}
        </div>
      </div>
      <div className="bg-slate-950 border border-white/10 rounded-2xl p-6">
        <h3 className="font-bold text-slate-50 mb-4 flex items-center gap-2"><AlertCircle className="w-5 h-5 text-amber-400" /> Needs Review</h3>
        <div className="space-y-2">
          {MOCK_DATA.needs_review.map(t => <div key={t} className="flex items-center gap-3 text-sm text-slate-300"><AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />{t}</div>)}
        </div>
      </div>
    </div>

    <div className="bg-slate-950 border border-white/10 rounded-3xl p-8">
      <h3 className="font-bold text-slate-50 mb-6 flex items-center gap-2"><Calendar className="w-5 h-5 text-cyan-400" /> Recent Activity</h3>
      <div className="divide-y divide-white/5">
        {MOCK_DATA.recent_activity.map((a, i) => (
          <div key={i} className="flex items-center gap-4 py-4">
            <span className={`w-2 h-2 rounded-full shrink-0 ${a.positive ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            <div className="flex-1">
              <p className="text-sm text-slate-200">{a.event}</p>
              <p className="text-xs text-slate-500 mt-1">{a.date}</p>
            </div>
            <span className={`text-xs font-bold px-3 py-1 rounded-full ${a.positive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>{a.score}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);
