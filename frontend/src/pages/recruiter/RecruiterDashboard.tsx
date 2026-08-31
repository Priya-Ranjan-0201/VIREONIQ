import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Search, Filter, Users, Star, ArrowUpRight, ShieldCheck, Mail, FileBarChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { recruiterApi } from "@/api/recruiterApi";
import type { Candidate } from "@/api/recruiterApi";
import { cn } from "@/lib/utils";

export const RecruiterDashboard = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    setIsLoading(true);
    try {
      const data = await recruiterApi.searchCandidates();
      setCandidates(data);
    } catch (error) {
      console.error("Failed to fetch candidates", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-50 flex items-center gap-3">
             <ShieldCheck className="w-8 h-8 text-primary" /> Recruiter Intelligence
          </h2>
          <p className="text-slate-400 mt-2">Discover and acquire top-tier talent vetted by PLACEIQ AI.</p>
        </div>
        <div className="flex gap-4">
           <Button variant="outline" className="rounded-xl border-white/10 bg-slate-900/50">
              <Filter className="w-4 h-4 mr-2" /> Advanced Filters
           </Button>
           <Button className="rounded-xl shadow-2xl">
              <Star className="w-4 h-4 mr-2" /> Premium Candidates
           </Button>
        </div>
      </header>

      {/* Search Bar */}
      <div className="relative group">
         <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-primary transition-colors">
            <Search className="w-5 h-5" />
         </div>
         <input 
           type="text" 
           placeholder="Search by role, skills, or candidate name..." 
           className="w-full bg-slate-950 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all shadow-inner"
           value={searchTerm}
           onChange={(e) => setSearchTerm(e.target.value)}
         />
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
         {/* Candidate List */}
         <Card className="lg:col-span-8 bg-slate-950 border-white/10 rounded-3xl overflow-hidden shadow-2xl">
            <CardHeader className="p-6 border-b border-white/5 bg-slate-900/30">
               <CardTitle className="text-sm font-bold flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary" /> Active Talent Pipeline
               </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
               <div className="divide-y divide-white/5">
                  {isLoading ? (
                    <div className="p-12 text-center text-slate-500 animate-pulse font-medium uppercase tracking-widest text-xs">Loading Pipeline...</div>
                  ) : candidates.length > 0 ? (
                    candidates.map((c) => (
                      <div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.02] transition-colors group">
                         <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg shadow-lg">
                               {c.name[0]}
                            </div>
                            <div>
                               <h4 className="font-bold text-slate-100 group-hover:text-primary transition-colors">{c.name}</h4>
                               <p className="text-xs text-slate-500">{c.role}</p>
                            </div>
                         </div>
                         <div className="flex gap-12 items-center">
                            <div className="text-center">
                               <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-1">ATS Match</p>
                               <p className="font-black text-slate-200">{c.ats_score}%</p>
                            </div>
                            <div className="text-center">
                               <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-1">Readiness</p>
                               <p className={cn(
                                 "font-black",
                                 c.readiness_score > 80 ? "text-emerald-400" : "text-amber-400"
                               )}>{c.readiness_score}%</p>
                            </div>
                            <div className="flex gap-2">
                               <Button size="icon" variant="ghost" className="rounded-xl hover:bg-primary/10 hover:text-primary">
                                  <Mail className="w-4 h-4" />
                               </Button>
                               <Button size="icon" variant="ghost" className="rounded-xl hover:bg-emerald-500/10 hover:text-emerald-500">
                                  <FileBarChart className="w-4 h-4" />
                               </Button>
                               <Button size="icon" variant="ghost" className="rounded-xl hover:bg-accent/10 hover:text-accent">
                                  <ArrowUpRight className="w-4 h-4" />
                               </Button>
                            </div>
                         </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-12 text-center text-slate-600 italic">No candidates found matching your criteria.</div>
                  )}
               </div>
            </CardContent>
         </Card>

         {/* Market Pulse / Insights */}
         <div className="lg:col-span-4 space-y-6">
            <Card className="bg-slate-950 border-white/10 rounded-3xl shadow-2xl overflow-hidden">
               <CardHeader className="p-6 border-b border-white/5 bg-gradient-to-br from-primary/10 to-transparent">
                  <CardTitle className="text-sm font-bold">Talent Pulse</CardTitle>
               </CardHeader>
               <CardContent className="p-6 space-y-4">
                  <div>
                     <p className="text-xs font-semibold text-slate-400 mb-2">High Demand Roles</p>
                     <div className="flex flex-wrap gap-2">
                        {["SDE-2", "DevOps", "AI Engineer"].map(tag => (
                          <span key={tag} className="text-[10px] font-bold bg-white/5 border border-white/5 px-2 py-1 rounded-lg text-slate-300 uppercase tracking-wider">{tag}</span>
                        ))}
                     </div>
                  </div>
                  <div className="pt-4 border-t border-white/5">
                     <p className="text-xs font-semibold text-slate-400 mb-2">Placement Velocity</p>
                     <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 w-[72%] shadow-[0_0_10px_rgba(16,185,129,0.4)]" />
                     </div>
                     <p className="text-[10px] text-slate-600 mt-2 italic">72% of Tier-1 candidates placed within 30 days.</p>
                  </div>
               </CardContent>
            </Card>

            <Card className="bg-primary/5 border border-primary/20 rounded-3xl p-6 shadow-2xl relative overflow-hidden group">
               <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <Star className="w-24 h-24 text-primary" />
               </div>
               <h3 className="text-lg font-bold text-white mb-2">Talent Acquisition AI</h3>
               <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  PLACEIQ AI has flagged 4 new candidates matching your "Big Tech" criteria in the last 24 hours.
               </p>
               <Button className="w-full rounded-xl bg-primary hover:bg-primary/90 text-white font-bold">
                  View Flagged Talent
               </Button>
            </Card>
         </div>
      </div>
    </div>
  );
};
