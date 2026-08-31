import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  ChevronRight,
  Search,
  Briefcase,
  MapPin,
  Sparkles,
  Code2,
  Award,
  ArrowUpRight,
  CheckCircle2,
  X,
  Layers,
  Cpu,
  Clock
} from 'lucide-react';
import { COMPANY_PROFILES, CompanyProfile } from './companyProfilesData';

const DIFFICULTY_COLOR: Record<string, string> = {
  Expert: 'text-red-400 bg-red-500/10 border border-red-500/20',
  Hard: 'text-amber-400 bg-amber-500/10 border border-amber-500/20',
  Medium: 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20',
};

const TYPE_BORDER: Record<string, string> = {
  FAANG: 'border-indigo-500/30 hover:border-indigo-500/60 hover:shadow-indigo-500/10',
  Product: 'border-cyan-500/30 hover:border-cyan-500/60 hover:shadow-cyan-500/10',
  FinTech: 'border-violet-500/30 hover:border-violet-500/60 hover:shadow-violet-500/10',
  Service: 'border-slate-700/60 hover:border-slate-500 hover:shadow-slate-500/10',
  Startup: 'border-emerald-500/30 hover:border-emerald-500/60 hover:shadow-emerald-500/10',
};

const TYPE_BADGE: Record<string, string> = {
  FAANG: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
  Product: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  FinTech: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
  Service: 'text-slate-300 bg-slate-800 border-slate-700',
  Startup: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};

const ROLE_FILTERS = [
  { key: 'all', label: 'All Roles' },
  { key: 'sde', label: 'SDE & Full-Stack' },
  { key: 'backend', label: 'Backend & Systems' },
  { key: 'data_ai', label: 'AI & Data Platforms' },
  { key: 'devops', label: 'Cloud & Infrastructure' },
  { key: 'service', label: 'Digital Specialist' },
];

