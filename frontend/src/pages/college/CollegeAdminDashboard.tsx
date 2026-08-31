import { GraduationCap, Users, Target, AlertTriangle, TrendingUp, BarChart2, Building2, Medal } from 'lucide-react';

const MOCK_DATA = {
  college_name: 'LPU - Lovely Professional University',
  subscription_status: 'Pro Plan · Expires 2027',
  total_enrolled_students: 340,
  placement_readiness_rate: 78.4,
  department_gaps: [
    { dept: 'Computer Science', readiness: 6.8, critical: ['System Design', 'Concurrency'], total: 180 },
    { dept: 'Electronics', readiness: 5.4, critical: ['Data Structures', 'Python Basics'], total: 90 },
    { dept: 'Mechanical', readiness: 4.1, critical: ['Coding Fundamentals', 'OOPs'], total: 70 },
  ],
  top_students: [
    { name: 'Priyansh S.', score: 9.4, branch: 'CSE' },
    { name: 'Aditya V.', score: 8.9, branch: 'CSE' },
    { name: 'Sneha P.', score: 8.5, branch: 'ECE' },
  ],
};

export const CollegeAdminDashboard = () => (
  <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <header>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-50 flex items-center gap-3"><Building2 className="w-8 h-8 text-indigo-400" /> College Admin Dashboard</h2>
          <p className="text-slate-400 mt-1">{MOCK_DATA.college_name}</p>
        </div>
        <span className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-bold rounded-xl">{MOCK_DATA.subscription_status}</span>
      </div>
    </header>

    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[
        { label: 'Total Students', value: MOCK_DATA.total_enrolled_students, icon: Users, color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
        { label: 'Placement Ready', value: `${MOCK_DATA.placement_readiness_rate}%`, icon: Target, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
        { label: 'Departments', value: MOCK_DATA.department_gaps.length, icon: GraduationCap, color: 'text-indigo-400', bg: 'bg-indigo-400/10' },
        { label: 'Top Score', value: `${MOCK_DATA.top_students[0].score}/10`, icon: Medal, color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
      ].map((s) => (
        <div key={s.label} className="bg-slate-950 border border-white/10 rounded-2xl p-5">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${s.bg} mb-3`}><s.icon className={`w-5 h-5 ${s.color}`} /></div>
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{s.label}</p>
          <p className={`text-2xl font-black mt-1 ${s.color}`}>{s.value}</p>
        </div>
      ))}
    </div>

    <div className="grid md:grid-cols-3 gap-6">
      {MOCK_DATA.department_gaps.map(dept => (
        <div key={dept.dept} className="bg-slate-950 border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all">
          <h4 className="font-bold text-slate-100 mb-1">{dept.dept}</h4>
          <p className="text-xs text-slate-500 mb-4">{dept.total} students</p>
          <div className="mb-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-500">Avg Readiness</span>
              <span className={`font-bold ${dept.readiness >= 7 ? 'text-emerald-400' : dept.readiness >= 5 ? 'text-yellow-400' : 'text-red-400'}`}>{dept.readiness}/10</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-full" style={{ width: `${dept.readiness * 10}%` }} />
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {dept.critical.map(c => <span key={c} className="px-2 py-1 text-[10px] font-bold bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg">⚠ {c}</span>)}
          </div>
        </div>
      ))}
    </div>

    <div className="bg-slate-950 border border-white/10 rounded-3xl p-8">
      <h3 className="font-bold text-slate-50 mb-6 flex items-center gap-2"><Medal className="w-5 h-5 text-yellow-400" /> Top Performers</h3>
      <div className="divide-y divide-white/5">
        {MOCK_DATA.top_students.map((s, i) => (
          <div key={s.name} className="flex items-center gap-4 py-4">
            <span className="text-xl">{['🥇', '🥈', '🥉'][i]}</span>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white font-black text-sm">{s.name[0]}</div>
            <div className="flex-1">
              <p className="font-bold text-slate-100 text-sm">{s.name}</p>
              <p className="text-xs text-slate-500">{s.branch}</p>
            </div>
            <span className="text-lg font-black text-yellow-400">{s.score}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);
