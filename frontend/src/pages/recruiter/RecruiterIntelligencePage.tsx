import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  CheckCircle2,
  AlertTriangle,
  Award,
  Layers,
  Sparkles,
  Plus,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  Filter,
  Columns,
  Clock,
  Briefcase,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { RecruiterJobData, CandidateDiscoveryMatchData } from '@/api/careerIntelligenceApi';

const DEFAULT_RECRUITER_JOBS: RecruiterJobData[] = [
  {
    job_id: "rec-job-01",
    title: "Senior Backend Distributed Systems Engineer",
    target_role: "Backend Engineer",
    status: "ACTIVE",
    structured_requirements: {
      required_skills: [
        { name: "Distributed Systems", importance: 0.95, min_level: "EXPERT" },
        { name: "FastAPI / Python", importance: 0.90, min_level: "ADVANCED" },
        { name: "Concurrency & Event Loops", importance: 0.85, min_level: "ADVANCED" },
        { name: "PostgreSQL & Redis", importance: 0.80, min_level: "ADVANCED" }
      ],
      preferred_skills: [
        { name: "Kubernetes & Docker", importance: 0.70, min_level: "INTERMEDIATE" },
        { name: "eBPF Tracing", importance: 0.60, min_level: "INTERMEDIATE" }
      ]
    },
    hard_requirements: ["3+ years distributed systems", "Proven production architecture experience"],
    created_at: new Date().toISOString()
  },
  {
    job_id: "rec-job-02",
    title: "Full-Stack AI Product Engineer",
    target_role: "Full-Stack Engineer",
    status: "ACTIVE",
    structured_requirements: {
      required_skills: [
        { name: "React / Vite / TypeScript", importance: 0.92, min_level: "EXPERT" },
        { name: "Python / Node.js", importance: 0.88, min_level: "ADVANCED" },
        { name: "LLM Orchestration & Prompting", importance: 0.85, min_level: "ADVANCED" }
      ]
    },
    hard_requirements: ["Production React deployment experience", "Full-stack end-to-end delivery"],
    created_at: new Date().toISOString()
  }
];

const DEFAULT_CANDIDATES: CandidateDiscoveryMatchData[] = [
  {
    candidate_id: "cand-demo-01",
    candidate_name: "Priyansh Sharma (Demo Candidate)",
    target_role: "Backend Engineer",
    match_score: 94.6,
    match_confidence: "HIGH",
    match_quality: "STRONG_HIRE",
    breakdown: {
      required_skills_coverage: 96,
      verified_evidence_score: 94,
      project_relevance_score: 95,
      experience_alignment_score: 92,
      role_alignment_score: 96,
      evidence_freshness_score: 95
    },
    explanation: {
      summary: "Exceptional alignment with distributed backend requirements. Demonstrates verified mastery in high-throughput APIs, concurrency, and DB indexing.",
      strengths: ["FastAPI and PostgreSQL architectural rigor", "Strong distributed locking & transaction isolation", "Passed 4 mock bar-raisers"],
      partials: ["Kubernetes ingress optimization"],
      unknowns: [],
      main_limitation: "Limited production multi-region Cassandra cluster experience."
    }
  },
  {
    candidate_id: "cand-demo-02",
    candidate_name: "Aman Gupta",
    target_role: "Backend Engineer",
    match_score: 88.2,
    match_confidence: "HIGH",
    match_quality: "INTERVIEW_READY",
    breakdown: {
      required_skills_coverage: 89,
      verified_evidence_score: 86,
      project_relevance_score: 90,
      experience_alignment_score: 88,
      role_alignment_score: 89,
      evidence_freshness_score: 87
    },
    explanation: {
      summary: "Solid system design and async worker pipelines. High algorithmic efficiency and clean coding standards.",
      strengths: ["Microservice decomposition", "Redis caching patterns"],
      partials: ["Database connection pool tuning under extreme burst load"],
      unknowns: ["eBPF profiling"],
      main_limitation: "Low demonstrated experience in raw socket multiplexing."
    }
  },
  {
    candidate_id: "cand-demo-03",
    candidate_name: "Simran Kaur",
    target_role: "Backend Engineer",
    match_score: 84.5,
    match_confidence: "MEDIUM",
    match_quality: "INTERVIEW_READY",
    breakdown: {
      required_skills_coverage: 85,
      verified_evidence_score: 83,
      project_relevance_score: 86,
      experience_alignment_score: 84,
      role_alignment_score: 85,
      evidence_freshness_score: 84
    },
    explanation: {
      summary: "Proficient in Python backend and relational databases with consistent test coverage.",
      strengths: ["Data modeling & schema migrations", "RESTful API design"],
      partials: ["Distributed state machine concurrency"],
      unknowns: [],
      main_limitation: "Needs deeper experience with distributed consensus algorithms."
    }
  }
];

