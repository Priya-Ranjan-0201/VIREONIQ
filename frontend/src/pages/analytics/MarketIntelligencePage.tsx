import { useState } from 'react';
import { TrendingUp, TrendingDown, BarChart3, Briefcase, AlertCircle, DollarSign, Download } from 'lucide-react';
import { toast } from 'sonner';

const MOCK_INTEL = {
  role_category: 'Software Engineer',
  week_start_date: '2026-06-16',
  jd_count_analyzed: 3420,
  trending_skills: [
    { skill: 'React / Next.js', demand_score: 92 },
    { skill: 'FastAPI / Python', demand_score: 88 },
    { skill: 'LangChain / LLMOps', demand_score: 87 },
    { skill: 'Qdrant / Vector DB', demand_score: 85 },
    { skill: 'Docker / Kubernetes', demand_score: 82 },
    { skill: 'GraphQL', demand_score: 74 },
  ],
  declining_skills: [
    { skill: 'jQuery', demand_score: 15 },
    { skill: 'SOAP APIs', demand_score: 12 },
    { skill: 'Angular 1.x', demand_score: 9 },
    { skill: 'Monolithic MVC', demand_score: 8 },
  ],
  salary_signals: { p50: 1200000, p75: 1800000, p90: 2400000 },
};

const formatLPA = (n: number) => `₹${(n / 100000).toFixed(1)} LPA`;

export const MarketIntelligencePage = () => {
  const [data] = useState(MOCK_INTEL);

  const handleExport = () => {
    try {
      const headers = "Skill,Demand Score\n";
      const rows = data.trending_skills.map(s => `"${s.skill}",${s.demand_score}`).join("\n");
      const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(headers + rows);
      const link = document.createElement("a");
      link.setAttribute("href", csvContent);
      link.setAttribute("download", `market_intelligence_report_${data.role_category.replace(/\\s+/g, '_')}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Market report exported successfully! 📊");
    } catch (e) {
      console.error(e);
      toast.error("Failed to export report.");
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-50 flex items-center gap-3"><BarChart3 className="w-8 h-8 text-emerald-400" /> Market Intelligence</h2>
          <p className="text-slate-400 mt-2">Live job market signals for <span className="text-white font-bold">{data.role_category}</span> — updated weekly.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-slate-950 border border-white/10 rounded-xl text-sm text-slate-400">
            <Briefcase className="w-4 h-4 inline mr-2" />{data.jd_count_analyzed.toLocaleString()} JDs Analyzed
          </div>
          <button 
            onClick={handleExport}
            className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-bold flex items-center gap-2 hover:bg-primary/90 transition-all"
          >
            <Download className="w-4 h-4" /> Export Report
          </button>
        </div>
      </header>

      {/* Salary Signals */}
      <div className="grid grid-cols-3 gap-4">
        {[['Median (P50)', data.salary_signals.p50, 'text-yellow-400'], ['75th Pct', data.salary_signals.p75, 'text-orange-400'], ['90th Pct', data.salary_signals.p90, 'text-emerald-400']].map(([label, val, color]) => (
          <div key={String(label)} className="bg-slate-950 border border-white/10 rounded-2xl p-5 text-center">
            <DollarSign className="w-6 h-6 mx-auto mb-2 text-slate-500" />
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">{label}</p>
            <p className={`text-2xl font-black ${color}`}>{formatLPA(Number(val))}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Trending */}
        <div className="bg-slate-950 border border-white/10 rounded-3xl p-6">
          <h3 className="font-bold text-slate-50 mb-5 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-400" /> Rising Demand</h3>
          <div className="space-y-3">
            {data.trending_skills.map((s) => (
              <div key={s.skill}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-slate-300">{s.skill}</span>
                  <span className="text-sm font-bold text-emerald-400">{s.demand_score}</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full" style={{ width: `${s.demand_score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Declining */}
        <div className="bg-slate-950 border border-white/10 rounded-3xl p-6">
          <h3 className="font-bold text-slate-50 mb-5 flex items-center gap-2"><TrendingDown className="w-5 h-5 text-red-400" /> Losing Relevance</h3>
          <div className="space-y-3">
            {data.declining_skills.map((s) => (
              <div key={s.skill}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-slate-400">{s.skill}</span>
                  <span className="text-sm font-bold text-red-400">{s.demand_score}</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full" style={{ width: `${s.demand_score}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex gap-3">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-xs text-amber-300">These skills are rapidly losing demand. Upskill to modern alternatives.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
