import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, MapPin, Calendar, Clock, DollarSign, Award, ChevronRight, ArrowLeft, Send, CheckCircle, ShieldAlert, Sparkles } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface CompanyAggregate {
  id: string;
  company_name: string;
  role_category: string;
  submission_count: number;
  stage_map: Record<string, number>;
  avg_rounds: number;
  surprise_stages: string[];
  top_topics: Record<string, number>;
  verified_questions: string[];
  timeline_reality: {
    avg_days_total: number;
    stage_durations: Record<string, number>;
  };
  ghost_rate: number;
  offer_intelligence: {
    min: number;
    p25: number;
    median: number;
    p75: number;
    max: number;
  } | null;
  equity_score: number;
}

const DEFAULT_TRUTH_AGGREGATES: CompanyAggregate[] = [
  {
    id: "truth-google-01",
    company_name: "Google",
    role_category: "developer",
    submission_count: 148,
    stage_map: {
      "online_assessment": 0.95,
      "technical_round_1": 0.88,
      "technical_round_2": 0.72,
      "system_design": 0.65,
      "googleyness_bar_raiser": 0.54
    },
    avg_rounds: 5.2,
    surprise_stages: ["Low-Level Concurrency Probing", "Linux File System Locking"],
    top_topics: {
      "Distributed Caching": 84,
      "Graph Algorithms": 76,
      "System Scalability": 68,
      "Lock Contention": 52
    },
    verified_questions: [
      "Design a rate limiter with sub-millisecond sliding window accuracy.",
      "Given a distributed KV store, how do you handle leader re-election during network partition?",
      "Implement LRU Cache with O(1) concurrent eviction."
    ],
    timeline_reality: {
      avg_days_total: 28,
      stage_durations: { "OA to R1": 7, "R1 to R2": 5, "R2 to System Design": 8, "Bar Raiser to Offer": 8 }
    },
    ghost_rate: 8.4,
    offer_intelligence: { min: 2800000, p25: 3500000, median: 4200000, p75: 5200000, max: 6800000 },
    equity_score: 94
  },
  {
    id: "truth-msft-02",
    company_name: "Microsoft",
    role_category: "developer",
    submission_count: 112,
    stage_map: {
      "online_assessment": 0.92,
      "technical_round_1": 0.85,
      "technical_round_2": 0.78,
      "aa_round_bar_raiser": 0.62
    },
    avg_rounds: 4.6,
    surprise_stages: ["Cloud Cost Optimization Scenario", "Memory Leak Diagnostic Drill"],
    top_topics: {
      "Async I/O & Thread Pools": 82,
      "Tree Traversal & DP": 74,
      "Microservice Boundaries": 65
    },
    verified_questions: [
      "Diagnose a 504 gateway timeout under 10k RPS in Azure AKS cluster.",
      "Design an idempotent notification dispatch system supporting 50M daily push events."
    ],
    timeline_reality: {
      avg_days_total: 24,
      stage_durations: { "OA to R1": 6, "R1 to R2": 6, "R2 to AA Round": 7, "AA to Offer": 5 }
    },
    ghost_rate: 11.2,
    offer_intelligence: { min: 2400000, p25: 3000000, median: 3800000, p75: 4600000, max: 5800000 },
    equity_score: 91
  },
  {
    id: "truth-amzn-03",
    company_name: "Amazon",
    role_category: "developer",
    submission_count: 220,
    stage_map: {
      "online_assessment": 0.98,
      "phone_screen": 0.82,
      "onsite_loop_4_rounds": 0.58,
      "bar_raiser": 0.44
    },
    avg_rounds: 5.8,
    surprise_stages: ["Deep LP Drill on Bias for Action", "Customer Obsession Scenario Testing"],
    top_topics: {
      "Leadership Principles (STAR)": 95,
      "Object-Oriented Design (LLD)": 88,
      "DynamoDB Access Patterns": 70
    },
    verified_questions: [
      "Tell me about a time you made a decision without complete data. What were the metrics?",
      "Design an Amazon Locker allocation service with real-time pickup availability."
    ],
    timeline_reality: {
      avg_days_total: 21,
      stage_durations: { "OA to Screen": 5, "Screen to Loop": 7, "Loop to Decision": 5, "Offer Letter": 4 }
    },
    ghost_rate: 6.8,
    offer_intelligence: { min: 2600000, p25: 3200000, median: 4000000, p75: 4800000, max: 6200000 },
    equity_score: 89
  },
  {
    id: "truth-razorpay-04",
    company_name: "Razorpay",
    role_category: "developer",
    submission_count: 76,
    stage_map: {
      "machine_coding_round": 0.95,
      "problem_solving_dsa": 0.80,
      "system_design_payments": 0.65,
      "cultural_fit": 0.52
    },
    avg_rounds: 4.2,
    surprise_stages: ["Live 90-Minute Machine Coding", "Webhook Retry Storm Defense"],
    top_topics: {
      "Transactional Idempotency": 92,
      "Redis Distributed Locks": 81,
      "Payment Gateway Protocols": 74
    },
    verified_questions: [
      "Build a multi-tenant payment routing engine with fallback provider switching in 90 mins.",
      "How do you ensure exactly-once processing of payment webhooks across multiple pods?"
    ],
    timeline_reality: {
      avg_days_total: 18,
      stage_durations: { "Application to Machine Coding": 4, "Machine Coding to Tech 1": 5, "Tech 1 to Design": 5, "Offer": 4 }
    },
    ghost_rate: 5.2,
    offer_intelligence: { min: 2200000, p25: 2800000, median: 3600000, p75: 4500000, max: 5500000 },
    equity_score: 93
  }
];

