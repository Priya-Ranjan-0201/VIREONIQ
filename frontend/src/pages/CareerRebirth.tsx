import React, { useState, useEffect } from "react";
import { Sparkles, Compass, FileText, ArrowRight, CheckCircle, RefreshCw, CheckSquare } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface TransferableSkill {
  original_skill: string;
  tech_equivalent: string;
  reframe_sentence: string;
  transfer_strength: string;
  concrete_project: string;
}

interface Phase {
  phase: number;
  title: string;
  weeks: string;
  goal: string;
  daily_tasks?: string[];
  project_ideas?: string[];
  milestone: string;
  break_nullifier?: string;
}

interface RebirthPlan {
  current_domain: string;
  target_role: string;
  available_hours_per_week: number;
  weeks_to_completion: number;
  completion_target_date: string;
  phases: Phase[];
  transferable_skills: TransferableSkill[];
  break_nullifier_strategy: string | null;
}

export const CareerRebirth = () => {
  const [activeTab, setActiveTab] = useState<"analyze" | "roadmap" | "resume">("analyze");
  const [plan, setPlan] = useState<RebirthPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [form, setForm] = useState({
    current_domain: "banking_finance",
    target_role: "Data Analyst",
    available_hours_per_week: 15,
    career_break_reason: "",
    break_duration_months: 0
  });

  const [analyzeText, setAnalyzeText] = useState("");
  const [skillsReport, setSkillsReport] = useState<TransferableSkill[]>([]);
  
  // Resume rewriter states
  const [resumeId, setResumeId] = useState("");
  const [rewrittenResume, setRewrittenResume] = useState<any>(null);

  const fetchMyPlan = async () => {
    try {
      const res = await client.get("/rebirth/my-plan");
      if (res.data && res.data.phases && res.data.phases.length > 0) {
        setPlan(res.data);
        setSkillsReport(res.data.transferable_skills || []);
        return;
      }
    } catch (e) {
      // Fallback below
    }

    // Default calibrated roadmap so user never sees an empty screen
    const DEFAULT_REBIRTH_PLAN: RebirthPlan = {
      current_domain: "Banking & Finance",
      target_role: "Data Analyst / FinTech Engineer",
      available_hours_per_week: 15,
      weeks_to_completion: 16,
      completion_target_date: "December 2026",
      break_nullifier_strategy: "Reframe domain banking expertise into compliance, SQL transactional analytics, and low-latency fraud detection mindset.",
      transferable_skills: [
        {
          original_skill: "Risk Assessment & Credit Scoring",
          tech_equivalent: "Predictive Analytics & Anomaly Detection",
          reframe_sentence: "Applied statistical modeling and risk scoring heuristics to financial ledgers, translating directly to regression analytics and automated classification.",
          transfer_strength: "High",
          concrete_project: "FinTech Credit Risk Predictor using Python & Scikit-Learn"
        },
        {
          original_skill: "Regulatory Reporting & Audit Compliance",
          tech_equivalent: "Data Governance & SQL Schema Integrity",
          reframe_sentence: "Designed strict ledger audit trails ensuring zero data discrepancy, mirroring ACID transactions and automated pipeline checks.",
          transfer_strength: "High",
          concrete_project: "Automated Financial Transaction Reconciliation Pipeline (PostgreSQL & Pandas)"
        },
        {
          original_skill: "Portfolio Performance Dashboards",
          tech_equivalent: "Business Intelligence & BI Engineering",
          reframe_sentence: "Synthesized multi-asset performance data into actionable stakeholder dashboards using Tableau and SQL.",
          transfer_strength: "High",
          concrete_project: "Real-Time Equity Portfolio Telemetry Dashboard (Streamlit & Plotly)"
        }
      ],
      phases: [
        {
          phase: 1,
          title: "Foundations & Modern SQL Analytics",
          weeks: "Weeks 1-4",
          goal: "Master modern PostgreSQL, window functions, and exploratory data analysis with Pandas.",
          daily_tasks: ["Advanced SQL (GROUP BY, HAVING, Window Functions)", "Python for Data Analysis (NumPy, Pandas)", "Database Schema Normalization"],
          project_ideas: ["E-Commerce Transaction Churn Analyzer", "Banking Ledger ETL Pipeline"],
          milestone: "Complete 20 SQL LeetCode Mediums and build initial portfolio schema"
        },
        {
          phase: 2,
          title: "Data Visualization & Dashboard Engineering",
          weeks: "Weeks 5-8",
          goal: "Translate business metrics into executive-ready dashboards and storytelling.",
          daily_tasks: ["Tableau / PowerBI interactive filters", "Data storytelling & stakeholder KPI decks", "Automated email reporting scripts"],
          project_ideas: ["Executive Revenue Forecasting Dashboard", "Credit Card Fraud Pattern Explorer"],
          milestone: "Deploy first interactive dashboard to Tableau Public or Streamlit Cloud"
        },
        {
          phase: 3,
          title: "Applied Machine Learning & Statistical Modeling",
          weeks: "Weeks 9-12",
          goal: "Predictive modeling, regression, and decision trees for business forecasting.",
          daily_tasks: ["Supervised Learning (Scikit-Learn)", "Feature Engineering on transactional datasets", "Model evaluation metrics (ROC-AUC, Precision, Recall)"],
          project_ideas: ["Customer Lifetime Value (LTV) Predictor", "Loan Default Probability Engine"],
          milestone: "Publish production ML repository with clean README and Dockerfile"
        },
        {
          phase: 4,
          title: "Target MNC Interview Screening & Portfolio Showcase",
          weeks: "Weeks 13-16",
          goal: "Behavioral STAR storytelling reframing past experience and technical screening rounds.",
          daily_tasks: ["Data Analyst live SQL screening mocks", "Product sense & metrics definition rounds", "Reframing non-tech background into a domain superpower"],
          project_ideas: ["End-to-End Capstone Project Presentation", "Personal Analytics Portfolio Website"],
          milestone: "Begin active recruiter outreach and secure 3+ interviews"
        }
      ]
    };
    setPlan(DEFAULT_REBIRTH_PLAN);
    setSkillsReport(DEFAULT_REBIRTH_PLAN.transferable_skills);
  };

  useEffect(() => {
    fetchMyPlan();
  }, []);

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const payload = {
        ...form,
        career_break_reason: form.career_break_reason || null,
        break_duration_months: form.break_duration_months || 0
      };
      const res = await client.post("/rebirth/generate-roadmap", payload);
      setPlan(res.data);
      setSkillsReport(res.data.transferable_skills);
      toast.success("Career switch roadmap generated successfully!");
      setActiveTab("roadmap");
    } catch (err: any) {
      toast.error("Failed to generate plan.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRewriteResume = async () => {
    if (!resumeId) {
      toast.error("Enter a valid Resume ID.");
      return;
    }
    setIsLoading(true);
    try {
      const res = await client.post("/rebirth/rewrite-resume", {
        resume_id: resumeId,
        target_role: plan?.target_role || "Software Developer"
      });
      setRewrittenResume(res.data);
      toast.success("Resume rewritten successfully!");
    } catch (err: any) {
      toast.error("Rewrite failed. Verify the Resume ID exists.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">Career Rebirth Engine</h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Transition non-tech domains and career breaks into distinct technical advantages</p>
      </header>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 pb-2 gap-4">
        {(["analyze", "roadmap", "resume"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-bold capitalize border-b-2 transition-all ${activeTab === tab ? "border-primary text-white" : "border-transparent text-slate-400 hover:text-slate-200"}`}
          >
            {tab} Transition
          </button>
        ))}
      </div>

      {activeTab === "analyze" && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-3xl space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" /> Setup Domain Conversion Parameters
            </h3>
            <form onSubmit={handleGeneratePlan} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Original Professional Domain</label>
                <select
                  value={form.current_domain}
                  onChange={(e) => setForm({ ...form, current_domain: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 outline-none focus:border-primary"
                >
                  <option value="banking_finance">Banking & Finance</option>
                  <option value="teaching_education">Teaching & Education</option>
                  <option value="logistics_operations">Logistics & Operations</option>
                  <option value="healthcare_nursing">Healthcare & Nursing</option>
                  <option value="military_defense">Military & Defense</option>
                  <option value="sales_marketing">Sales & Marketing</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Target Tech Role</label>
                <input
                  type="text"
                  required
                  value={form.target_role}
                  onChange={(e) => setForm({ ...form, target_role: e.target.value })}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-400 font-bold block mb-1">Available Hours / Week</label>
                  <input
                    type="number"
                    required
                    value={form.available_hours_per_week}
                    onChange={(e) => setForm({ ...form, available_hours_per_week: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-bold block mb-1">Career Break Reason</label>
                  <select
                    value={form.career_break_reason}
                    onChange={(e) => setForm({ ...form, career_break_reason: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 outline-none focus:border-primary"
                  >
                    <option value="">No Break</option>
                    <option value="maternity_paternity">Maternity/Paternity</option>
                    <option value="health">Medical Recovery</option>
                    <option value="family_care">Family Care</option>
                    <option value="travel">Travel</option>
                    <option value="self_study">Self Study</option>
                    <option value="startup_failed">Failed Startup</option>
                  </select>
                </div>
              </div>

              {form.career_break_reason && (
                <div>
                  <label className="text-xs text-slate-400 font-bold block mb-1">Break Duration (months)</label>
                  <input
                    type="number"
                    value={form.break_duration_months}
                    onChange={(e) => setForm({ ...form, break_duration_months: parseInt(e.target.value) })}
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-primary to-accent hover:opacity-90 font-bold rounded-xl text-white flex items-center justify-center gap-2"
              >
                {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Build Rebirth Roadmap"}
              </button>
            </form>
          </div>

          <div className="glass-panel p-6 rounded-3xl space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-primary" /> Transferable Skill Reframe Reports
            </h3>
            {skillsReport.length > 0 ? (
              <div className="space-y-4 max-h-[450px] overflow-y-auto pr-2">
                {skillsReport.map((s, idx) => (
                  <div key={idx} className="bg-slate-950/40 border border-slate-850 p-4 rounded-2xl space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-400">{s.original_skill} &rarr; <strong className="text-primary">{s.tech_equivalent}</strong></span>
                      <span className="px-2 py-0.5 bg-slate-800 text-slate-300 font-bold rounded-full">{s.transfer_strength} Strength</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-semibold italic">"{s.reframe_sentence}"</p>
                    <div className="text-[10px] text-slate-400"><strong className="text-accent">Demonstration Project:</strong> {s.concrete_project}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500">Configure parameters on the left to extract conversion reports.</div>
            )}
          </div>
        </div>
      )}

      {activeTab === "roadmap" && (
        <div className="space-y-6">
          {plan ? (
            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                {plan.phases.map((phase) => (
                  <div key={phase.phase} className="glass-panel p-6 rounded-3xl border border-slate-800">
                    <div className="flex justify-between text-xs mb-2">
                      <span className="px-2 py-1 bg-slate-850 text-slate-300 rounded font-bold uppercase tracking-wider">Phase {phase.phase}</span>
                      <span className="font-bold text-slate-400">Weeks: {phase.weeks}</span>
                    </div>
                    <h4 className="text-base font-bold text-white mb-2">{phase.title}</h4>
                    <p className="text-xs text-slate-400 mb-4">{phase.goal}</p>

                    {phase.daily_tasks && (
                      <div className="bg-slate-950/30 p-4 rounded-2xl border border-slate-900 mb-4">
                        <span className="text-[10px] text-primary font-bold uppercase tracking-wider mb-2 block">Daily tasks</span>
                        <ul className="space-y-2">
                          {phase.daily_tasks.map((task, i) => (
                            <li key={i} className="text-xs text-slate-300 flex items-center gap-2">
                              <CheckSquare className="w-3.5 h-3.5 text-slate-500" /> {task}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {phase.project_ideas && (
                      <div className="bg-slate-950/30 p-4 rounded-2xl border border-slate-900 mb-4">
                        <span className="text-[10px] text-accent font-bold uppercase tracking-wider mb-2 block">Project Ideas</span>
                        <ul className="space-y-2">
                          {phase.project_ideas.map((idea, i) => (
                            <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                              <span className="text-accent font-extrabold shrink-0">&middot;</span> <span>{idea}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="border-t border-slate-850 pt-4 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Milestone: <strong className="text-white">{phase.milestone}</strong></span>
                      {phase.break_nullifier && (
                        <span className="px-2 py-0.5 bg-slate-800 text-amber-500 rounded font-semibold text-[10px]">Break Nullifier Active</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="glass-panel p-6 rounded-3xl h-fit space-y-4">
                <h4 className="text-sm text-slate-400 font-bold uppercase tracking-wider">Timeline Summary</h4>
                <div>
                  <div className="text-xs text-slate-500">Duration Needed</div>
                  <div className="text-lg font-bold text-white mt-0.5">{plan.weeks_to_completion} Weeks</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500">Target Completion</div>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">{plan.completion_target_date}</div>
                </div>
                {plan.break_nullifier_strategy && (
                  <div className="border-t border-slate-800 pt-4">
                    <span className="text-xs text-amber-500 font-bold block mb-1">Break Strategy</span>
                    <p className="text-xs text-slate-400 leading-relaxed">{plan.break_nullifier_strategy}</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-sm text-slate-400 py-12">No plan generated yet. Generate in the Analyze tab.</div>
          )}
        </div>
      )}

      {activeTab === "resume" && (
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" /> Resume Rewriter for Career Switchers
          </h3>
          <div className="flex gap-4 max-w-xl">
            <input
              type="text"
              placeholder="Paste your Resume UUID..."
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
            />
            <button
              onClick={handleRewriteResume}
              disabled={isLoading}
              className="px-6 py-2.5 bg-primary hover:opacity-90 font-bold rounded-xl text-white text-xs flex items-center gap-2"
            >
              {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Reframe Resume"}
            </button>
          </div>

          {rewrittenResume && (
            <div className="space-y-6 mt-6 border-t border-slate-850 pt-6">
              <div>
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Summary Pitch Re-Write</h4>
                <p className="text-xs text-slate-350 bg-slate-950/40 p-4 rounded-xl leading-relaxed border border-slate-900 font-medium">
                  {rewrittenResume.summary_rewritten}
                </p>
              </div>

              <div>
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Domain Advantage Section Additions</h4>
                <ul className="space-y-2">
                  {rewrittenResume.domain_advantage_section.map((bullet: string, i: number) => (
                    <li key={i} className="text-xs text-slate-300 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" /> {bullet}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Experience Bullets Reframing Mappings</h4>
                <div className="space-y-4">
                  {Object.entries(rewrittenResume.experience_bullets_rewritten).map(([original, reframed]: [string, any], idx) => (
                    <div key={idx} className="grid grid-cols-2 gap-4 text-xs bg-slate-950/20 border border-slate-850 p-4 rounded-2xl">
                      <div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Original Bullet</div>
                        <span className="text-slate-400 font-medium">{original}</span>
                      </div>
                      <div className="border-l border-slate-850 pl-4">
                        <div className="text-[10px] text-primary font-bold uppercase tracking-wider mb-1">Reframed Technical equivalent</div>
                        <span className="text-slate-200 font-bold">{reframed}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
