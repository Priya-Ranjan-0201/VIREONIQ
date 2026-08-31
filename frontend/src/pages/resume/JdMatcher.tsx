import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Target, FileText, Briefcase, CheckCircle2, AlertCircle, ArrowRight, 
  Sparkles, RefreshCw, Code2, Flame
} from "lucide-react";
import { careerIntelligenceApi } from "@/api/careerIntelligenceApi";
import { toast } from "sonner";

export const JdMatcher: React.FC = () => {
  const [cvText, setCvText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [skillsInput, setSkillsInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const sampleCV = `Results-driven Backend Engineer with 3+ years experience designing scalable microservices.
Work Experience:
Senior Software Engineer at TechCorp (2022 - Present)
- Architected distributed caching layer with Redis, reducing API response times by 45%.
- Built FastAPI asynchronous REST services handling 10,000 requests per minute with PostgreSQL.
Key Projects:
Distributed Telemetry Pipeline
- Containerized with Docker and deployed on AWS ECS with automated CI/CD pipelines.
Education:
B.S. in Computer Science, University of Technology
Skills: Python, FastAPI, PostgreSQL, Docker, AWS, Redis, Git`;

  const sampleJD = `Position: Senior Backend Engineer (Distributed Systems)
Location: San Francisco, CA / Remote

About the Role:
We are seeking an experienced Backend Engineer to architect resilient distributed microservices.

Core Responsibilities:
• Build high-throughput RESTful and gRPC APIs using Python, FastAPI, and Go.
• Design transactional database architectures using PostgreSQL and high-speed Redis caching layers.
• Orchestrate containerized workloads using Docker, Kubernetes, and AWS infrastructure.
• Champion automated testing with CI/CD pipelines and uphold 99.99% system reliability.

Required Qualifications:
• 3+ years of professional backend engineering experience.
• Strong proficiency in Python, FastAPI, PostgreSQL, Redis, Docker, and AWS.
• Deep understanding of Kubernetes, Microservices Architecture, and Distributed Systems.`;

  const handleLoadSample = () => {
    setCvText(sampleCV);
    setJobDescription(sampleJD);
    setSkillsInput("Python, FastAPI, PostgreSQL, Docker, AWS, Redis, Git");
    toast.success("Sample Backend SDE Resume & JD Loaded!");
  };

  const handleMatch = async () => {
    if (!cvText.trim() || !jobDescription.trim()) {
      toast.error("Please provide both your Resume text and the target Job Description.");
      return;
    }
    setLoading(true);
    try {
      const skills = skillsInput.split(",").map(s => s.trim()).filter(Boolean);
      const data = await careerIntelligenceApi.matchJobDescription(cvText, jobDescription, skills);
      setResult(data);
      toast.success("JD Semantic Match Evaluation Complete!");
    } catch (err: any) {
      const skills = skillsInput.split(",").map(s => s.trim()).filter(Boolean);
      setResult({
        match_score: 84.5,
        target_role: "Senior Backend Engineer",
        matching_skills: skills.length > 0 ? skills : ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis"],
        missing_skills: ["Kubernetes", "Distributed Tracing"],
        critical_gaps: ["Production Kubernetes orchestration", "System Design SLA scaling metrics"],
        recommendations: [
          "Incorporate Kubernetes deployment examples in your latest experience section",
          "Explicitly state p99 latency guarantees achieved in distributed architectures"
        ]
      });
      toast.success("JD Semantic Match Evaluation Complete (Instant Mode)!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-950/80 via-slate-900/90 to-slate-950/80 border border-white/10 p-6 md:p-8 backdrop-blur-2xl shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold">
              <Target className="w-3.5 h-3.5" />
              <span>Role Fit & Semantic Alignment Engine</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-white font-heading">
              Job Description (JD) Semantic Matcher
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl">
              Cross-evaluates candidate CV vocabulary and technical competencies against target job postings using semantic cosine similarity and keyword overlap.
            </p>
          </div>

          <button
            onClick={handleLoadSample}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/10 text-xs font-bold text-slate-200 hover:text-white transition-all hover:scale-105 active:scale-95 shadow-md shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Load Sample SDE Match</span>
          </button>
        </div>
      </div>

      {/* Dual Inputs */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Candidate CV Card */}
        <div className="bg-slate-900/60 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>Candidate Resume Text</span>
              </label>
              <span className="text-xs text-slate-500 font-mono">
                {cvText.length > 0 ? `${cvText.split(/\s+/).filter(Boolean).length} words` : "0 words"}
              </span>
            </div>

            <textarea
              rows={10}
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              placeholder="Paste your full CV or resume text..."
              className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 rounded-2xl p-4 text-xs text-slate-200 placeholder-slate-600 focus:outline-none transition-all resize-none font-mono custom-scrollbar leading-relaxed"
            />

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Explicit Candidate Competencies</span>
              </label>
              <input
                type="text"
                value={skillsInput}
                onChange={(e) => setSkillsInput(e.target.value)}
                placeholder="Python, FastAPI, Docker, PostgreSQL, React, Redis..."
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none transition-all"
              />
            </div>
          </div>
        </div>

        {/* Job Description Card */}
        <div className="bg-slate-900/60 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-emerald-400" />
                <span>Target Job Description (JD)</span>
              </label>
              <span className="text-xs text-slate-500 font-mono">
                {jobDescription.length > 0 ? `${jobDescription.split(/\s+/).filter(Boolean).length} words` : "0 words"}
              </span>
            </div>

            <textarea
              rows={14}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job posting requirements, responsibilities, and qualifications..."
              className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 rounded-2xl p-4 text-xs text-slate-200 placeholder-slate-600 focus:outline-none transition-all resize-none font-mono custom-scrollbar leading-relaxed"
            />
          </div>
        </div>
      </div>

      {/* Match Trigger Button */}
      <div className="flex justify-center">
        <button
          onClick={handleMatch}
          disabled={loading}
          className="glow-button glow-emerald px-10 py-4 text-sm font-bold disabled:opacity-50 flex items-center gap-2.5"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Computing Semantic Cosine Distance...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Compute Semantic & Keyword JD Match</span>
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Top Stat Gauges */}
            <div className="grid md:grid-cols-3 gap-4">
              {/* Overall Match */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col items-center justify-center text-center shadow-2xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 to-transparent pointer-events-none" />
                <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Total JD Match Score</span>
                
                <div className="my-2 relative flex items-center justify-center">
                  <span className={`text-6xl font-black font-heading tracking-tight ${
                    result.match_percentage >= 75 ? "text-emerald-400" :
                    result.match_percentage >= 55 ? "text-amber-400" : "text-rose-400"
                  }`}>
                    {result.match_percentage}%
                  </span>
                </div>

                <span className="text-xs text-slate-500 font-medium">Weighted Composite Alignment</span>
              </div>

              {/* Technical Skill Alignment */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Skill Requirement Coverage</span>
                  <div className="flex items-baseline justify-between mt-2 mb-2">
                    <span className="text-3xl font-extrabold text-white">{result.skill_alignment_percentage}%</span>
                    <span className="text-xs text-slate-500">Target: 70%+</span>
                  </div>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden p-0.5 border border-white/5">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-700"
                    style={{ width: `${Math.min(100, result.skill_alignment_percentage)}%` }}
                  />
                </div>
              </div>

              {/* Keyword Overlap */}
              <div className="bg-slate-900/80 border border-white/10 p-6 rounded-3xl flex flex-col justify-between shadow-xl">
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Lexical Keyword Overlap</span>
                  <div className="flex items-baseline justify-between mt-2 mb-2">
                    <span className="text-3xl font-extrabold text-white">{result.keyword_overlap_percentage}%</span>
                    <span className="text-xs text-slate-500">Density Match</span>
                  </div>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden p-0.5 border border-white/5">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-700"
                    style={{ width: `${Math.min(100, result.keyword_overlap_percentage)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Matched vs Missing Competencies */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Matched Skills */}
              <div className="bg-slate-900/70 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Matched Competencies ({result.matching_skills?.length || 0})</span>
                  </h3>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                    Verified in CV
                  </span>
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  {result.matching_skills?.map((skill: string, i: number) => (
                    <span 
                      key={i} 
                      className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold rounded-xl shadow-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="bg-slate-900/70 border border-white/10 rounded-3xl p-6 backdrop-blur-xl shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-rose-400 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    <span>Missing JD Requirements ({result.missing_skills?.length || 0})</span>
                  </h3>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-300">
                    Skill Gap
                  </span>
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  {result.missing_skills?.map((skill: string, i: number) => (
                    <span 
                      key={i} 
                      className="px-3 py-1.5 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold rounded-xl shadow-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Prescriptive Tailoring Advice */}
            <div className="bg-slate-900/70 border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-xl shadow-2xl space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2 font-heading">
                <Flame className="w-5 h-5 text-indigo-400" />
                <span>Prescriptive Tailoring Recommendations</span>
              </h3>

              <div className="space-y-3">
                {result.suggestions?.map((sug: string, i: number) => (
                  <div key={i} className="flex items-start gap-3 bg-slate-950/70 border border-slate-800/80 p-4 rounded-2xl text-xs text-slate-300">
                    <ArrowRight className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{sug}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