export const CompanyProfilesPage = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('All');
  const [filterRole, setFilterRole] = useState('all');
  const [selected, setSelected] = useState<CompanyProfile | null>(null);

  const filtered = useMemo(() => {
    return COMPANY_PROFILES.filter((c) => {
      const matchType = filterType === 'All' || c.type === filterType;
      const matchRole = filterRole === 'all' || c.roleCategory === filterRole;
      const q = search.toLowerCase().trim();
      const matchSearch =
        !q ||
        c.name.toLowerCase().includes(q) ||
        c.primaryRole.toLowerCase().includes(q) ||
        c.jobProfiles.some((jp) => jp.toLowerCase().includes(q)) ||
        c.techStack.some((ts) => ts.toLowerCase().includes(q)) ||
        c.location.toLowerCase().includes(q);

      return matchType && matchRole && matchSearch;
    });
  }, [search, filterType, filterRole]);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-16">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black text-slate-50 flex items-center gap-3 tracking-tight">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/5">
              <Building2 className="w-5 h-5" />
            </div>
            Company Interview Profiles
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
            Study real hiring loops, authentic brand logos, exact job profiles, salary benchmarks (CTC), and bar-raiser rubrics for 35+ top tech titans.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/app/mnc-interview')}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-cyan-600/20 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Open MNC Studio
          </button>
        </div>
      </header>

      {/* Filter Toolbar */}
      <div className="space-y-3 bg-slate-900/60 p-4 rounded-2xl border border-white/5 backdrop-blur-md">
        <div className="flex gap-3 flex-wrap">
          {/* Search bar */}
          <div className="flex-1 min-w-[260px] relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies, job profiles (e.g. SDE-1, SRE), tech stack..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-white/10 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-cyan-500/50 transition-all font-medium placeholder:text-slate-600"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
              >
                Clear
              </button>
            )}
          </div>

          {/* Company Type Chips */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {['All', 'FAANG', 'Product', 'FinTech', 'Service', 'Startup'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                  filterType === t
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25'
                    : 'bg-slate-950/80 border border-white/10 text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Job Profile Role Filter Chips */}
        <div className="flex items-center gap-2 pt-2 border-t border-white/5 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-500 font-semibold flex items-center gap-1 shrink-0">
            <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
            Job Profile:
          </span>
          <div className="flex items-center gap-1.5">
            {ROLE_FILTERS.map((r) => (
              <button
                key={r.key}
                onClick={() => setFilterRole(r.key)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all shrink-0 ${
                  filterRole === r.key
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 border border-white/5'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
          <span className="ml-auto text-slate-500 text-xs shrink-0 pl-2">
            Showing <strong className="text-white">{filtered.length}</strong> companies
          </span>
        </div>
      </div>

      {/* Grid of Company Cards */}
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((c) => (
          <div
            key={c.key}
            onClick={() => setSelected(c)}
            className={`group text-left bg-slate-900/90 hover:bg-slate-900 border rounded-2xl p-5 transition-all duration-200 cursor-pointer shadow-lg hover:-translate-y-1 flex flex-col justify-between ${
              TYPE_BORDER[c.type] || 'border-white/10'
            }`}
          >
            <div>
              {/* Card Header: Official Brand Logo + Difficulty Pill */}
              <div className="flex items-start justify-between mb-3.5">
                <div className="w-12 h-12 rounded-xl bg-slate-950 border border-white/10 flex items-center justify-center p-1.5 shadow-inner group-hover:scale-105 transition-transform">
                  {c.renderLogo()}
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${TYPE_BADGE[c.type]}`}>
                    {c.type}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${DIFFICULTY_COLOR[c.difficulty]}`}>
                    {c.difficulty}
                  </span>
                </div>
              </div>

              {/* Company Name & CTC */}
              <div className="mb-2">
                <h4 className="font-extrabold text-base text-slate-100 group-hover:text-cyan-400 transition-colors flex items-center justify-between">
                  {c.name}
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-cyan-400 opacity-0 group-hover:opacity-100 transition-all" />
                </h4>
                <p className="text-xs font-semibold text-emerald-400 font-mono mt-0.5">
                  {c.ctc}
                </p>
              </div>

              {/* Job Profile Badge (User Request) */}
              <div className="mb-3">
                <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl px-2.5 py-1.5 flex items-start gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-bold text-indigo-200 truncate" title={c.primaryRole}>
                      {c.primaryRole}
                    </p>
                    <p className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <MapPin className="w-2.5 h-2.5 text-slate-500 shrink-0" />
                      <span className="truncate">{c.experienceLevel}</span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Stages Preview */}
              <div className="space-y-1.5 mb-3 bg-slate-950/60 p-2.5 rounded-xl border border-white/5">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Hiring Stages</p>
                {c.stages.slice(0, 2).map((s) => (
                  <p key={s} className="text-[11px] text-slate-300 flex items-center gap-1.5 truncate" title={s}>
                    <ChevronRight className="w-3 h-3 text-cyan-400 shrink-0" />
                    <span className="truncate">{s}</span>
                  </p>
                ))}
                {c.stages.length > 2 && (
                  <p className="text-[10px] text-cyan-400 font-medium pl-4">
                    +{c.stages.length - 2} more rounds...
                  </p>
                )}
              </div>
            </div>

            {/* Weights & Tech Stack Footer */}
            <div>
              {/* Tech Stack Pills */}
              <div className="flex flex-wrap gap-1 mb-3">
                {c.techStack.slice(0, 3).map((tech) => (
                  <span
                    key={tech}
                    className="text-[10px] px-1.5 py-0.5 bg-slate-950 border border-slate-800 text-slate-400 rounded-md font-mono"
                  >
                    {tech}
                  </span>
                ))}
                {c.techStack.length > 3 && (
                  <span className="text-[10px] px-1.5 py-0.5 text-slate-500 font-mono">
                    +{c.techStack.length - 3}
                  </span>
                )}
              </div>

              {/* Skill Weight Distribution */}
              <div className="pt-3 border-t border-white/5 flex gap-1.5">
                <div className="flex-1 text-center bg-slate-950/50 py-1 px-1 rounded-lg">
                  <p className="text-[9px] text-slate-500 uppercase font-semibold">DSA</p>
                  <p className="text-xs font-black text-cyan-400">{c.weights.DSA}%</p>
                </div>
                <div className="flex-1 text-center bg-slate-950/50 py-1 px-1 rounded-lg">
                  <p className="text-[9px] text-slate-500 uppercase font-semibold">System</p>
                  <p className="text-xs font-black text-indigo-400">{c.weights.System}%</p>
                </div>
                <div className="flex-1 text-center bg-slate-950/50 py-1 px-1 rounded-lg">
                  <p className="text-[9px] text-slate-500 uppercase font-semibold">Behavioral</p>
                  <p className="text-xs font-black text-amber-400">{c.weights.Behavioral}%</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* No Results Fallback */}
      {filtered.length === 0 && (
        <div className="text-center py-16 bg-slate-900/40 rounded-3xl border border-white/5 p-8">
          <Building2 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h4 className="text-lg font-bold text-slate-300">No companies found</h4>
          <p className="text-sm text-slate-500 mt-1">Try clearing your search query or selecting 'All' filters.</p>
          <button
            onClick={() => {
              setSearch('');
              setFilterType('All');
              setFilterRole('all');
            }}
            className="mt-4 px-4 py-2 bg-cyan-600 text-white rounded-xl text-xs font-bold"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Comprehensive Detail Modal */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 overflow-y-auto"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700/60 rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-6 my-8 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header: Logo, Company Name, CTC & Close */}
            <div className="flex items-start justify-between pb-5 border-b border-slate-800">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-slate-950 border border-white/10 flex items-center justify-center p-2 shadow-inner">
                  {selected.renderLogo()}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-2xl font-black text-white">{selected.name}</h3>
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${DIFFICULTY_COLOR[selected.difficulty]}`}>
                      {selected.difficulty}
                    </span>
                  </div>
                  <p className="text-slate-400 text-xs mt-1 flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded font-bold ${TYPE_BADGE[selected.type]}`}>{selected.type}</span>
                    <span>•</span>
                    <span className="text-emerald-400 font-mono font-bold text-sm">{selected.ctc}</span>
                    <span>•</span>
                    <span className="text-slate-400">{selected.location}</span>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Target Job Profiles (User Requested Focus) */}
            <div className="space-y-2.5">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
                Target Job Profiles & Roles
              </h4>
              <div className="grid sm:grid-cols-2 gap-2">
                {selected.jobProfiles.map((role, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-950/70 border border-white/5 text-xs text-slate-200"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span className="font-semibold">{role}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Full Interview Loop Stages */}
            <div className="space-y-2.5">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                Complete Interview Loop Stages
              </h4>
              <div className="space-y-2">
                {selected.stages.map((stage, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 bg-slate-950/60 rounded-xl border border-white/5 text-xs text-slate-300"
                  >
                    <span className="w-6 h-6 bg-cyan-500/20 text-cyan-300 rounded-full flex items-center justify-center text-xs font-black shrink-0">
                      {i + 1}
                    </span>
                    <span className="font-medium text-slate-200 leading-snug">{stage}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Skill Weight Distribution Progress Bars */}
            <div className="space-y-3 bg-slate-950/70 p-4 rounded-2xl border border-white/5">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-amber-400" />
                Evaluation Rubric Weights
              </h4>
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-semibold">DSA & Algorithmic Optimization</span>
                    <span className="text-cyan-400 font-mono font-bold">{selected.weights.DSA}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div className="bg-cyan-500 h-2 rounded-full" style={{ width: `${selected.weights.DSA}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-semibold">System Architecture & LLD/HLD</span>
                    <span className="text-indigo-400 font-mono font-bold">{selected.weights.System}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${selected.weights.System}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-semibold">Behavioral & Leadership Principles</span>
                    <span className="text-amber-400 font-mono font-bold">{selected.weights.Behavioral}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${selected.weights.Behavioral}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-semibold">Core CS Fundamentals (OS, DBMS, OOP)</span>
                    <span className="text-emerald-400 font-mono font-bold">{selected.weights.CoreCS}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${selected.weights.CoreCS}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Bar Raiser Secret Tip Banner */}
            <div className="bg-amber-500/10 border border-amber-500/20 p-4 rounded-2xl space-y-1.5">
              <div className="flex items-center gap-2 text-amber-400 text-xs font-bold">
                <Sparkles className="w-4 h-4" />
                Insider Bar-Raiser Tip for {selected.name}
              </div>
              <p className="text-xs text-amber-200/90 leading-relaxed font-medium">
                {selected.hiringTip}
              </p>
            </div>

            {/* Tech Stack & Culture Pillars */}
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Production Tech Stack</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selected.techStack.map((tech) => (
                    <span key={tech} className="text-xs px-2 py-0.5 bg-slate-950 border border-slate-800 text-slate-300 rounded-md font-mono">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Culture Pillars & Values</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selected.culturePillars.map((pillar) => (
                    <span key={pillar} className="text-xs px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-md font-medium">
                      {pillar}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-800">
              <button
                onClick={() => {
                  setSelected(null);
                  navigate('/app/mnc-interview');
                }}
                className="flex-1 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-cyan-600/25 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Start {selected.name} Calibrated Simulator
              </button>
              <button
                onClick={() => {
                  setSelected(null);
                  navigate('/app/coding-interview');
                }}
                className="py-3 px-5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-bold text-sm transition-all border border-slate-700 flex items-center justify-center gap-2"
              >
                <Code2 className="w-4 h-4" />
                Practice Sandbox
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
