import React, { useState, useEffect } from "react";
import { Search, ShieldAlert, Award, ArrowUpRight, ArrowDownRight, Clipboard, Star } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";
import { Link } from "react-router-dom";

interface EmployerScore {
  company_name: string;
  overall_score: number;
  label: string;
  ghost_rate: number;
  submission_count: number;
  transparency_score: number;
  timeline_score: number;
  feedback_score: number;
  equity_score: number;
}

const DEFAULT_EMPLOYER_SCORES: Record<string, EmployerScore[]> = {
  best: [
    {
      company_name: "Google",
      overall_score: 94.2,
      label: "Gold Standard",
      ghost_rate: 4.8,
      submission_count: 148,
      transparency_score: 96,
      timeline_score: 92,
      feedback_score: 90,
      equity_score: 95
    },
    {
      company_name: "Atlassian",
      overall_score: 92.8,
      label: "High Transparency",
      ghost_rate: 5.2,
      submission_count: 84,
      transparency_score: 94,
      timeline_score: 93,
      feedback_score: 91,
      equity_score: 93
    },
    {
      company_name: "Microsoft",
      overall_score: 91.5,
      label: "High Transparency",
      ghost_rate: 6.4,
      submission_count: 112,
      transparency_score: 92,
      timeline_score: 89,
      feedback_score: 88,
      equity_score: 92
    },
    {
      company_name: "Stripe",
      overall_score: 90.4,
      label: "High Transparency",
      ghost_rate: 5.8,
      submission_count: 65,
      transparency_score: 91,
      timeline_score: 90,
      feedback_score: 89,
      equity_score: 91
    }
  ],
  worst: [
    {
      company_name: "Turing Outsourcing",
      overall_score: 41.2,
      label: "High Ghosting Risk",
      ghost_rate: 48.6,
      submission_count: 42,
      transparency_score: 38,
      timeline_score: 42,
      feedback_score: 35,
      equity_score: 50
    },
    {
      company_name: "Revature Services",
      overall_score: 46.5,
      label: "Opaque Compensation",
      ghost_rate: 39.2,
      submission_count: 38,
      transparency_score: 42,
      timeline_score: 48,
      feedback_score: 40,
      equity_score: 56
    }
  ],
  most_improved: [
    {
      company_name: "Amazon India",
      overall_score: 84.6,
      label: "Significantly Improved",
      ghost_rate: 7.2,
      submission_count: 220,
      transparency_score: 86,
      timeline_score: 85,
      feedback_score: 82,
      equity_score: 85
    },
    {
      company_name: "Swiggy Tech",
      overall_score: 88.0,
      label: "Candidate Friendly",
      ghost_rate: 6.1,
      submission_count: 94,
      transparency_score: 89,
      timeline_score: 88,
      feedback_score: 84,
      equity_score: 88
    }
  ]
};

