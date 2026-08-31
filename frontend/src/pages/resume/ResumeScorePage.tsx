import React, { useState, useEffect, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Upload, FileText, CheckCircle, ArrowLeft, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import client from "@/api/client";
import { toast } from "sonner";

interface ScoreResponse {
  id: string;
  overall_score: number;
  keyword_match_score: number;
  completeness_score: number;
  quantified_achievements_score: number;
  action_verb_score: number;
  formatting_score: number;
  role_relevance_score: number;
  improvement_notes: {
    quantified?: string;
    verbs?: string;
    keywords?: string;
  };
}

interface ResumeScan {
  id: string;
  storage_key: string;
  is_active: boolean;
  scores: ScoreResponse[];
}

export const ResumeScorePage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [history, setHistory] = useState<ResumeScan[]>([]);
  const [activeScan, setActiveScan] = useState<ResumeScan | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch history on mount
  useEffect(() => {
    fetchScanHistory();
  }, []);

  const fetchScanHistory = async () => {
    try {
      const res = await client.get("/resume/history");
      if (res.data && Array.isArray(res.data.resumes)) {
        setHistory(res.data.resumes);
        if (res.data.resumes.length > 0) {
          // Default to showing the most recent scan
          setActiveScan(res.data.resumes[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch resume scan history", error);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Only PDF and DOCX files are allowed.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error("File size exceeds the 5MB limit.");
      return;
    }
    setSelectedFile(file);
    toast.success(`Selected ${file.name}`);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error("Please select a file first.");
      return;
    }
    if (!targetRole.trim()) {
      toast.error("Please specify a target role.");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("target_role", targetRole);

    try {
      const res = await client.post("/resume/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      
      toast.success("Resume parsed and scored successfully! ✨");
      
      if (Array.isArray(res.data) && res.data.length > 0) {
        setHistory(res.data);
        setActiveScan(res.data[0]); // Most recent uploaded
      } else {
        await fetchScanHistory();
      }
    } catch (error: any) {
      const errMsg = error.response?.data?.detail || "Failed to process resume.";
      toast.error(errMsg);
    } finally {
      setSelectedFile(null);
      setIsLoading(false);
    }
  };

  const getCleanFilename = (storageKey: string) => {
    const parts = storageKey.split("_");
    if (parts.length > 1) {
      return parts.slice(1).join("_");
    }
    return storageKey;
  };

  const activeScore = activeScan?.scores && activeScan.scores.length > 0 ? activeScan.scores[0] : null;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-success bg-clip-text text-transparent">Resume Intelligence</h2>
          <p className="text-[#9CA3AF] mt-2">Analyze your resume against ATS algorithms and target roles.</p>
        </div>
        {activeScan && (
          <Button 
            variant="outline" 
            className="border-white/10 bg-white/5 hover:bg-white/10"
            onClick={() => {
              setActiveScan(null);
              setSelectedFile(null);
            }}
          >
            <Upload className="w-4 h-4 mr-2" />
            Scan New Resume
          </Button>
        )}
      </header>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center p-20 glass-panel rounded-3xl min-h-[50vh]">
          <Loader2 className="w-16 h-16 text-primary animate-spin mb-6" />
          <h3 className="text-xl font-bold text-slate-100 mb-2">Analyzing Resume...</h3>
          <p className="text-slate-400 text-sm max-w-xs text-center">
            Parsing document structure, evaluating keyword relevance, and counting action verbs using NLP engines.
          </p>
        </div>
      ) : activeScan && activeScore ? (
        <div className="grid gap-8 lg:grid-cols-4">
          {/* Scan details dashboard */}
          <div className="lg:col-span-3 space-y-6">
            <Card className="glass-panel p-6 border-white/5 rounded-3xl">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Gauge chart */}
                <div className="relative w-36 h-36 flex items-center justify-center rounded-full bg-slate-900 border-4 border-slate-800/50 shadow-inner shrink-0">
                  <svg className="absolute inset-0 w-full h-full transform -rotate-90">
                    <circle
                      cx="72"
                      cy="72"
                      r="64"
                      className="stroke-slate-800/40 fill-none"
                      strokeWidth="8"
                    />
                    <circle
                      cx="72"
                      cy="72"
                      r="64"
                      className="stroke-success fill-none transition-all duration-1000 ease-out"
                      strokeWidth="8"
                      strokeDasharray={402}
                      strokeDashoffset={402 - (402 * activeScore.overall_score) / 100}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="text-4xl font-extrabold text-white">{Math.round(activeScore.overall_score)}%</span>
                </div>

                {/* Meta details */}
                <div className="flex-1 space-y-3 text-center md:text-left">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-success/15 border border-success/30 rounded-full text-xs font-semibold text-success">
                    <CheckCircle className="w-3.5 h-3.5" />
                    Overall Readiness
                  </div>
                  <h3 className="text-xl font-bold text-slate-100 truncate max-w-md">
                    {getCleanFilename(activeScan.storage_key)}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    Scanned against target role settings. Below is the detailed breakdown.
                  </p>
                </div>
              </div>
            </Card>

            {/* Individual breakdown grid */}
            <div className="grid gap-6 md:grid-cols-2">
              <Card className="glass-panel p-6 border-white/5">
                <h4 className="text-sm font-bold text-slate-300 mb-6 uppercase tracking-wider">Scoring Breakdown</h4>
                <div className="space-y-4">
                  {[
                    { label: "Keyword Match", val: activeScore.keyword_match_score, color: "bg-blue-500" },
                    { label: "Completeness", val: activeScore.completeness_score, color: "bg-purple-500" },
                    { label: "Quantified Achievements", val: activeScore.quantified_achievements_score, color: "bg-cyan-500" },
                    { label: "Action Verbs", val: activeScore.action_verb_score, color: "bg-emerald-500" },
                    { label: "Formatting Check", val: activeScore.formatting_score, color: "bg-indigo-500" },
                    { label: "Role Relevance", val: activeScore.role_relevance_score, color: "bg-violet-500" }
                  ].map((item) => (
                    <div key={item.label}>
                      <div className="flex justify-between items-center mb-1 text-xs font-semibold text-slate-300">
                        <span>{item.label}</span>
                        <span>{Math.round(item.val)}%</span>
                      </div>
                      <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-white/5">
                        <div
                          className={`h-full ${item.color} transition-all duration-1000`}
                          style={{ width: `${item.val}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Actionable recommendations */}
              <Card className="glass-panel p-6 border-white/5 flex flex-col justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-300 mb-6 uppercase tracking-wider">Improvement Recommendations</h4>
                  <div className="space-y-4 text-xs text-slate-400">
                    {activeScore.improvement_notes?.keywords && (
                      <div className="flex gap-3">
                        <Sparkles className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                        <p>{activeScore.improvement_notes.keywords}</p>
                      </div>
                    )}
                    {activeScore.improvement_notes?.verbs && (
                      <div className="flex gap-3">
                        <Sparkles className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <p>{activeScore.improvement_notes.verbs}</p>
                      </div>
                    )}
                    {activeScore.improvement_notes?.quantified && (
                      <div className="flex gap-3">
                        <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                        <p>{activeScore.improvement_notes.quantified}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="pt-6 border-t border-white/5 mt-6">
                  <div className="flex items-center gap-2 text-xs text-amber-500 font-medium">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>Scores below 80% should be revised and re-analyzed.</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Sidebar - Recent scans */}
          <div className="lg:col-span-1">
            <Card className="glass-panel p-6 border-white/5 h-full">
              <h4 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Recent Scans</h4>
              <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
                {history.map((scan) => {
                  const score = scan.scores && scan.scores.length > 0 ? scan.scores[0].overall_score : 0;
                  return (
                    <div 
                      key={scan.id} 
                      onClick={() => setActiveScan(scan)}
                      className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer group ${
                        activeScan.id === scan.id
                          ? "bg-primary/10 border-primary/50"
                          : "bg-white/5 border-white/5 hover:border-primary/50 hover:bg-primary/5"
                      }`}
                    >
                      <div className="flex items-center truncate mr-2">
                        <FileText className={`w-4 h-4 mr-3 shrink-0 ${activeScan.id === scan.id ? "text-primary" : "text-slate-400"}`} />
                        <div className="truncate">
                          <p className="text-xs font-semibold text-slate-200 truncate">{getCleanFilename(scan.storage_key)}</p>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-success shrink-0">{Math.round(score)}%</span>
                    </div>
                  );
                })}
                {history.length === 0 && (
                  <p className="text-xs text-slate-500 text-center py-6">No previous scans found.</p>
                )}
              </div>
            </Card>
          </div>
        </div>
      ) : (
        /* Upload interface */
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <form onSubmit={handleUpload}>
              <div className="glass-panel rounded-3xl p-8 space-y-6">
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Target Job Role</label>
                  <input
                    type="text"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/40"
                    placeholder="e.g. Senior Software Engineer"
                    required
                  />
                </div>

                <div 
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center text-center transition-all cursor-pointer group ${
                    isDragging
                      ? "border-primary bg-primary/5 scale-[0.98]"
                      : "border-primary/30 hover:border-primary/60 hover:bg-white/5"
                  }`}
                >
                  <input 
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.docx"
                    className="hidden"
                  />
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent shadow-[0_0_20px_rgba(99,102,241,0.3)] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <Upload className="w-8 h-8 text-white" />
                  </div>
                  {selectedFile ? (
                    <>
                      <h3 className="text-lg font-bold mb-1 text-slate-200">File Selected</h3>
                      <p className="text-sm text-primary font-semibold mb-2">{selectedFile.name}</p>
                      <p className="text-xs text-slate-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </>
                  ) : (
                    <>
                      <h3 className="text-lg font-bold mb-1 text-slate-200">Drag and drop your resume</h3>
                      <p className="text-sm text-slate-400 mb-6 max-w-sm">
                        Supports PDF or Word documents. We'll score against your target role.
                      </p>
                      <Button type="button" size="sm" className="px-6 glow-button">Select File</Button>
                    </>
                  )}
                </div>

                <div className="flex justify-end pt-4">
                  <Button 
                    type="submit" 
                    disabled={!selectedFile || isLoading} 
                    className="w-full md:w-auto px-8 glow-button h-12 font-bold"
                  >
                    Analyze Resume Score
                  </Button>
                </div>
              </div>
            </form>
          </div>

          <div className="lg:col-span-1">
            <Card className="glass-panel p-6 border-white/5 h-full">
              <h4 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Recent Scans</h4>
              <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
                {history.map((scan) => {
                  const score = scan.scores && scan.scores.length > 0 ? scan.scores[0].overall_score : 0;
                  return (
                    <div 
                      key={scan.id} 
                      onClick={() => setActiveScan(scan)}
                      className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer group"
                    >
                      <div className="flex items-center truncate mr-2">
                        <FileText className="w-4 h-4 mr-3 shrink-0 text-slate-400 group-hover:text-primary transition-colors" />
                        <div className="truncate">
                          <p className="text-xs font-semibold text-slate-200 truncate">{getCleanFilename(scan.storage_key)}</p>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-success shrink-0">{Math.round(score)}%</span>
                    </div>
                  );
                })}
                {history.length === 0 && (
                  <p className="text-xs text-slate-500 text-center py-6">No previous scans found.</p>
                )}
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
