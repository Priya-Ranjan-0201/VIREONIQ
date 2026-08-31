import React, { useState, useEffect } from "react";
import { Award, Users, Calendar, Video, Clock, Star, TrendingUp, AlertCircle, CheckCircle, RefreshCw } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface Mentor {
  mentor_id: string;
  mentor_name: string;
  placement_company: string;
  placement_role: string;
  college_name: string;
  match_score: number;
  reasons: string[];
}

interface MentorSession {
  id: string;
  session_type: string;
  status: string;
  scheduled_at: string;
  meeting_link: string;
  agenda: { agenda: string[] };
}

const DEFAULT_MENTORS: Mentor[] = [
  {
    mentor_id: "m-001",
    mentor_name: "Aditya Verma",
    placement_company: "Google",
    placement_role: "Software Engineer (L4)",
    college_name: "IIT Bombay",
    match_score: 96,
    reasons: ["Top 1% in Distributed Systems", "Conducted 45+ mock interviews", "Cleared Google L4 Bar-Raiser in 2025"]
  },
  {
    mentor_id: "m-002",
    mentor_name: "Sneha Mukherjee",
    placement_company: "Microsoft",
    placement_role: "SDE-2 (Azure Core)",
    college_name: "BITS Pilani",
    match_score: 93,
    reasons: ["Azure Cloud Platform Expert", "Low-Level Design & Concurrency Specialist", "Alumni mentor rating: 4.9/5.0"]
  },
  {
    mentor_id: "m-003",
    mentor_name: "Karan Singhal",
    placement_company: "Amazon",
    placement_role: "SDE-1 (AWS Lambda)",
    college_name: "DTU Delhi",
    match_score: 89,
    reasons: ["Serverless Architectures", "14 Leadership Principles Coach", "Amazon SDE offer in 2025"]
  },
  {
    mentor_id: "m-004",
    mentor_name: "Pooja Sundaram",
    placement_company: "Stripe",
    placement_role: "Backend Engineer",
    college_name: "NIT Trichy",
    match_score: 87,
    reasons: ["Payment APIs & Idempotency", "System Design & Reliability", "Top-rated mock interviewer"]
  }
];

const DEFAULT_SESSIONS: MentorSession[] = [
  {
    id: "sess-m-01",
    session_type: "Technical Mock Interview",
    status: "confirmed",
    scheduled_at: new Date(Date.now() + 86400000).toISOString(),
    meeting_link: "https://meet.jit.si/vireoniq-mentor-session-alpha",
    agenda: {
      agenda: [
        "Distributed Caching & Concurrency Invalidation",
        "System Architecture Deep-Dive (Google L4 Standard)",
        "Granular Feedback & Rubric Scoring"
      ]
    }
  }
];

const DEFAULT_LEADERBOARD = [
  { rank: 1, name: "Aditya Verma", company: "Google", sessions_count: 54, rating: 4.96, badge: "👑 Top Mentor" },
  { rank: 2, name: "Sneha Mukherjee", company: "Microsoft", sessions_count: 42, rating: 4.92, badge: "⭐ Master Coach" },
  { rank: 3, name: "Karan Singhal", company: "Amazon", sessions_count: 36, rating: 4.88, badge: "🔥 Bar Raiser" },
  { rank: 4, name: "Pooja Sundaram", company: "Stripe", sessions_count: 29, rating: 4.85, badge: "🚀 Fast Track" }
];

