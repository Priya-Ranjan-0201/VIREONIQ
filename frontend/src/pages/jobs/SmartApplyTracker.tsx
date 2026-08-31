import { useState, useMemo } from "react";
import { 
  ClipboardList, 
  Clock, 
  MessageSquare, 
  Gift, 
  Search, 
  ArrowRight, 
  Target, 
  Plus, 
  Sparkles, 
  Building2, 
  CheckCircle2, 
  X,
  ExternalLink,
  ChevronRight,
  TrendingUp
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Spinner } from "@/components/shared/Spinner";
import { useApplications, useUpdateAppStage } from "@/api/hooks/useCRM";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApplicationDetail } from "./ApplicationDetail";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

const COLUMNS = [
  { id: "saved", label: "Saved", icon: Clock, color: "text-slate-400", bg: "bg-slate-500/10" },
  { id: "applied", label: "Applied", icon: ClipboardList, color: "text-cyan-400", bg: "bg-cyan-500/10" },
  { id: "oa", label: "OA / Assessment", icon: ArrowRight, color: "text-purple-400", bg: "bg-purple-500/10" },
  { id: "interview", label: "Interview", icon: MessageSquare, color: "text-amber-400", bg: "bg-amber-500/10" },
  { id: "final", label: "Final Round", icon: Target, color: "text-rose-400", bg: "bg-rose-500/10" },
  { id: "offer", label: "Offer Received", icon: Gift, color: "text-emerald-400", bg: "bg-emerald-500/10" },
];

const STAGE_ORDER = ["saved", "applied", "oa", "interview", "final", "offer"];

const DEFAULT_APPLICATIONS = [
  {
    id: "app_demo_01",
    status: "interview",
    stage_id: 4,
    updated_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    is_referral: true,
    job: {
      id: "job_01",
      title: "Software Engineer (L3)",
      company_name: "Google",
      location: "Bengaluru",
      salary_min: 2400000,
      salary_max: 4200000
    },
    offer: null,
    events: [
      { id: "ev_1", event_type: "interview", title: "DSA Round 1 Passed (Graph Traversal)", event_date: "2026-08-28" },
      { id: "ev_2", event_type: "interview", title: "Upcoming: Low-Level System Design", event_date: "2026-09-02" }
    ]
  },
  {
    id: "app_demo_02",
    status: "final",
    stage_id: 5,
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    is_referral: false,
    job: {
      id: "job_02",
      title: "Full-Stack Engineer (Platform)",
      company_name: "Swiggy",
      location: "Bengaluru",
      salary_min: 1600000,
      salary_max: 2600000
    },
    offer: null,
    events: [
      { id: "ev_3", event_type: "final", title: "Hiring Manager Bar-Raiser", event_date: "2026-08-31" }
    ]
  },
  {
    id: "app_demo_03",
    status: "offer",
    stage_id: 6,
    updated_at: new Date(Date.now() - 4 * 86400000).toISOString(),
    is_referral: true,
    job: {
      id: "job_03",
      title: "Backend Infrastructure Engineer",
      company_name: "Stripe",
      location: "Remote (India)",
      salary_min: 2800000,
      salary_max: 4800000
    },
    offer: {
      id: "off_1",
      base_salary: 3200000,
      bonus: 400000,
      equity_value: 1200000,
      location: "Remote (India)",
      deadline: new Date(Date.now() + 10 * 86400000).toISOString()
    },
    events: []
  },
  {
    id: "app_demo_04",
    status: "oa",
    stage_id: 3,
    updated_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    is_referral: false,
    job: {
      id: "job_04",
      title: "High-Throughput Core Systems Engineer",
      company_name: "Zepto",
      location: "Mumbai",
      salary_min: 1500000,
      salary_max: 2500000
    },
    offer: null,
    events: [
      { id: "ev_4", event_type: "oa", title: "HackerRank 90m OA Completed", event_date: "2026-08-27" }
    ]
  },
  {
    id: "app_demo_05",
    status: "applied",
    stage_id: 2,
    updated_at: new Date().toISOString(),
    is_referral: true,
    job: {
      id: "job_05",
      title: "Software Development Engineer I",
      company_name: "Amazon",
      location: "Hyderabad",
      salary_min: 2200000,
      salary_max: 3200000
    },
    offer: null,
    events: []
  }
];