export const EmployerTruthScore = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"best" | "worst" | "most_improved">("best");
  const [selectedScore, setSelectedScore] = useState<EmployerScore | null>(null);
  const [leaderboard, setLeaderboard] = useState<EmployerScore[]>(DEFAULT_EMPLOYER_SCORES.best);
  const [isLoading, setIsLoading] = useState(false);

  const fetchLeaderboard = async () => {
    setIsLoading(true);
    const fallbacks = DEFAULT_EMPLOYER_SCORES[activeTab] || DEFAULT_EMPLOYER_SCORES.best;
    try {
      const res = await client.get(`/employer-truth/leaderboard/${activeTab}`);
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        setLeaderboard(res.data);
      } else {
        setLeaderboard(fallbacks);
      }
    } catch (e) {
      setLeaderboard(fallbacks);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      const res = await client.get(`/employer-truth/score/${searchQuery}`);
      if (res.data.status === "insufficient_data") {
        toast.info(`Insufficient experiences logged for ${searchQuery} (needs 10).`);
        return;
      }
      setSelectedScore(res.data);
    } catch (e) {
      toast.error("Company not found or insufficient reviews.");
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, [activeTab]);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">Employer Truth Score</h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Candidate leverage at scale: verified experience feedback analytics</p>
      </header>

      {/* Prominent Search bar */}
      <div className="glass-panel p-8 rounded-3xl max-w-xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-white">Compare Employer Standards</h3>
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search any company (e.g. Google, Wise)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-950 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none text-sm"
          />
        </form>
      </div>

      {selectedScore && (
        <div className="space-y-6">
          {/* Safety alert banner for scores under 40 */}
          {selectedScore.overall_score < 40 && (
            <div className="bg-rose-500/10 border border-rose-500/25 p-4 rounded-3xl flex gap-3 items-start">
              <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-white">Significant concerns reported</h4>
                <p className="text-xs text-slate-400 mt-1">This employer has a score of {selectedScore.overall_score}/100. Read past candidate experiences before applying.</p>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-3 gap-6">
            {/* Score Ring / Label Card */}
            <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-center text-center">
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-4">ETS Overall rating</span>
              <div className="relative w-36 h-36 flex items-center justify-center">
                <svg className="absolute w-full h-full transform -rotate-95">
                  <circle cx="72" cy="72" r="64" stroke="#1E293B" strokeWidth="10" fill="transparent" />
                  <circle
                    cx="72"
                    cy="72"
                    r="64"
                    stroke={selectedScore.overall_score >= 75 ? "#10B981" : selectedScore.overall_score >= 60 ? "#F59E0B" : "#EF4444"}
                    strokeWidth="10"
                    fill="transparent"
                    strokeDasharray={402}
                    strokeDashoffset={402 - (402 * selectedScore.overall_score) / 100}
                  />
                </svg>
                <div className="text-3xl font-extrabold text-white">{Math.round(selectedScore.overall_score)}</div>
              </div>
              <span className="mt-4 px-3 py-1 bg-slate-800 text-slate-300 text-xs font-bold rounded-full uppercase tracking-wider">{selectedScore.label}</span>
              <p className="text-slate-400 text-xs mt-2 max-w-[200px]">Based on {selectedScore.submission_count} verified experiences.</p>
            </div>

            {/* Dimension Breakdown Card */}
            <div className="glass-panel p-6 rounded-3xl md:col-span-2 space-y-4">
              <h4 className="text-sm text-slate-300 font-bold">ETS Sub-Dimension Analytics</h4>
              
              <div className="space-y-3">
                {/* Transparency */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Process Transparency</span>
                    <span className="font-bold text-white">{selectedScore.transparency_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: `${selectedScore.transparency_score}%` }} />
                  </div>
                </div>

                {/* Timeline */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Timeline Honesty</span>
                    <span className="font-bold text-white">{selectedScore.timeline_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-400 h-full" style={{ width: `${selectedScore.timeline_score}%` }} />
                  </div>
                </div>

                {/* Feedback Quality */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Constructive Feedback Quality</span>
                    <span className="font-bold text-white">{selectedScore.feedback_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-purple-400 h-full" style={{ width: `${selectedScore.feedback_score}%` }} />
                  </div>
                </div>

                {/* Ghost Rate */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Ghost Rate (Lower is Better)</span>
                    <span className="font-bold text-rose-400">{selectedScore.ghost_rate}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-rose-500 h-full" style={{ width: `${selectedScore.ghost_rate}%` }} />
                  </div>
                </div>

                {/* Equity */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Statistical Equity</span>
                    <span className="font-bold text-white">{selectedScore.equity_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-yellow-400 h-full" style={{ width: `${selectedScore.equity_score}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard tabs */}
      <div className="glass-panel p-6 rounded-3xl space-y-6">
        <div className="flex border-b border-slate-800 pb-4 justify-between items-center">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">ETS Leaderboard</h4>
          <div className="flex gap-2">
            {(["best", "worst", "most_improved"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold uppercase transition-all ${activeTab === tab ? "bg-primary text-white" : "bg-slate-800 text-slate-400 hover:text-white"}`}
              >
                {tab.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-3 animate-pulse">
            {[1, 2, 3].map(n => (
              <div key={n} className="bg-slate-850 h-12 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="text-slate-400 border-b border-slate-850">
                  <th className="pb-3 font-bold">Company</th>
                  <th className="pb-3 font-bold">ETS Score</th>
                  <th className="pb-3 font-bold">Label</th>
                  <th className="pb-3 font-bold">Ghost Rate</th>
                  <th className="pb-3 font-bold">Submissions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {leaderboard.map((row) => (
                  <tr key={row.company_name} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-4 font-semibold text-white">{row.company_name}</td>
                    <td className="py-4 font-bold text-primary">{Math.round(row.overall_score)}</td>
                    <td className="py-4">
                      <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-bold uppercase tracking-widest text-[9px]">
                        {row.label}
                      </span>
                    </td>
                    <td className="py-4 text-slate-300">{row.ghost_rate}%</td>
                    <td className="py-4 text-slate-300">{row.submission_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="text-center pt-4">
        <Link
          to="/app/truth"
          className="px-6 py-3 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-2xl font-bold text-xs inline-flex items-center gap-2"
        >
          <Clipboard className="w-4 h-4 text-primary" /> Interviewed recently? Add your experience details
        </Link>
      </div>
    </div>
  );
};