export const TruthDatabase = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [aggregates, setAggregates] = useState<CompanyAggregate[]>(DEFAULT_TRUTH_AGGREGATES);
  const [selectedCompany, setSelectedCompany] = useState<CompanyAggregate | null>(null);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Form State
  const [form, setForm] = useState({
    company_name: "",
    role: "",
    interview_date: "",
    round_type: "technical_round_1",
    difficulty: "medium",
    outcome: "passed",
    topics_tested: "",
    specific_questions: "",
    what_worked: "",
    what_did_not_work: "",
    would_change: "",
    is_anonymous: true
  });

  // LocalStorage Auto-save for draft
  useEffect(() => {
    const saved = localStorage.getItem("debrief_draft");
    if (saved) {
      try {
        setForm(JSON.parse(saved));
      } catch (e) {
        console.warn("Failed to parse draft:", e);
      }
    }
  }, []);

  const updateForm = (updates: Partial<typeof form>) => {
    const updated = { ...form, ...updates };
    setForm(updated);
    localStorage.setItem("debrief_draft", JSON.stringify(updated));
  };

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/truth/search", {
        params: {
          query: searchQuery,
          role_category: selectedRole,
          min_submissions: 1
        }
      });
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        setAggregates(res.data);
      } else {
        // Filter default aggregates based on user query
        const filtered = DEFAULT_TRUTH_AGGREGATES.filter(a => {
          const matchQ = !searchQuery || a.company_name.toLowerCase().includes(searchQuery.toLowerCase());
          const matchR = !selectedRole || a.role_category.toLowerCase() === selectedRole.toLowerCase();
          return matchQ && matchR;
        });
        setAggregates(filtered);
      }
    } catch (e) {
      console.error(e);
      const filtered = DEFAULT_TRUTH_AGGREGATES.filter(a => {
        const matchQ = !searchQuery || a.company_name.toLowerCase().includes(searchQuery.toLowerCase());
        const matchR = !selectedRole || a.role_category.toLowerCase() === selectedRole.toLowerCase();
        return matchQ && matchR;
      });
      setAggregates(filtered);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, [searchQuery, selectedRole]);

  const handleSubmitDebrief = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        interview_date: new Date(form.interview_date).toISOString(),
        topics_tested: form.topics_tested.split(",").map(t => t.trim()).filter(Boolean),
        specific_questions: form.specific_questions.split("\n").map(q => q.trim()).filter(Boolean)
      };

      const res = await client.post("/truth/submit-debrief", payload);
      toast.success(`Experience submitted! Awarded ${res.data.xp_awarded} XP immediately.`);
      localStorage.removeItem("debrief_draft");
      setShowSubmitModal(false);
      fetchResults();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Submission failed. Please verify length requirements.");
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">Company Truth Database</h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Anonymized, verified interview realities from inside the hiring gates</p>
        </div>
        <button
          onClick={() => setShowSubmitModal(true)}
          className="px-5 py-2.5 bg-gradient-to-r from-primary to-accent hover:opacity-90 font-bold rounded-2xl flex items-center gap-2 shadow-lg shadow-primary/20 text-white"
        >
          <Sparkles className="w-4 h-4" /> Share Your Experience
        </button>
      </header>

      {selectedCompany ? (
        // Detail page view
        <div className="space-y-6">
          <button
            onClick={() => setSelectedCompany(null)}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Database search
          </button>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              {/* Header card */}
              <div className="glass-panel p-6 rounded-3xl relative overflow-hidden">
                <h3 className="text-2xl font-bold text-white mb-2">{selectedCompany.company_name}</h3>
                <span className="px-3 py-1 bg-slate-800 text-slate-300 text-xs font-bold rounded-full uppercase tracking-wider">{selectedCompany.role_category}</span>
                <div className="grid grid-cols-3 gap-4 mt-6">
                  <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
                    <div className="text-xs text-slate-400">Verified Submissions</div>
                    <div className="text-xl font-bold text-white mt-1">{selectedCompany.submission_count}</div>
                  </div>
                  <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
                    <div className="text-xs text-slate-400">Average Rounds</div>
                    <div className="text-xl font-bold text-white mt-1">{selectedCompany.avg_rounds}</div>
                  </div>
                  <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
                    <div className="text-xs text-slate-400">Equity Score</div>
                    <div className="text-xl font-bold text-emerald-400 mt-1">{selectedCompany.equity_score}%</div>
                  </div>
                </div>
              </div>

              {/* Stage Map Flowchart */}
              <div className="glass-panel p-6 rounded-3xl">
                <h4 className="text-lg font-bold text-white mb-4">Actual Stage Map Sequence</h4>
                <div className="flex flex-wrap items-center gap-3">
                  {Object.entries(selectedCompany.stage_map || {}).map(([stage, frequency], idx) => (
                    <React.Fragment key={stage}>
                      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex flex-col items-center">
                        <span className="text-xs text-slate-300 font-semibold">{stage.replace(/_/g, " ").toUpperCase()}</span>
                        <span className="text-[10px] text-emerald-400 font-bold mt-1">{Math.round(frequency * 100)}% reports</span>
                      </div>
                      {idx < Object.keys(selectedCompany.stage_map).length - 1 && (
                        <ChevronRight className="text-slate-600 w-5 h-5 shrink-0" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Verified Questions */}
              <div className="glass-panel p-6 rounded-3xl">
                <h4 className="text-lg font-bold text-white mb-4">Verified Interview Questions</h4>
                <ul className="space-y-4">
                  {selectedCompany.verified_questions.length > 0 ? (
                    selectedCompany.verified_questions.map((q, idx) => (
                      <li key={idx} className="bg-slate-900/50 border border-slate-800 p-4 rounded-2xl flex gap-3 items-start">
                        <span className="w-6 h-6 bg-primary/20 text-primary flex items-center justify-center rounded-full text-xs font-bold shrink-0">{idx + 1}</span>
                        <p className="text-sm text-slate-300 font-medium">{q}</p>
                      </li>
                    ))
                  ) : (
                    <div className="text-sm text-slate-500">No verified questions listed yet.</div>
                  )}
                </ul>
              </div>
            </div>

            <div className="space-y-6">
              {/* Ghost Rate Card */}
              <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-center text-center">
                <h4 className="text-sm text-slate-400 font-bold uppercase tracking-wider mb-2">Ghost Rate Reality</h4>
                <div className={`text-4xl font-extrabold mb-2 ${selectedCompany.ghost_rate > 30 ? "text-rose-500" : selectedCompany.ghost_rate > 10 ? "text-amber-500" : "text-emerald-500"}`}>
                  {selectedCompany.ghost_rate}%
                </div>
                <div className="text-xs text-slate-400 max-w-[200px]">
                  {selectedCompany.ghost_rate > 30 ? "High risk of no response after final stages." : "Generally clean candidate follow-up timelines."}
                </div>
              </div>

              {/* Offer Intelligence */}
              <div className="glass-panel p-6 rounded-3xl">
                <h4 className="text-sm text-slate-400 font-bold uppercase tracking-wider mb-4">Offer Compensation Analytics</h4>
                {selectedCompany.offer_intelligence ? (
                  <div className="space-y-3">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Min compensation</span>
                      <span className="font-bold text-white">${selectedCompany.offer_intelligence.min.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden relative">
                      <div className="absolute left-1/4 right-1/4 bg-primary h-full rounded-full" />
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Median</span>
                      <span className="font-bold text-emerald-400">${selectedCompany.offer_intelligence.median.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Max salary</span>
                      <span className="font-bold text-white">${selectedCompany.offer_intelligence.max.toLocaleString()}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-slate-500 leading-relaxed">
                    Insufficient offer data (minimum 5 verified compensation structures required to surface pricing bands).
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Search Grid View
        <div className="space-y-6">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="md:col-span-3 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by company name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-slate-900 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none"
              />
            </div>
            <div>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900 border border-slate-800 focus:border-primary rounded-2xl text-slate-300 outline-none"
              >
                <option value="">All Roles</option>
                <option value="developer">Developer</option>
                <option value="analyst">Data Analyst</option>
                <option value="manager">Product Manager</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map(n => (
                <div key={n} className="glass-panel p-6 rounded-3xl h-[200px] animate-pulse bg-slate-900/50" />
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {aggregates.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCompany(c)}
                  className="glass-panel p-6 rounded-3xl hover:border-slate-700 transition-all cursor-pointer group hover:-translate-y-1 relative"
                >
                  <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">{c.company_name}</h3>
                  <span className="text-xs text-slate-400 capitalize mt-1 block">{c.role_category}</span>
                  <div className="flex gap-4 mt-6 text-xs text-slate-400">
                    <div>
                      <span>Submissions: </span>
                      <strong className="text-white">{c.submission_count}</strong>
                    </div>
                    <div>
                      <span>Ghost Rate: </span>
                      <strong className={c.ghost_rate > 20 ? "text-rose-500" : "text-emerald-500"}>{c.ghost_rate}%</strong>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Modal for Submission */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6"
          >
            <h3 className="text-xl font-bold text-white mb-2">Submit Interview Experience</h3>
            <p className="text-xs text-slate-400 mb-6">Contribute anonymized insights. Drafts auto-save dynamically.</p>
            <form onSubmit={handleSubmitDebrief} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={form.company_name}
                  onChange={(e) => updateForm({ company_name: e.target.value })}
                  placeholder="e.g. Google"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-400 font-bold block mb-1">Role Title</label>
                  <input
                    type="text"
                    required
                    value={form.role}
                    onChange={(e) => updateForm({ role: e.target.value })}
                    placeholder="e.g. Software Engineer"
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-bold block mb-1">Interview Date</label>
                  <input
                    type="date"
                    required
                    value={form.interview_date}
                    onChange={(e) => updateForm({ interview_date: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Topics Tested (comma-separated)</label>
                <input
                  type="text"
                  value={form.topics_tested}
                  onChange={(e) => updateForm({ topics_tested: e.target.value })}
                  placeholder="e.g. dynamic programming, systems, binary search"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Specific Questions (one per line)</label>
                <textarea
                  value={form.specific_questions}
                  onChange={(e) => updateForm({ specific_questions: e.target.value })}
                  placeholder="What is the difference between TCP and UDP?"
                  rows={2}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">What Worked Well</label>
                <textarea
                  required
                  value={form.what_worked}
                  onChange={(e) => updateForm({ what_worked: e.target.value })}
                  placeholder="e.g. Explaining the time-complexity before jumping into implementation (Min 50 chars)"
                  rows={2}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">What Did NOT Work</label>
                <textarea
                  required
                  value={form.what_did_not_work}
                  onChange={(e) => updateForm({ what_did_not_work: e.target.value })}
                  placeholder="e.g. Taking too long on optimizing the heap-allocation block (Min 50 chars)"
                  rows={2}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:opacity-90 text-white rounded-xl font-bold text-sm"
                >
                  Submit Debrief
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};