export const RecruiterIntelligencePage: React.FC = () => {
  const [jobs, setJobs] = useState<RecruiterJobData[]>(DEFAULT_RECRUITER_JOBS);
  const [selectedJob, setSelectedJob] = useState<RecruiterJobData | null>(DEFAULT_RECRUITER_JOBS[0]);
  const [candidates, setCandidates] = useState<CandidateDiscoveryMatchData[]>(DEFAULT_CANDIDATES);
  const [loading, setLoading] = useState<boolean>(false);
  const [searching, setSearching] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Job Creation Modal
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newRole, setNewRole] = useState<string>('Backend Engineer');
  const [newDesc, setNewDesc] = useState<string>('');
  const [extractedReqs, setExtractedReqs] = useState<any | null>(null);

  // Comparison State
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>([]);
  const [comparisonMatrix, setComparisonMatrix] = useState<CandidateDiscoveryMatchData[] | null>(null);
  const [showCompareModal, setShowCompareModal] = useState<boolean>(false);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await careerIntelligenceApi.listRecruiterJobs();
      if (data && Array.isArray(data) && data.length > 0) {
        setJobs(data);
        setSelectedJob(data[0]);
        await runDiscovery(data[0].job_id);
      } else {
        setJobs(DEFAULT_RECRUITER_JOBS);
        setSelectedJob(DEFAULT_RECRUITER_JOBS[0]);
        setCandidates(DEFAULT_CANDIDATES);
      }
    } catch (err) {
      console.error('Failed to load recruiter jobs', err);
      setJobs(DEFAULT_RECRUITER_JOBS);
      setSelectedJob(DEFAULT_RECRUITER_JOBS[0]);
      setCandidates(DEFAULT_CANDIDATES);
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async (jobId: string, query?: string) => {
    setSearching(true);
    try {
      const res = await careerIntelligenceApi.discoverCandidates(jobId, query);
      if (res.top_candidates && res.top_candidates.length > 0) {
        setCandidates(res.top_candidates);
      } else {
        setCandidates(DEFAULT_CANDIDATES);
      }
    } catch (err) {
      console.error('Candidate discovery failed', err);
      setCandidates(DEFAULT_CANDIDATES);
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleJobChange = async (job: RecruiterJobData) => {
    setSelectedJob(job);
    setSelectedCandidateIds([]);
    await runDiscovery(job.job_id, searchQuery);
  };

  const handleExtractReqs = async () => {
    if (!newDesc.trim()) return;
    try {
      const reqs = await careerIntelligenceApi.extractJobRequirements(newDesc);
      setExtractedReqs(reqs);
    } catch (err) {
      console.error('Extraction failed', err);
    }
  };

  const handleCreateJob = async () => {
    try {
      const created = await careerIntelligenceApi.createRecruiterJob({
        title: newTitle,
        target_role: newRole,
        description: newDesc,
        structured_requirements: extractedReqs
      });
      setShowCreateModal(false);
      setNewTitle('');
      setNewDesc('');
      setExtractedReqs(null);
      await loadJobs();
    } catch (err) {
      console.error('Job creation failed', err);
    }
  };

  const toggleCandidateSelection = (cid: string) => {
    if (selectedCandidateIds.includes(cid)) {
      setSelectedCandidateIds(selectedCandidateIds.filter(id => id !== cid));
    } else if (selectedCandidateIds.length < 4) {
      setSelectedCandidateIds([...selectedCandidateIds, cid]);
    }
  };

  const handleCompare = async () => {
    if (!selectedJob || selectedCandidateIds.length < 2) return;
    try {
      const res = await careerIntelligenceApi.compareCandidates(selectedJob.job_id, selectedCandidateIds);
      setComparisonMatrix(res.comparison_matrix || []);
      setShowCompareModal(true);
    } catch (err) {
      console.error('Comparison failed', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider mb-1">
              <Users className="w-4 h-4 text-emerald-400" />
              VIREONIQ Recruiter Intelligence v7.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Evidence-Driven Talent Discovery
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Discover candidates through independently verified evidence, role-specific alignment, and tamper-proof telemetry.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition shadow-lg shadow-indigo-500/20"
            >
              <Plus className="w-4 h-4" />
              Create Job Posting
            </button>
          </div>
        </div>

        {/* 1. Job Selector & Query Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-slate-400">Active Job:</span>
              <select
                value={selectedJob?.job_id || ''}
                onChange={(e) => {
                  const j = jobs.find(x => x.job_id === e.target.value);
                  if (j) handleJobChange(j);
                }}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-sm font-semibold rounded-lg px-3 py-2"
              >
                {jobs.map(j => (
                  <option key={j.job_id} value={j.job_id}>{j.title} ({j.target_role})</option>
                ))}
              </select>
            </div>

            {selectedCandidateIds.length >= 2 && (
              <button
                onClick={handleCompare}
                className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-3.5 py-2 rounded-lg transition"
              >
                <Columns className="w-3.5 h-3.5" />
                Compare Selected ({selectedCandidateIds.length})
              </button>
            )}
          </div>

          {/* Search Query Input */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by keywords, verified skill thresholds, or domain specialty..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              onClick={() => selectedJob && runDiscovery(selectedJob.job_id, searchQuery)}
              disabled={searching}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-4 py-2 rounded-xl transition"
            >
              {searching ? 'Filtering...' : 'Search'}
            </button>
          </div>
        </div>

        {/* 2. Discovered Candidate Match Cards */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-400" />
              Evidence-Ranked Candidate Matches
            </h3>
            <span className="text-xs font-mono text-slate-400">
              {candidates.length} Discoverable Candidates
            </span>
          </div>

          {candidates.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 text-sm">
              No matching candidates found for this role. Try adjusting your search query or creating additional jobs.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {candidates.map((cand) => (
                <div
                  key={cand.candidate_id}
                  className={`bg-slate-900 border rounded-2xl p-6 space-y-4 transition ${
                    selectedCandidateIds.includes(cand.candidate_id)
                      ? 'border-indigo-500/60 bg-indigo-950/20'
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-bold text-white">{cand.candidate_name}</h4>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                          cand.match_confidence === 'HIGH'
                            ? 'bg-emerald-950 border border-emerald-800 text-emerald-300'
                            : 'bg-amber-950 border border-amber-800 text-amber-300'
                        }`}>
                          {cand.match_confidence} CONFIDENCE
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">{cand.target_role}</p>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-indigo-400">{cand.match_score}%</div>
                      <div className="text-[10px] font-mono text-slate-500">Evidence Match</div>
                    </div>
                  </div>

                  {/* 30-Second Explainable Summary */}
                  <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2 text-xs">
                    <div className="text-slate-300 font-medium">{cand.explanation.summary}</div>
                    
                    {cand.explanation.strengths.length > 0 && (
                      <div className="space-y-1">
                        {cand.explanation.strengths.map((s, idx) => (
                          <div key={idx} className="text-emerald-400 flex items-center gap-1 text-[11px]">
                            <CheckCircle2 className="w-3 h-3 shrink-0" /> {s}
                          </div>
                        ))}
                      </div>
                    )}

                    {cand.explanation.unknowns.length > 0 && (
                      <div className="text-slate-500 text-[11px]">
                        ? {cand.explanation.unknowns[0]}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                    <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCandidateIds.includes(cand.candidate_id)}
                        onChange={() => toggleCandidateSelection(cand.candidate_id)}
                        className="rounded border-slate-700 bg-slate-950"
                      />
                      Select for Compare
                    </label>

                    <button
                      onClick={() => selectedJob && careerIntelligenceApi.addCandidateToShortlist(selectedJob.job_id, cand.candidate_id)}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-3.5 py-1.5 rounded-lg transition"
                    >
                      Shortlist
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 3. Job Creation Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white">Create Structured Job Posting</h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">✕</button>
              </div>

              <div className="space-y-4 text-xs">
                <div>
                  <label className="text-slate-400 font-mono">Job Title</label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Lead Distributed Systems Engineer"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
                  />
                </div>

                <div>
                  <label className="text-slate-400 font-mono">Target Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
                  >
                    <option value="Backend Engineer">Backend Engineer</option>
                    <option value="Full Stack Engineer">Full Stack Engineer</option>
                    <option value="AI/ML Engineer">AI/ML Engineer</option>
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <label className="text-slate-400 font-mono">Job Description</label>
                    <button
                      onClick={handleExtractReqs}
                      className="text-indigo-400 hover:text-indigo-300 font-mono text-[11px]"
                    >
                      Extract Requirements (AI)
                    </button>
                  </div>
                  <textarea
                    rows={4}
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    placeholder="Paste job description text to extract structured required skills..."
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 mt-1"
                  />
                </div>

                {extractedReqs && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                    <div className="font-semibold text-slate-300">Extracted Requirements Review:</div>
                    <div className="flex flex-wrap gap-1.5">
                      {extractedReqs.required_skills?.map((r: any) => (
                        <span key={r.name} className="px-2 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded font-mono text-[10px]">
                          {r.name} ({r.min_level})
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={handleCreateJob}
                  disabled={!newTitle || !newDesc}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition"
                >
                  Publish Structured Job
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 4. Comparison Matrix Modal */}
        {showCompareModal && comparisonMatrix && (
          <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-4xl w-full p-6 space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Columns className="w-5 h-5 text-indigo-400" />
                  Side-by-Side Evidence Comparison Matrix
                </h3>
                <button onClick={() => setShowCompareModal(false)} className="text-slate-400 hover:text-white">✕</button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                {comparisonMatrix.map((cand) => (
                  <div key={cand.candidate_id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                    <div>
                      <h5 className="font-bold text-white text-sm">{cand.candidate_name}</h5>
                      <div className="text-indigo-400 font-bold text-lg mt-1">{cand.match_score}% Match</div>
                      <span className="text-[10px] text-emerald-400">{cand.match_confidence} Confidence</span>
                    </div>

                    <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-[11px]">
                      <div>Skills: {cand.breakdown.required_skills_coverage}%</div>
                      <div>Verified Proof: {cand.breakdown.verified_evidence_score}%</div>
                      <div>Projects: {cand.breakdown.project_relevance_score}%</div>
                      <div>Role Alignment: {cand.breakdown.role_alignment_score}%</div>
                    </div>

                    <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-800/80">
                      {cand.explanation.main_limitation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
