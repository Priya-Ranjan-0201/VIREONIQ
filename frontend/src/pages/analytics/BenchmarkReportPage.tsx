import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { BarChart3, Globe, Users2, Trophy, ArrowUpRight, ArrowDownRight, Info } from "lucide-react";
import { reportApi } from "@/api/reportApi";
import type { BenchmarkReport } from "@/api/reportApi";
import { cn } from "@/lib/utils";

export const BenchmarkReportPage = () => {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    reportApi.getBenchmarkReport()
      .then(setReport)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div className="h-full flex items-center justify-center"><BarChart3 className="w-8 h-8 text-primary animate-pulse" /></div>;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-50">Talent Benchmarking</h2>
          <p className="text-slate-400 mt-2">See how you stack up against the global pool of candidates for your target role.</p>
        </div>
        <div className="bg-primary/10 border border-primary/20 px-4 py-2 rounded-2xl flex items-center gap-3">
           <Trophy className="w-5 h-5 text-primary" />
           <div className="text-sm">
              <span className="text-slate-400">Global Ranking:</span>
              <span className="ml-2 font-bold text-white">Top {100 - (report?.percentile_ranking || 0)}%</span>
           </div>
        </div>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
         {/* Peer Comparison Cards */}
         {[
           { label: "ATS Score", key: "ats", value: report?.user_metrics.ats_score, diff: report?.peer_comparison.ats },
           { label: "Technical", key: "technical", value: report?.user_metrics.interview_readiness.technical, diff: report?.peer_comparison.technical },
           { label: "Communication", key: "communication", value: report?.user_metrics.interview_readiness.communication, diff: report?.peer_comparison.communication },
         ].map((item) => (
           <Card key={item.key} className="bg-slate-950 border-white/10 rounded-3xl overflow-hidden shadow-2xl transition-all hover:border-primary/30">
              <CardContent className="p-6">
                 <div className="flex justify-between items-start mb-4">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{item.label}</p>
                    <div className={cn(
                      "flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full",
                      (item.diff || 0) >= 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                    )}>
                       {(item.diff || 0) >= 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                       {Math.abs(Math.round(item.diff || 0))}% vs Peers
                    </div>
                 </div>
                 <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-black text-white">{Math.round(item.value || 0)}%</span>
                    <span className="text-xs text-slate-500 font-medium">Readiness</span>
                 </div>
              </CardContent>
           </Card>
         ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
         {/* Detailed Insights */}
         <Card className="bg-slate-950 border-white/10 lg:col-span-8 rounded-3xl overflow-hidden shadow-2xl">
            <CardHeader className="p-8 border-b border-white/5 flex flex-row items-center justify-between">
               <CardTitle className="text-lg font-bold flex items-center gap-3">
                  <Globe className="w-5 h-5 text-primary" /> Readiness Summary
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8">
               <p className="text-slate-300 leading-relaxed text-lg italic">
                  "{report?.readiness_summary}"
               </p>
               <div className="mt-8 pt-8 border-t border-white/5 flex gap-8">
                  <div className="flex flex-col">
                     <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Global Avg</span>
                     <span className="text-xl font-bold text-slate-100">{report?.global_averages.ats_score}%</span>
                  </div>
                  <div className="flex flex-col">
                     <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Peer Percentile</span>
                     <span className="text-xl font-bold text-slate-100">{report?.percentile_ranking}th</span>
                  </div>
               </div>
            </CardContent>
         </Card>

         {/* Competitive Edge */}
         <Card className="bg-slate-950 border-white/10 lg:col-span-4 rounded-3xl overflow-hidden shadow-2xl">
            <CardHeader className="p-6 border-b border-white/5">
               <CardTitle className="text-sm font-bold flex items-center gap-2">
                  <Users2 className="w-4 h-4 text-primary" /> Peer Distribution
               </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
               <div className="space-y-6">
                  <div>
                     <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest mb-2">
                        <span className="text-slate-500">Tier 1 candidates</span>
                        <span className="text-slate-300">Top 5%</span>
                     </div>
                     <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-primary w-[5%] shadow-[0_0_10px_rgba(var(--primary),0.5)]" />
                     </div>
                  </div>
                  <div>
                     <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest mb-2">
                        <span className="text-slate-500">Your Standing</span>
                        <span className="text-primary font-black">Top {100 - (report?.percentile_ranking || 0)}%</span>
                     </div>
                     <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-primary/40" style={{ width: `${100 - (report?.percentile_ranking || 0)}%` }} />
                     </div>
                  </div>
               </div>
               <div className="mt-8 p-4 bg-primary/5 border border-primary/10 rounded-2xl flex gap-3">
                  <Info className="w-4 h-4 text-primary shrink-0" />
                  <p className="text-[10px] text-slate-400 leading-normal italic">
                     These metrics are derived from real-time global talent data within the PLACEIQ ecosystem and historical Big Tech placement benchmarks.
                  </p>
               </div>
            </CardContent>
         </Card>
      </div>
    </div>
  );
};