export const SmartApplyTracker = () => {
  const { data: serverApps, isLoading } = useApplications();
  const { mutate: updateStage } = useUpdateAppStage();

  const [localApps, setLocalApps] = useState<any[]>(() => {
    const saved = localStorage.getItem("vireoniq_user_applications");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return DEFAULT_APPLICATIONS;
  });

  const [search, setSearch] = useState("");
  const [selectedApp, setSelectedApp] = useState<any>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newCompany, setNewCompany] = useState("");
  const [newRole, setNewRole] = useState("");
  const [newLocation, setNewLocation] = useState("Bengaluru");
  const [newStage, setNewStage] = useState("applied");
  const [isReferral, setIsReferral] = useState(false);

  // Sync server applications if available
  const allApps = useMemo(() => {
    if (serverApps && serverApps.length > 0) {
      // Merge unique server apps
      const serverMap = new Map();
      serverApps.forEach((a: any) => serverMap.set(a.id, a));
      localApps.forEach((a: any) => {
        if (!serverMap.has(a.id)) serverMap.set(a.id, a);
      });
      return Array.from(serverMap.values());
    }
    return localApps;
  }, [serverApps, localApps]);

  const groupedApps = useMemo(() => {
    const groups: Record<string, any[]> = {};
    COLUMNS.forEach((col) => (groups[col.id] = []));
    allApps.forEach((app: any) => {
      const st = app.status || "saved";
      if (groups[st]) {
        groups[st].push(app);
      } else {
        groups["saved"].push(app);
      }
    });
    return groups;
  }, [allApps]);

  const handleAdvance = (e: React.MouseEvent, app: any) => {
    e.stopPropagation();
    const currentIndex = STAGE_ORDER.indexOf(app.status);
    if (currentIndex < STAGE_ORDER.length - 1) {
      const nextStage = STAGE_ORDER[currentIndex + 1];
      const updated = allApps.map((a) =>
        a.id === app.id ? { ...a, status: nextStage, updated_at: new Date().toISOString() } : a
      );
      setLocalApps(updated);
      localStorage.setItem("vireoniq_user_applications", JSON.stringify(updated));

      try {
        updateStage({ appId: app.id, status: nextStage });
      } catch (err) {}

      toast.success(`Advanced to ${nextStage.toUpperCase()}! +25 XP awarded 🎯`);
    }
  };

  const handleAddApplication = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCompany.trim() || !newRole.trim()) {
      toast.error("Please enter company and role");
      return;
    }

    const newApp = {
      id: "app_custom_" + Date.now(),
      status: newStage,
      stage_id: STAGE_ORDER.indexOf(newStage) + 1,
      updated_at: new Date().toISOString(),
      is_referral: isReferral,
      job: {
        id: "job_custom_" + Date.now(),
        title: newRole,
        company_name: newCompany,
        location: newLocation,
        salary_min: 1800000,
        salary_max: 3000000
      },
      offer: newStage === "offer" ? {
        base_salary: 2400000,
        bonus: 300000,
        equity_value: 600000,
        location: newLocation,
        deadline: new Date(Date.now() + 14 * 86400000).toISOString()
      } : null,
      events: [
        { id: "ev_" + Date.now(), event_type: newStage, title: "Application tracked in pipeline", event_date: new Date().toISOString().split("T")[0] }
      ]
    };

    const updated = [newApp, ...localApps];
    setLocalApps(updated);
    localStorage.setItem("vireoniq_user_applications", JSON.stringify(updated));
    setShowAddModal(false);
    setNewCompany("");
    setNewRole("");
    toast.success(`Application for ${newCompany} tracked! +50 XP 🚀`);
  };

  if (isLoading) return <div className="h-[60vh] flex items-center justify-center"><Spinner className="w-8 h-8" /></div>;

  return (
    <div className="flex flex-col space-y-6 animate-fade-in pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-400 tracking-wide uppercase mb-1">
            <ClipboardList className="w-3.5 h-3.5" /> High-Priority Candidate CRM
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
              <Building2 className="w-5 h-5" />
            </div>
            Application Tracker
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Tracking {allApps.length} active opportunities across top MNCs and high-growth scaleups.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5 w-full md:w-auto">
          <Button
            onClick={() => setShowAddModal(true)}
            className="rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/20"
          >
            <Plus className="w-4 h-4 mr-1.5" /> Track New Job
          </Button>

          <Link to="/app/offer-comparison">
            <Button variant="outline" className="rounded-xl border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs font-bold">
              <Gift className="w-4 h-4 mr-1.5" /> Offer Comparator
            </Button>
          </Link>

          <div className="relative flex-1 md:w-56">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies..." 
              className="pl-9 h-10 bg-slate-950 border-white/10 rounded-xl text-xs"
            />
          </div>
        </div>
      </header>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-6 custom-scrollbar min-h-[560px]">
        {COLUMNS.map((col) => {
          const colApps = groupedApps[col.id]?.filter((app) =>
            !search || app.job?.company_name?.toLowerCase().includes(search.toLowerCase()) ||
            app.job?.title?.toLowerCase().includes(search.toLowerCase())
          ) || [];

          return (
            <div key={col.id} className="flex flex-col w-[290px] shrink-0 space-y-3">
              <div className="flex items-center justify-between px-2 py-1">
                <div className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded-lg ${col.bg} flex items-center justify-center`}>
                    <col.icon className={cn("w-3.5 h-3.5", col.color)} />
                  </div>
                  <h3 className="font-black text-slate-200 text-xs uppercase tracking-wider">{col.label}</h3>
                </div>
                <Badge variant="outline" className="bg-slate-900 border-white/10 text-xs font-bold px-2 py-0.5">
                  {colApps.length}
                </Badge>
              </div>

              <div className="flex-1 bg-slate-950/60 border border-white/5 rounded-2xl p-2.5 space-y-2.5 overflow-y-auto min-h-[460px]">
                <AnimatePresence mode="popLayout">
                  {colApps.map((app: any) => (
                    <motion.div
                      key={app.id}
                      layout
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                    >
                      <Card 
                        onClick={() => setSelectedApp(app)}
                        className="group bg-slate-900/90 border-white/10 hover:border-cyan-500/50 transition-all cursor-pointer shadow-lg hover:shadow-cyan-500/10 rounded-xl"
                      >
                        <CardContent className="p-4 space-y-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="text-xs font-black text-slate-100 line-clamp-1 group-hover:text-cyan-400 transition-colors">
                                {app.job?.title || "Software Engineer"}
                              </h4>
                              <p className="text-[11px] text-slate-400 font-semibold mt-0.5">
                                {app.job?.company_name || "Company"} • {app.job?.location || "India"}
                              </p>
                            </div>
                            <div className="w-8 h-8 rounded-lg bg-slate-950 border border-white/10 flex items-center justify-center text-xs font-black text-slate-300">
                              {app.job?.company_name ? app.job.company_name[0] : "C"}
                            </div>
                          </div>

                          <div className="flex flex-wrap items-center gap-1.5">
                            {app.is_referral && (
                              <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[9px] font-bold px-2 py-0.5">
                                REFERRAL ACTIVE
                              </Badge>
                            )}
                            {app.offer && (
                              <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-[9px] font-bold px-2 py-0.5">
                                ₹{(app.offer.base_salary / 100000).toFixed(1)}L CTC
                              </Badge>
                            )}
                            {app.events?.length > 0 && (
                              <Badge variant="outline" className="text-[9px] border-white/10 text-slate-400 px-2 py-0.5">
                                {app.events.length} Event{app.events.length > 1 ? "s" : ""}
                              </Badge>
                            )}
                          </div>

                          <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[10px] text-slate-500">
                              {new Date(app.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                            </span>
                            {col.id !== "offer" && (
                              <button 
                                onClick={(e) => handleAdvance(e, app)}
                                className="text-[10px] font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 bg-cyan-500/10 hover:bg-cyan-500/20 px-2 py-1 rounded-lg transition-colors"
                              >
                                Advance Stage <ArrowRight className="w-3 h-3" />
                              </button>
                            )}
                            {col.id === "offer" && (
                              <Link to="/app/offer-comparison" onClick={(e) => e.stopPropagation()}>
                                <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-1 bg-emerald-500/10 px-2 py-1 rounded-lg">
                                  Compare Offer <ChevronRight className="w-3 h-3" />
                                </span>
                              </Link>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {colApps.length === 0 && (
                  <div className="h-32 border border-dashed border-white/5 rounded-xl flex flex-col items-center justify-center text-slate-600 text-[11px] font-semibold p-4 text-center">
                    <span>No applications in this stage</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Track Application Modal */}
      {showAddModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setShowAddModal(false)}
        >
          <div
            className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-md p-6 sm:p-8 space-y-5 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-black text-white">Track New Opportunity</h3>
                <p className="text-xs text-slate-400">Add an active recruitment pipeline to your board</p>
              </div>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddApplication} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-bold mb-1">Company Name</label>
                <input
                  type="text"
                  placeholder="e.g. Google, Stripe, Zepto"
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-300 font-bold mb-1">Job Title</label>
                <input
                  type="text"
                  placeholder="e.g. Software Development Engineer I"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Location</label>
                  <input
                    type="text"
                    placeholder="e.g. Bengaluru / Remote"
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-bold mb-1">Initial Stage</label>
                  <select
                    value={newStage}
                    onChange={(e) => setNewStage(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white outline-none focus:border-cyan-500"
                  >
                    <option value="saved">Saved</option>
                    <option value="applied">Applied</option>
                    <option value="oa">OA / Assessment</option>
                    <option value="interview">Interview</option>
                    <option value="final">Final Round</option>
                    <option value="offer">Offer Received</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 p-3 bg-slate-900 rounded-xl border border-white/5">
                <input
                  type="checkbox"
                  id="referralCheck"
                  checked={isReferral}
                  onChange={(e) => setIsReferral(e.target.checked)}
                  className="w-4 h-4 rounded text-cyan-500"
                />
                <label htmlFor="referralCheck" className="text-slate-300 font-semibold cursor-pointer">
                  Applied via Employee Referral (3.8x Callback Boost)
                </label>
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  variant="outline"
                  className="flex-1 py-5 rounded-xl border-slate-700 text-slate-300 text-xs font-bold"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 py-5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-cyan-600/30"
                >
                  Add to Board 🚀
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <AnimatePresence>
        {selectedApp && (
          <ApplicationDetail 
            application={selectedApp} 
            onClose={() => setSelectedApp(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
};
