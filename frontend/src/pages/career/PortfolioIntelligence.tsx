import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Globe, GitBranch, Code2, Linkedin, CheckCircle2, AlertTriangle, ArrowRight, 
  Sparkles, RefreshCw, ShieldCheck, Award, Flame, ExternalLink
} from "lucide-react";
import { careerIntelligenceApi } from "@/api/careerIntelligenceApi";
import { toast } from "sonner";

export const PortfolioIntelligence: React.FC = () => {
  const [form, setForm] = useState({
    github_url: "",
    leetcode_user: "",
    codeforces_user: "",
    hackerrank_user: "",
    linkedin_url: ""
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleLoadSample = () => {
    setForm({
      github_url: "https://github.com/alexchen-dev",
      leetcode_user: "alex_algorithms",
      codeforces_user: "alex_code",
      hackerrank_user: "alex_dev",
      linkedin_url: "https://linkedin.com/in/alexchen"
    });
    toast.success("Sample Full-Stack Developer Profiles Loaded!");
  };

  const handleChange = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleAnalyze = async () => {
    if (!form.github_url && !form.leetcode_user && !form.linkedin_url) {
      toast.error("Please provide at least a GitHub URL or LeetCode username.");
      return;
    }
    setLoading(true);
    try {
      const data = await careerIntelligenceApi.analyzeDeveloperPortfolio(form);
      setResult(data);
      toast.success("Developer Evidence Signals Ingested into Graph!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to analyze developer portfolio.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-teal-950/80 via-slate-900/90 to-slate-950/80 border border-white/10 p-6 md:p-8 backdrop-blur-2xl shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-semibold">
              <Globe className="w-3.5 h-3.5" />
              <span>Real-World Developer Evidence Engine</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-white font-heading">
              Multi-Platform Portfolio Intelligence
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl">
              Extracts and ingests verified activity signals from GitHub, LeetCode, Codeforces, and LinkedIn into the canonical Evidence Graph as DEMONSTRATED competencies.
            </p>
          </div>

          <button
            onClick={handleLoadSample}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/10 text-xs font-bold text-slate-200 hover:text-white transition-all hover:scale-105 active:scale-95 shadow-md shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Load Sample Profile Signals</span>
          </button>
        </div>
      </div>

      {/* Profile Form Cards */}
      <div className="bg-slate-900/60 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-xl shadow-xl space-y-6">
        <div className="grid md:grid-cols-2 gap-5">
          {/* GitHub Card */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 focus-within:border-teal-500/50 transition-all">
            <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-teal-400" />
                GitHub Profile URL
              </span>
              <span className="text-[10px] text-teal-400 font-mono">Repositories & Commits</span>
            </label>
            <input
              type="text"
              value={form.github_url}
              onChange={e => handleChange("github_url", e.target.value)}
              placeholder="https://github.com/username"
              className="w-full bg-transparent border-0 text-xs text-slate-200 placeholder-slate-600 focus:outline-none font-mono"
            />
          </div>

          {/* LeetCode Card */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 focus-within:border-amber-500/50 transition-all">
            <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-amber-400" />
                LeetCode Handle
              </span>
              <span className="text-[10px] text-amber-400 font-mono">DSA & Algorithms</span>
            </label>
            <input
              type="text"
              value={form.leetcode_user}
              onChange={e => handleChange("leetcode_user", e.target.value)}
              placeholder="username (e.g. alex_algorithms)"
              className="w-full bg-transparent border-0 text-xs text-slate-200 placeholder-slate-600 focus:outline-none font-mono"
            />
          </div>

          {/* LinkedIn Card */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 focus-within:border-blue-500/50 transition-all">
            <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Linkedin className="w-4 h-4 text-blue-400" />
                LinkedIn Profile URL
              </span>
              <span className="text-[10px] text-blue-400 font-mono">Professional Network</span>
            </label>
            <input
              type="text"
              value={form.linkedin_url}
              onChange={e => handleChange("linkedin_url", e.target.value)}
              placeholder="https://linkedin.com/in/username"
              className="w-full bg-transparent border-0 text-xs text-slate-200 placeholder-slate-600 focus:outline-none font-mono"
            />
          </div>

          {/* Codeforces / HackerRank */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 focus-within:border-indigo-500/50 transition-all">
            <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-indigo-400" />
                Codeforces / HackerRank Handle
              </span>
              <span className="text-[10px] text-indigo-400 font-mono">Competitive Rating</span>
            </label>
            <input
              type="text"
              value={form.codeforces_user}
              onChange={e => handleChange("codeforces_user", e.target.value)}
              placeholder="username (e.g. competitive_alex)"
              className="w-full bg-transparent border-0 text-xs text-slate-200 placeholder-slate-600 focus:outline-none font-mono"
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-teal-400 shrink-0" />
            <span>Signals are ingested directly into the Unified Evidence Graph as <strong>DEMONSTRATED</strong> tier.</span>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="glow-button glow-cyan px-8 py-3.5 text-xs font-bold disabled:opacity-50 flex items-center gap-2 w-full sm:w-auto justify-center"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Harvesting Platform Signals...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Ingest & Fuse Portfolio Signals</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Top Stat Gauges */}
            <div className="grid md:grid-cols-3 gap-4">
              {/* Overall Grade Card */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col items-center justify-center text-center shadow-2xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-teal-500/10 to-transparent pointer-events-none" />
                <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Developer Profile Rating</span>
                
                <div className="my-2 relative flex items-baseline justify-center gap-2">
                  <span className="text-6xl font-black font-heading text-teal-400 tracking-tight">
                    {result.overall_grade}
                  </span>
                  <span className="text-sm font-semibold text-slate-400">Tier</span>
                </div>

                <span className="text-xs text-teal-300 font-semibold px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20">
                  Strength Score: {result.strength_score}/100
                </span>
              </div>

              {/* Ingested Competencies */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Ingested Skill Atoms</span>
                  <p className="text-xs text-slate-400 mt-1 mb-3">Elevated in Evidence Graph</p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.ingested_evidence_skills?.map((s: string, i: number) => (
                      <span key={i} className="px-2.5 py-1 bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs font-semibold rounded-lg">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Graph Status */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Evidence State</span>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    All signals are mapped to <strong>DEMONSTRATED</strong> tier in the PostgreSQL graph. Automatically integrated into the <strong>Career Digital Twin</strong>.
                  </p>
                </div>
                <div className="pt-2 flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Graph Synchronization Active</span>
                </div>
              </div>
            </div>

            {/* Strengths & Growth Recommendations */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Verified Strengths */}
              <div className="bg-slate-900/70 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl space-y-4">
                <h3 className="text-sm font-bold text-teal-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Verified Platform Signals ({result.strengths?.length || 0})</span>
                </h3>

                <div className="space-y-3">
                  {result.strengths?.map((str: string, i: number) => (
                    <div key={i} className="flex items-start gap-3 bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-2xl text-xs text-slate-300 leading-relaxed">
                      <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                      <span>{str}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Growth Recommendations */}
              <div className="bg-slate-900/70 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl space-y-4">
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Evidence Growth Recommendations</span>
                </h3>

                <div className="space-y-3">
                  {result.recommendations?.map((rec: string, i: number) => (
                    <div key={i} className="flex items-start gap-3 bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-2xl text-xs text-slate-300 leading-relaxed">
                      <ArrowRight className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