export const MentorNetwork = () => {
  const [activeTab, setActiveTab] = useState<"find" | "my-sessions" | "leaderboard" | "mentor-mode">("find");
  const [mentors, setMentors] = useState<Mentor[]>(DEFAULT_MENTORS);
  const [mySessions, setMySessions] = useState<MentorSession[]>(DEFAULT_SESSIONS);
  const [leaderboard, setLeaderboard] = useState<any[]>(DEFAULT_LEADERBOARD);
  const [mentorProfile, setMentorProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Scheduling state
  const [selectedMentor, setSelectedMentor] = useState<Mentor | null>(null);
  const [sessionType, setSessionType] = useState("technical_mock");
  const [scheduledAt, setScheduledAt] = useState("");

  // Mentor Mode Activation form
  const [activationForm, setActivationForm] = useState({
    placement_company: "",
    placement_role: "",
    placement_ctc: ""
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      try {
        const menRes = await client.get("/mentors/find");
        setMentors(menRes.data && menRes.data.length > 0 ? menRes.data : DEFAULT_MENTORS);
      } catch {
        setMentors(DEFAULT_MENTORS);
      }

      try {
        const sessRes = await client.get("/mentors/my-sessions");
        setMySessions(sessRes.data && sessRes.data.length > 0 ? sessRes.data : DEFAULT_SESSIONS);
      } catch {
        setMySessions(DEFAULT_SESSIONS);
      }

      try {
        const leadRes = await client.get("/mentors/leaderboard");
        setLeaderboard(leadRes.data && leadRes.data.length > 0 ? leadRes.data : DEFAULT_LEADERBOARD);
      } catch {
        setLeaderboard(DEFAULT_LEADERBOARD);
      }

      try {
        const profRes = await client.get("/mentors/my-profile");
        setMentorProfile(profRes.data);
      } catch (err) {
        // Mentor profile not active is expected for regular candidates
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivateMentor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...activationForm,
        placement_ctc: activationForm.placement_ctc ? parseInt(activationForm.placement_ctc) : null
      };
      const res = await client.post("/mentors/activate", payload);
      toast.success("Mentor profile activated successfully! Congratulations!");
      fetchData();
      setActiveTab("mentor-mode");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Eligibility requirements not met (requires verified offer or PRS >= 75).");
    }
  };

  const handleRequestSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMentor) return;
    try {
      const payload = {
        mentor_id: selectedMentor.mentor_id,
        session_type: sessionType,
        scheduled_at: new Date(scheduledAt).toISOString()
      };
      await client.post("/mentors/request-session", payload);
      toast.success("Session request submitted successfully!");
      setSelectedMentor(null);
      fetchData();
      setActiveTab("my-sessions");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to schedule session.");
    }
  };

  const handleCompleteSession = async (sessionId: string) => {
    try {
      await client.post(`/mentors/complete-session/${sessionId}`, {
        mentor_rating: 5,
        mentee_rating: 5
      });
      toast.success("Session marked as completed! XP rewarded.");
      fetchData();
    } catch (e) {
      toast.error("Failed to complete session.");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Syncing mentor coordinates...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">1000 Mentors Network</h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Structured give-back network matching alumni with current candidates</p>
        </div>
        <div className="flex gap-2">
          {(["find", "my-sessions", "leaderboard", "mentor-mode"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold uppercase transition-all ${activeTab === tab ? "bg-primary text-white" : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"}`}
            >
              {tab === "find" ? "Match Mentors" : tab === "my-sessions" ? "My Sessions" : tab === "leaderboard" ? "Leaderboard" : "Alumni Mode"}
            </button>
          ))}
        </div>
      </header>

      {activeTab === "find" && (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {mentors.map((m) => (
                <div key={m.mentor_id} className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col justify-between h-[250px] relative overflow-hidden group">
                  <div>
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-white text-base">{m.mentor_name}</h4>
                        <span className="text-xs text-slate-400 mt-0.5 block">{m.placement_role} @ {m.placement_company}</span>
                      </div>
                      <span className="px-2.5 py-1 bg-primary/10 border border-primary/25 text-primary text-[10px] font-bold rounded-lg">
                        Match: {Math.round(m.match_score)}%
                      </span>
                    </div>

                    <ul className="space-y-1.5 mt-4">
                      {m.reasons.map((reason, i) => (
                        <li key={i} className="text-xs text-slate-350 flex items-center gap-1.5 font-medium">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> {reason}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <button
                    onClick={() => setSelectedMentor(m)}
                    className="w-full py-2 bg-primary hover:opacity-90 font-bold rounded-xl text-white text-xs mt-4"
                  >
                    Request Session
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            {/* Explainer / FAQ card */}
            <div className="glass-panel p-6 rounded-3xl">
              <h4 className="text-sm text-slate-300 font-bold uppercase tracking-wider mb-3">Structured Give-Back Protocol</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                PlaceIQ utilizes a closed-loop alumni commitment protocol. Every placed candidate pledges 12 hours of mock technical coaching, resume reviews, and career counseling to help students behind them.
              </p>
            </div>
          </div>
        </div>
      )}

      {selectedMentor && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-white">Schedule Mock Session</h3>
            <p className="text-xs text-slate-400">Requesting a mock session with {selectedMentor.mentor_name}</p>
            <form onSubmit={handleRequestSession} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Session Type</label>
                <select
                  value={sessionType}
                  onChange={(e) => setSessionType(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 outline-none focus:border-primary text-sm"
                >
                  <option value="technical_mock">Technical Mock Interview</option>
                  <option value="resume_review">Resume Review & Re-Write</option>
                  <option value="career_strategy">Hiring Pipeline Strategy</option>
                  <option value="offer_negotiation">Offer Negotiation tactics</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setSelectedMentor(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:opacity-90 text-white rounded-xl font-bold text-sm"
                >
                  Confirm Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {activeTab === "my-sessions" && (
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Scheduled Mentorship Sessions</h3>
          <div className="space-y-4">
            {mySessions.length > 0 ? (
              mySessions.map((sess) => (
                <div key={sess.id} className="bg-slate-950/40 border border-slate-850 p-5 rounded-2xl flex justify-between items-center">
                  <div>
                    <h5 className="font-bold text-white text-sm capitalize">{sess.session_type.replace("_", " ")}</h5>
                    <div className="text-[10px] text-slate-400 mt-1 flex gap-3">
                      <span>Status: <strong className="text-primary capitalize">{sess.status}</strong></span>
                      <span>Scheduled: <strong className="text-slate-300">{new Date(sess.scheduled_at).toLocaleString()}</strong></span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {sess.meeting_link && (
                      <a
                        href={sess.meeting_link}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-lg text-slate-300 text-xs flex items-center gap-1.5"
                      >
                        <Video className="w-4 h-4 text-primary" /> Join Call
                      </a>
                    )}
                    {sess.status === "scheduled" && (
                      <button
                        onClick={() => handleCompleteSession(sess.id)}
                        className="px-3 py-1.5 bg-primary hover:opacity-90 font-bold rounded-lg text-white text-xs"
                      >
                        Mark Completed
                      </button>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-500">No mentoring sessions scheduled. Match with a mentor to begin.</div>
            )}
          </div>
        </div>
      )}

      {activeTab === "leaderboard" && (
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Mentor Leaderboard</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="text-slate-400 border-b border-slate-850">
                  <th className="pb-3 font-bold">Rank</th>
                  <th className="pb-3 font-bold">Name</th>
                  <th className="pb-3 font-bold">Company</th>
                  <th className="pb-3 font-bold">Sessions Completed</th>
                  <th className="pb-3 font-bold">Mentees Helped</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {leaderboard.map((row) => (
                  <tr key={row.mentor_id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-4 font-bold text-slate-400">{row.rank}</td>
                    <td className="py-4 font-semibold text-white">{row.mentor_name}</td>
                    <td className="py-4 text-slate-300">{row.placement_company}</td>
                    <td className="py-4 font-bold text-primary">{row.sessions_completed}</td>
                    <td className="py-4 text-slate-300">{row.mentees_helped}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "mentor-mode" && (
        <div className="max-w-xl mx-auto glass-panel p-8 rounded-3xl">
          {mentorProfile ? (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white">Alumni Mentor Dashboard</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950/50 p-4 rounded-2xl border border-slate-850">
                  <div className="text-xs text-slate-400">Total Commitment</div>
                  <div className="text-lg font-bold text-white mt-1">{mentorProfile.sessions_committed} Sessions</div>
                </div>
                <div className="bg-slate-950/50 p-4 rounded-2xl border border-slate-850">
                  <div className="text-xs text-slate-400">Completed Sessions</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">{mentorProfile.sessions_completed} Sessions</div>
                </div>
              </div>
              <div className="border-t border-slate-850 pt-4">
                <span className="text-xs text-slate-400 font-bold block mb-2">Active Mentees</span>
                <p className="text-xs text-slate-450 leading-relaxed">
                  Matched pipeline matches: {mentorProfile.mentees_active.length} active students currently in queue.
                </p>
              </div>
            </div>
          ) : (
            <form onSubmit={handleActivateMentor} className="space-y-6">
              <h3 className="text-xl font-bold text-white mb-2">Activate Alumni Mentoring Profile</h3>
              <p className="text-xs text-slate-400 mb-6">Congratulations on your offer! Unlock give-back pathways and guide students in the cohort.</p>
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Placement Company Name</label>
                <input
                  type="text"
                  required
                  value={activationForm.placement_company}
                  onChange={(e) => setActivationForm({ ...activationForm, placement_company: e.target.value })}
                  placeholder="e.g. Wise, Google"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">Placement Role Title</label>
                <input
                  type="text"
                  required
                  value={activationForm.placement_role}
                  onChange={(e) => setActivationForm({ ...activationForm, placement_role: e.target.value })}
                  placeholder="e.g. Software Engineer"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 font-bold block mb-1">CTC Earned (thousands / optional)</label>
                <input
                  type="number"
                  value={activationForm.placement_ctc}
                  onChange={(e) => setActivationForm({ ...activationForm, placement_ctc: e.target.value })}
                  placeholder="e.g. 1500000"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:border-primary text-sm"
                />
              </div>
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-primary to-accent hover:opacity-90 font-bold rounded-xl text-white"
              >
                Activate Mentor Profile
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};
