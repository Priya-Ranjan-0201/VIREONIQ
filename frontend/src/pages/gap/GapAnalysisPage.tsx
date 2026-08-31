import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Target, ArrowRight, BrainCircuit, Activity, Zap, Shield, Code } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useGapStore } from "../../store/gapStore";

export const GapAnalysisPage = () => {
  const { analysis, isLoading, error, analyzeGap, fetchHistory } = useGapStore();
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [companyType, setCompanyType] = useState("Product");

  useEffect(() => {
    // Optionally fetch latest history on mount
    fetchHistory();
  }, [fetchHistory]);

  const handleAnalyze = () => {
    analyzeGap({
      target_role: targetRole,
      company_type: companyType,
      experience_level_years: 2,
    });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.6)]';
      case 'moderate': return 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.6)]';
      case 'minor': return 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.6)]';
      default: return 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.6)]';
    }
  };

  const dimensions = analysis ? [
    { name: "Technical Core", score: analysis.technical_gap_score, severity: analysis.technical_gap_severity, icon: Code },
    { name: "Project Depth", score: analysis.project_gap_score, severity: analysis.project_gap_severity, icon: Zap },
    { name: "Communication", score: analysis.communication_gap_score, severity: analysis.communication_gap_severity, icon: BrainCircuit },
    { name: "Confidence", score: analysis.confidence_gap_score, severity: analysis.confidence_gap_severity, icon: Activity },
    { name: "Consistency", score: analysis.consistency_gap_score, severity: analysis.consistency_gap_severity, icon: Shield },
  ] : [];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 via-emerald-400 to-amber-400 bg-clip-text text-transparent">5-Dimensional Gap Analysis</h2>
          <p className="text-[#9CA3AF] mt-2">AI-driven evaluation of your readiness against market standards.</p>
        </div>
        {analysis && (
           <Button onClick={handleAnalyze} disabled={isLoading} className="rounded-xl" variant="outline">
             {isLoading ? "Analyzing..." : "Re-Analyze"}
           </Button>
        )}
      </header>

      {!analysis && !isLoading && (
        <Card className="glass-panel flex flex-col items-center justify-center p-12 text-center rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.5)]">
          <Target className="w-16 h-16 text-indigo-500 mb-6 animate-bounce drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]" />
          <h3 className="text-2xl font-bold text-white mb-2">Configure Your Target</h3>
          <p className="text-slate-400 max-w-md mb-8">We will scan your parsed resume and run a deep multi-dimensional analysis to measure your placement probability.</p>
          
          <div className="flex gap-4 mb-8 w-full max-w-md">
             <input 
               type="text" 
               value={targetRole} 
               onChange={e => setTargetRole(e.target.value)} 
               className="flex-1 bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-white" 
               placeholder="Role (e.g. Backend Developer)"
             />
             <select 
               value={companyType} 
               onChange={e => setCompanyType(e.target.value)}
               className="bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-white"
             >
               <option value="Product">Product</option>
               <option value="Startup">Startup</option>
               <option value="Service">Service</option>
             </select>
          </div>
          <Button size="lg" onClick={handleAnalyze} className="rounded-full px-12 glow-button">
            Run AI Analysis
          </Button>
          {error && <p className="text-red-400 mt-4 text-sm">{error}</p>}
        </Card>
      )}

      {isLoading && (
         <Card className="glass-panel p-12 flex flex-col items-center justify-center rounded-3xl">
            <Activity className="w-12 h-12 text-indigo-500 animate-pulse mb-6 drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]" />
            <h3 className="text-xl font-bold text-white mb-2">Analyzing Resume Neural Vectors</h3>
            <p className="text-slate-400">Computing multidimensional gaps for {targetRole}...</p>
         </Card>
      )}

      {analysis && !isLoading && (
        <div className="grid gap-6 lg:grid-cols-3">
           <Card className="glass-panel overflow-hidden lg:col-span-2 rounded-3xl">
              <div className="bg-gradient-to-r from-indigo-500/20 to-transparent p-8 border-b border-white/5 flex justify-between items-center">
                 <div>
                    <h3 className="text-2xl font-bold text-slate-100">Target: {analysis.target_role_name}</h3>
                    <p className="text-sm text-primary font-semibold tracking-wide uppercase mt-1">Company Type: {analysis.company_type}</p>
                 </div>
                 <div className="text-right">
                    <p className="text-4xl font-black text-white">{analysis.overall_readiness_score}<span className="text-lg text-slate-400 font-normal">/100</span></p>
                    <p className="text-xs text-slate-400 uppercase tracking-widest mt-1">Overall Readiness</p>
                 </div>
              </div>
              <CardContent className="p-8">
                 <h4 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">The 5 Dimensions</h4>
                 <div className="space-y-6">
                    {dimensions.map((dim) => (
                      <div key={dim.name} className="space-y-2 group">
                         <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2">
                               <dim.icon className="w-4 h-4 text-slate-400 group-hover:text-primary transition-colors" />
                               <span className="font-semibold text-slate-200">{dim.name}</span>
                            </div>
                            <div className="flex items-center gap-3">
                               <span className="text-xs text-slate-500 font-medium">{dim.severity}</span>
                               <span className="font-bold text-white">{dim.score}%</span>
                            </div>
                         </div>
                         <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
                            <div className={cn("h-full transition-all duration-1000", getSeverityColor(dim.severity).split(' ')[0])} style={{ width: `${dim.score}%`}} />
                         </div>
                      </div>
                    ))}
                 </div>
              </CardContent>
           </Card>

           <div className="space-y-6">
              <Card className="glass-panel bg-gradient-to-br from-indigo-500/10 to-emerald-500/10 border-indigo-500/20 rounded-3xl">
                 <CardContent className="p-6">
                    <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-4">Placement Probability</h4>
                    <div className="flex items-end gap-2 mb-2">
                       <span className="text-5xl font-black text-white">{analysis.placement_probability}%</span>
                    </div>
                    <p className="text-sm text-slate-300">Based on market trends for {analysis.company_type} companies.</p>
                 </CardContent>
              </Card>

              <Card className="glass-panel rounded-3xl">
                 <CardContent className="p-6">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-4">Expected Salary Band</h4>
                    <div className="flex items-center gap-3">
                       <Zap className="w-8 h-8 text-emerald-500" />
                       <span className="text-2xl font-bold text-white">{analysis.expected_salary_band}</span>
                    </div>
                 </CardContent>
              </Card>

              {analysis.missing_skills?.length > 0 && (
                <Card className="glass-panel border-amber-500/30 rounded-3xl">
                   <CardContent className="p-6">
                      <h4 className="text-xs font-bold text-red-400 uppercase tracking-widest mb-4">Critical Missing Skills</h4>
                      <div className="flex flex-wrap gap-2">
                         {analysis.missing_skills.map((skill: string, idx: number) => (
                           <span key={idx} className="bg-red-500/10 text-red-400 px-3 py-1.5 rounded-lg text-sm border border-red-500/20 font-medium">
                             {skill}
                           </span>
                         ))}
                      </div>
                   </CardContent>
                </Card>
              )}
           </div>

           {/* Recommendations Section */}
           <Card className="glass-panel lg:col-span-3 rounded-3xl overflow-hidden mt-6 border-indigo-500/20">
              <div className="bg-slate-900/50 p-6 border-b border-white/5">
                 <h3 className="text-xl font-bold text-slate-100">AI Preparation Blueprint</h3>
                 <p className="text-sm text-slate-400 mt-1">Your actionable 30/60/90-day execution plan based on the gap analysis.</p>
              </div>
              <CardContent className="p-0">
                 <div className="divide-y divide-white/5">
                    {analysis.recommendations?.map((rec: any, idx: number) => (
                      <div key={idx} className="p-6 hover:bg-white/[0.02] transition-colors flex gap-6 group">
                         <div className="flex flex-col items-center justify-center bg-slate-900 border border-white/10 rounded-2xl w-24 h-24 shrink-0 group-hover:border-primary/50 transition-colors">
                            <span className="text-2xl font-black text-white">{rec.time_horizon_days}</span>
                            <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Days</span>
                         </div>
                         <div className="flex flex-col justify-center">
                            <div className="flex items-center gap-2 mb-2">
                               <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded uppercase font-bold tracking-widest border border-primary/20">
                                 {rec.dimension}
                               </span>
                            </div>
                            <p className="text-slate-200 font-medium text-lg leading-snug mb-3">
                               {rec.task_description}
                            </p>
                            {rec.resources?.length > 0 && (
                               <div className="flex gap-4">
                                  {rec.resources.map((res: string, i: number) => (
                                    <a key={i} href={res} target="_blank" rel="noreferrer" className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium">
                                      <ArrowRight className="w-3 h-3" /> Resource {i+1}
                                    </a>
                                  ))}
                               </div>
                            )}
                         </div>
                      </div>
                    ))}
                 </div>
              </CardContent>
           </Card>
        </div>
      )}
    </div>
  );
};
