import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GraduationCap, BookOpen, CheckCircle, Calendar, Users, TrendingUp, AlertCircle, Award } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface YearPlan {
  year_number: number;
  label: string;
  quarterly_milestones: string[];
  recommended_skills: string[];
  project_idea: string;
  resources: string[];
  community: string;
}

interface Trajectory {
  current_class: number;
  target_role: string;
  interest_areas: string[];
  hours_per_week: number;
  years_to_placement: number;
  year_plans: YearPlan[];
  milestones_completed: Record<string, boolean>;
  last_market_refresh_at: string;
}

export const HighSchoolTrajectory = () => {
  const [trajectory, setTrajectory] = useState<Trajectory | null>(null);
  const [activeYear, setActiveYear] = useState<number>(1);
  const [cohort, setCohort] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [changesApplied, setChangesApplied] = useState<string[]>([]);

  // Generator form
  const [form, setForm] = useState({
    current_class: 11,
    target_role: "Software Developer",
    interest_areas: "web development, robotics",
    hours_per_week: 5
  });

  const fetchTrajectory = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/highschool/my-trajectory");
      setTrajectory(res.data);
      // Set active year based on class
      const current_class = res.data.current_class;
      // Heuristic map class to year of trajectory
      const classYearMap: Record<number, number> = { 9: 1, 10: 2, 11: 3, 12: 4 };
      setActiveYear(classYearMap[current_class] || 1);
      
      // Fetch cohort stats
      const cohortRes = await client.get("/highschool/cohort-benchmarks", {
        params: { current_class: res.data.current_class, target_role: res.data.target_role }
      });
      setCohort(cohortRes.data);
    } catch (e) {
      // Default initial state when trajectory is not yet initialized
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrajectory();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const payload = {
        ...form,
        interest_areas: form.interest_areas.split(",").map(i => i.trim()).filter(Boolean)
      };
      const res = await client.post("/highschool/generate-trajectory", payload);
      setTrajectory(res.data);
      toast.success("Roadmap generated successfully!");
      fetchTrajectory();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Generation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckMilestone = async (year: number, index: number) => {
    try {
      const res = await client.post("/highschool/log-milestone", {
        year_number: year,
        milestone_index: index
      });
      toast.success("Milestone completed! Awarded 50 XP.");
      fetchTrajectory();
    } catch (e) {
      toast.error("Failed to log milestone.");
    }
  };

  const handleMarketRefresh = async () => {
    try {
      const res = await client.post("/highschool/refresh-for-market");
      setChangesApplied(res.data.changes_applied);
      if (res.data.changes_applied.length > 0) {
        toast.info("Trajectory updated with new market trends!");
        fetchTrajectory();
      } else {
        toast.success("Trajectory is already up to date with latest trends.");
      }
    } catch (e) {
      toast.error("Failed to refresh.");
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Loading high school operating kernel...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">PlaceIQ for High Schools</h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">4-Year adaptive career trajectories starting at age 16</p>
        </div>
        {trajectory && (
          <button
            onClick={handleMarketRefresh}
            className="px-4 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 flex items-center gap-2"
          >
            <TrendingUp className="w-4 h-4 text-emerald-400" /> Sync Market Trends
          </button>
        )}
      </header>

      {changesApplied.length > 0 && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-3xl flex gap-3 items-start">
          <AlertCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-white">Market Update Banner</h4>
            <p className="text-xs text-slate-400 mt-1">We updated your recommended skills based on weekly market intelligence: {changesApplied.join(", ")}</p>
          </div>
        </div>
      )}

      {trajectory ? (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Timeline */}
          <div className="md:col-span-2 space-y-4">
            {trajectory.year_plans.map((year) => {
              const isActive = activeYear === year.year_number;
              // Calculate completion percentage
              const total = year.quarterly_milestones.length;
              const completed = year.quarterly_milestones.reduce((acc, _, idx) => {
                return acc + (trajectory.milestones_completed[`${year.year_number}:${idx}`] ? 1 : 0);
              }, 0);
              const percentage = total > 0 ? (completed / total) * 100 : 0;

              return (
                <div
                  key={year.year_number}
                  className={`glass-panel rounded-3xl transition-all ${isActive ? "border-primary/40 bg-gradient-to-b from-primary/5 to-transparent" : "border-slate-800"}`}
                >
                  <div
                    onClick={() => setActiveYear(year.year_number)}
                    className="p-6 cursor-pointer flex justify-between items-center"
                  >
                    <div>
                      <h3 className="text-lg font-bold text-white">{year.label}</h3>
                      <div className="w-[180px] bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                        <div className="bg-primary h-full" style={{ width: `${percentage}%` }} />
                      </div>
                    </div>
                    <span className="text-xs text-slate-400 font-bold">{completed}/{total} Completed</span>
                  </div>

                  <AnimatePresence>
                    {isActive && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden border-t border-slate-850 px-6 pb-6 pt-4 space-y-6"
                      >
                        {/* Milestone checklist */}
                        <div>
                          <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-3">Quarterly Milestones</h4>
                          <div className="space-y-3">
                            {year.quarterly_milestones.map((milestone, idx) => {
                              const isDone = trajectory.milestones_completed[`${year.year_number}:${idx}`];
                              return (
                                <div key={idx} className="flex items-center gap-3 bg-slate-950/40 p-3 rounded-2xl border border-slate-900">
                                  <input
                                    type="checkbox"
                                    checked={!!isDone}
                                    disabled={!!isDone}
                                    onChange={() => handleCheckMilestone(year.year_number, idx)}
                                    className="w-4 h-4 rounded border-slate-800 text-primary focus:ring-primary"
                                  />
                                  <span className={`text-xs ${isDone ? "text-slate-500 line-through" : "text-slate-300"}`}>{milestone}</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Project Idea card */}
                        <div className="bg-slate-950/50 border border-slate-850 p-4 rounded-2xl">
                          <h4 className="text-xs text-primary font-bold uppercase tracking-wider mb-2">Your Year Project</h4>
                          <p className="text-xs text-slate-400 leading-relaxed">{year.project_idea}</p>
                        </div>

                        {/* Resources */}
                        <div>
                          <h4 className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Recommended Free Resources</h4>
                          <div className="flex gap-4">
                            {year.resources.map((res, i) => (
                              <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                                <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                                <span>{res}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>

          {/* Cohort Stats */}
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-3xl">
              <h4 className="text-sm text-slate-400 font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                <Users className="w-4 h-4 text-primary" /> Cohort Benchmarks
              </h4>
              {cohort && cohort.status === "success" ? (
                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-slate-400">Class size cohort</div>
                    <div className="text-xl font-bold text-white mt-1">{cohort.cohort_size} students</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">Average committed hours</div>
                    <div className="text-xl font-bold text-white mt-1">{cohort.avg_hours_committed} hrs/week</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">Milestone completion rate</div>
                    <div className="text-xl font-bold text-emerald-400 mt-1">{cohort.milestone_completion_rate}%</div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-500 lead-relaxed">
                  Cohort stats are private and aggregate. Insufficient cohort data (requires minimum 5 comparable trajectories to display).
                </div>
              )}
            </div>

            <div className="glass-panel p-6 rounded-3xl">
              <h4 className="text-sm text-slate-400 font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                <Award className="w-4 h-4 text-primary" /> Target role
              </h4>
              <div className="text-sm text-slate-300 font-semibold">{trajectory.target_role}</div>
              <div className="flex flex-wrap gap-2 mt-4">
                {trajectory.interest_areas.map((int) => (
                  <span key={int} className="px-2.5 py-1 bg-slate-800 text-slate-400 text-xs font-bold rounded-md">
                    {int}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Trajectory Generator Form
        <div className="max-w-xl mx-auto glass-panel p-8 rounded-3xl">
          <h3 className="text-xl font-bold text-white mb-2">Build Your 4-Year Trajectory</h3>
          <p className="text-xs text-slate-400 mb-6">Designed for high schoolers starting early. Formulate your adaptive pipeline.</p>
          <form onSubmit={handleGenerate} className="space-y-6">
            <div>
              <label className="text-xs text-slate-400 font-bold block mb-1">Current Class / Grade</label>
              <select
                value={form.current_class}
                onChange={(e) => setForm({ ...form, current_class: parseInt(e.target.value) })}
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 outline-none focus:border-primary"
              >
                <option value="9">Class 9 (Age 14)</option>
                <option value="10">Class 10 (Age 15)</option>
                <option value="11">Class 11 (Age 16)</option>
                <option value="12">Class 12 (Age 17)</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 font-bold block mb-1">Target Tech Role</label>
              <input
                type="text"
                required
                value={form.target_role}
                onChange={(e) => setForm({ ...form, target_role: e.target.value })}
                placeholder="e.g. AI Engineer, Mobile Developer"
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 font-bold block mb-1">Interest Areas (comma-separated)</label>
              <input
                type="text"
                required
                value={form.interest_areas}
                onChange={(e) => setForm({ ...form, interest_areas: e.target.value })}
                placeholder="coding, games, math, design"
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 font-bold block mb-1">Available Hours per Week</label>
              <input
                type="number"
                required
                value={form.hours_per_week}
                onChange={(e) => setForm({ ...form, hours_per_week: parseFloat(e.target.value) })}
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-gradient-to-r from-primary to-accent hover:opacity-90 font-bold rounded-xl text-white"
            >
              Generate Adaptive Trajectory
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
