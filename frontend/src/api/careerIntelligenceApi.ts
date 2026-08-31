import client from "./client";

export interface SkillEvidenceItem {
  skill_name: string;
  evidence_tier: "CLAIMED" | "INFERRED" | "DEMONSTRATED" | "ASSESSED" | "VERIFIED";
  weight: number;
  score: number;
  confidence: "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH";
  freshness_score: number;
  evidence_count: number;
  explanation: string;
  source_provenance?: any;
  proficiency_level?: number;
  proficiency_label?: string;
  conflict_report?: any;
  relationships?: any[];
}

export interface DimensionContributionItem {
  dimension: string;
  label: string;
  score: number;
  weight: number;
  contribution_points: number;
  percentage_of_total: number;
  evidence: string[];
}

export interface CareerReadinessV3 {
  target_role: string;
  overall_readiness_score: number;
  readiness_band: "NOT_READY" | "DEVELOPING" | "INTERVIEW_READY" | "STRONG_HIRE";
  confidence: "LOW" | "MEDIUM" | "HIGH";
  explanation: {
    summary: string;
    strongest_areas: Array<{ skill: string; score: number }>;
    moderate_areas: Array<{ skill: string; score: number }>;
    limiting_constraint: string;
  };
  dimension_contributions: Record<string, DimensionContributionItem>;
  metadata: {
    readiness_model_version: string;
    role_version: string;
    calculated_at: string;
    evidence_count: number;
  };
}

export interface BottleneckItem {
  skill_name: string;
  role_importance: number;
  expected_level: number;
  candidate_level: number | null;
  evidence_tier: string;
  deficit_severity: number;
  bottleneck_score: number;
  is_unknown: boolean;
  diagnosis: string;
}

export interface CareerBottleneckReport {
  target_role: string;
  has_bottleneck: boolean;
  primary_bottleneck: BottleneckItem | null;
  secondary_constraints: BottleneckItem[];
  all_constraints_ranked: BottleneckItem[];
  bottleneck_summary: string;
}

export interface NextBestActionItem {
  action_id: string;
  title: string;
  action_type: "BUILD" | "ASSESS" | "PRACTICE" | "LEARN" | "INTERVIEW" | "IMPROVE RESUME" | "VERIFY";
  primary_gap: string;
  multi_gap_closure_count: number;
  addressed_gaps: Array<{ skill_name: string; classification: string; importance: number }>;
  estimated_effort_hours: string;
  evidence_value_tier: string;
  difficulty: string;
  roi_score: number;
  prerequisites: {
    has_unmet_prerequisites: boolean;
    unmet_prerequisites: string[];
  };
  preview: {
    current_readiness: number;
    projected_readiness_range: string;
    projected_delta: string;
    confidence: string;
  };
  why_this_action: string;
  deliverable: string;
}

export interface NextBestActionsResponse {
  target_role: string;
  current_readiness: number;
  total_actions_evaluated: number;
  highest_roi_action: NextBestActionItem | null;
  ranked_interventions: NextBestActionItem[];
}

export interface AssessmentQuestionData {
  question_id: string;
  competency: string;
  difficulty: string;
  question_type: string;
  prompt: string;
  starter_code?: string;
  has_hidden_tests: boolean;
  current_session_difficulty: string;
  status?: string;
  message?: string;
}

export interface AssessmentResultData {
  session_id: string;
  target_role: string;
  mode: string;
  overall_score: number;
  evidence_created_count: number;
  evidence_items: Array<{ skill_name: string; tier: string; score: number }>;
  recalculated_career_readiness: number;
  readiness_delta_explanation: string;
  highest_roi_next_action?: NextBestActionItem;
}

export interface InterventionTaskData {
  id: string;
  day_number: number;
  title: string;
  description: string;
  task_type: string;
  estimated_minutes: number;
  expected_evidence_type: string;
  completion_criteria: string;
  status?: string;
}

export interface InterventionPlanData {
  plan_id: string;
  target_role: string;
  title: string;
  objective: string;
  primary_gap: string;
  secondary_gaps: string[];
  strategy: string;
  duration_days: number;
  daily_time_budget_minutes: number;
  expected_readiness_delta_range: string;
  status: string;
  progress_pct: number;
  tasks_count?: number;
  tasks: InterventionTaskData[];
}

export interface MissionTaskStep {
  phase: string;
  detail: string;
}

export interface MissionTaskHow {
  steps: MissionTaskStep[];
  optimal_approach: string;
  code_blueprint?: string;
  common_pitfalls: string[];
}

export interface MissionTaskWhere {
  platform: string;
  url?: string;
  mnc_companies: string[];
  recommended_tools: string;
}

export interface MissionTaskWhen {
  recommended_time: string;
  duration_minutes: number;
  sprint_phase: string;
}

export interface MissionTaskProof {
  deliverable: string;
  verification_method: string;
}

export interface DailyMissionTask {
  task_id: string;
  title: string;
  task_type: string;
  estimated_minutes: number;
  projected_delta: string;
  status: string;
  why: string;
  difficulty?: string;
  how?: MissionTaskHow;
  where?: MissionTaskWhere;
  when?: MissionTaskWhen;
  proof_criteria?: MissionTaskProof;
}

export interface DailyMissionData {
  mission_date: string;
  target_role: string;
  active_plan_title: string;
  tasks_count: number;
  total_estimated_minutes: number;
  progress_pct: number;
  tasks: DailyMissionTask[];
  rationale: string;
}

export interface WeeklyCareerReviewData {
  week_start_date: string;
  target_role: string;
  starting_readiness: number;
  ending_readiness: number;
  readiness_delta: number;
  evidence_count_added: number;
  gaps_closed: string[];
  remaining_constraints: string[];
  attribution: Record<string, string>;
  next_week_priority: string;
}

// Phase 6 Talent Passport & Verified Credentials
export interface VerifiedCompetencyItem {
  competency: string;
  level: string;
  credential_type: string;
  issuer: string;
  public_reference: string;
  freshness_state: string;
  issued_at: string;
  provenance_drilldown: {
    evidence_tier: string;
    assessment_score: number;
    integrity_indicator: string;
    verification_link: string;
  };
}

export interface TalentPassportData {
  passport_version: string;
  is_public_view: boolean;
  target_role: string;
  candidate: {
    name: string;
    headline: string;
    trust_indicator: string;
    trust_rationale: string;
  };
  verified_competencies: VerifiedCompetencyItem[];
  demonstrated_projects: Array<{
    id: string;
    project_name: string;
    complexity_score: number;
    technologies: string[];
    verification_status: string;
    role_relevance: string;
  }>;
  role_alignment: {
    alignment_percentage: number;
    matched_skills: string[];
    summary: string;
  };
  verification_registry: string;
  last_updated: string;
  active_share_links?: Array<{
    share_token: string;
    share_url: string;
    target_role: string;
    created_at: string;
    view_count: number;
  }>;
}

export interface PublicVerificationResult {
  valid: boolean;
  status?: string;
  message?: string;
  credential?: {
    public_reference: string;
    competency: string;
    level: string;
    credential_type: string;
    issuer: string;
    status: string;
    freshness_state: string;
    issued_at: string;
    verified_at: string;
    evidence_proof: string;
  };
  verification?: {
    signature_status: string;
    checked_at: string;
    issuer_registry: string;
  };
}

// Phase 7 Recruiter Intelligence & Candidate Matching
export interface RecruiterJobData {
  job_id: string;
  title: string;
  target_role: string;
  status: string;
  structured_requirements: {
    required_skills?: Array<{ name: string; importance: number; min_level: string; confidence?: string }>;
    preferred_skills?: Array<{ name: string; importance: number; min_level: string }>;
  };
  hard_requirements?: string[];
  created_at: string;
}

export interface CandidateDiscoveryMatchData {
  candidate_id: string;
  candidate_name: string;
  target_role: string;
  match_score: number;
  match_confidence: "HIGH" | "MEDIUM" | "LOW";
  match_quality: string;
  breakdown: {
    required_skills_coverage: number;
    verified_evidence_score: number;
    project_relevance_score: number;
    experience_alignment_score: number;
    role_alignment_score: number;
    evidence_freshness_score: number;
  };
  explanation: {
    summary: string;
    strengths: string[];
    partials: string[];
    unknowns: string[];
    main_limitation: string;
    reason_codes?: string[];
  };
}

// Phase 8 Employer & Workforce Skills Intelligence
export interface WorkforceCompetencyItem {
  competency: string;
  coverage_pct: number;
  importance: number;
  criticality: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  gap_status: string;
  shortage_type: string;
  practitioners: number;
  expert_count: number;
}

export interface WorkforceCriticalGapItem {
  competency: string;
  coverage_pct: number;
  criticality: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  gap_status: string;
  shortage_type: string;
  practitioners: number;
  diagnosis: string;
}

export interface WorkforceConcentrationRiskItem {
  competency: string;
  expert_count: number;
  team_size: number;
  risk_level: "HIGH" | "CRITICAL";
  diagnosis: string;
}

export interface OrganizationCapabilitiesData {
  organization_twin_version: string;
  team_size: number;
  overall_coverage_pct: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  evidence_coverage_pct: number;
  critical_gaps_count: number;
  concentration_risks_count: number;
  primary_bottleneck: string;
  critical_gaps: WorkforceCriticalGapItem[];
  concentration_risks: WorkforceConcentrationRiskItem[];
  competencies: WorkforceCompetencyItem[];
  calculated_at: string;
}

// Phase 9 Career Simulator & Counterfactual Planning
export interface CareerScenarioData {
  simulation_id: string;
  title: string;
  target_role: string;
  simulation_type: string;
  adjacency_proximity_pct?: number;
  projected_readiness: {
    current_score: number;
    projected_range: [number, number];
    projected_base: number;
    best_case: number;
    base_case: number;
    conservative_case: number;
    confidence: "HIGH" | "MEDIUM" | "LOW";
  };
  projected_skills?: Record<string, { current_score: number; projected_score: number; delta: number }>;
  projected_gaps?: {
    transferable_skills: Array<{ skill_name: string; transfer_tier: string; current_tier: string; current_score: number }>;
    critical_gaps: Array<{ skill_name: string; status: string; importance: number }>;
    closed_gaps: string[];
  };
  timeline_estimate?: {
    estimated_effort_hours: string;
    estimated_duration_days: number;
    feasibility: string;
  };
  sensitivity_analysis?: {
    critical_driver: string;
    sensitivity_level: string;
    driver_explanation: string;
  };
  hypothetical_evidence?: any[];
  created_at: string;
}

// Phase 10 AI Fabric & Observability
export interface CopilotChatResponse {
  role_mode: "CANDIDATE" | "RECRUITER" | "EMPLOYER";
  status: "SUCCESS" | "DENIED" | "ERROR";
  answer: string;
  target_role?: string;
  confidence?: "HIGH" | "MEDIUM" | "LOW";
  structured_response?: {
    facts: string[];
    inferences: string[];
    recommendations: string[];
    projections: string[];
  };
  provenance_sources?: string[];
  tool_trace?: Array<{ tool_name: string; status: string; latency_ms: number }>;
}

export interface AIObservabilityData {
  total_ai_requests: number;
  total_estimated_cost_usd: number;
  average_latency_ms: number;
  success_rate_pct: number;
  active_models: string[];
  orchestrator_status: string;
}

export const careerIntelligenceApi = {
  // Phase 10 AI Fabric & Copilot
  sendCopilotMessage: async (
    message: string,
    roleMode: "CANDIDATE" | "RECRUITER" | "EMPLOYER" = "CANDIDATE",
    targetRole?: string
  ): Promise<CopilotChatResponse> => {
    const res = await client.post("/ai/copilot/chat", {
      message,
      role_mode: roleMode,
      target_role: targetRole
    });
    return res.data;
  },

  getAIObservabilityMetrics: async (): Promise<AIObservabilityData> => {
    const res = await client.get("/ai/observability");
    return res.data;
  },

  runAIEvaluationSuite: async () => {
    const res = await client.get("/ai/evaluations/run");
    return res.data;
  },

  // Phase 9 Career Simulator
  runCareerScenario: async (scenarioData: {
    target_role: string;
    simulation_type?: string;
    scenario_actions?: Array<{ skill_name: string; action_type: string; target_score: number }>;
    assumptions?: any;
    title?: string;
  }): Promise<CareerScenarioData> => {
    const res = await client.post("/career-simulator/scenarios", scenarioData);
    return res.data;
  },

  listCareerScenarios: async (): Promise<CareerScenarioData[]> => {
    const res = await client.get("/career-simulator/scenarios");
    return res.data;
  },

  getCareerScenario: async (simulationId: string): Promise<CareerScenarioData> => {
    const res = await client.get(`/career-simulator/scenarios/${simulationId}`);
    return res.data;
  },

  compareCareerPaths: async (targetRoles: string[]) => {
    const res = await client.post("/career-simulator/compare-paths", { target_roles: targetRoles });
    return res.data;
  },

  convertScenarioToPlan: async (simulationId: string) => {
    const res = await client.post(`/career-simulator/scenarios/${simulationId}/convert-to-plan`);
    return res.data;
  },

  deleteCareerScenario: async (simulationId: string) => {
    const res = await client.delete(`/career-simulator/scenarios/${simulationId}`);
    return res.data;
  },

  // Phase 8 Workforce Intelligence
  getOrganizationCapabilities: async (unitId?: string): Promise<OrganizationCapabilitiesData> => {
    const params = unitId ? { unit_id: unitId } : {};
    const res = await client.get("/org/capabilities", { params });
    return res.data;
  },

  getWorkforceCapabilityMatrix: async () => {
    const res = await client.get("/org/matrix");
    return res.data;
  },

  getHiringVsUpskillingTradeoffs: async (competency: string, unitId?: string) => {
    const params = unitId ? { unit_id: unitId } : {};
    const res = await client.get(`/org/gaps/${competency}/tradeoffs`, { params });
    return res.data;
  },

  getInternalTalentMobility: async (targetRole: string = "Platform Engineer") => {
    const res = await client.get("/org/mobility", { params: { target_role: targetRole } });
    return res.data;
  },

  simulateWorkforceChange: async (unitId: string | null, hypotheticalChanges: any) => {
    const res = await client.post("/org/simulate", {
      unit_id: unitId,
      hypothetical_changes: hypotheticalChanges
    });
    return res.data;
  },

  takeOrganizationSnapshot: async (unitId?: string) => {
    const res = await client.post("/org/snapshots", { unit_id: unitId });
    return res.data;
  },

  listOrganizationSnapshots: async () => {
    const res = await client.get("/org/snapshots");
    return res.data;
  },

  createAssessmentCampaign: async (campaignData: {
    title: string;
    competency: string;
    target_role?: string;
    unit_id?: string;
    invited_count?: number;
  }) => {
    const res = await client.post("/org/campaigns", campaignData);
    return res.data;
  },

  listOrganizationRoles: async () => {
    const res = await client.get("/org/roles");
    return res.data;
  },

  createOrganizationRole: async (roleData: any) => {
    const res = await client.post("/org/roles", roleData);
    return res.data;
  },

  // Phase 7 Recruiter Intelligence
  listRecruiterJobs: async (): Promise<RecruiterJobData[]> => {
    const res = await client.get("/recruiter-intel/jobs");
    return res.data;
  },

  createRecruiterJob: async (jobData: {
    title: string;
    target_role: string;
    description: string;
    structured_requirements?: any;
    hard_requirements?: string[];
  }): Promise<RecruiterJobData> => {
    const res = await client.post("/recruiter-intel/jobs", jobData);
    return res.data;
  },

  extractJobRequirements: async (jobDescription: string) => {
    const res = await client.post("/recruiter-intel/jobs/extract-requirements", {
      job_description: jobDescription
    });
    return res.data;
  },

  discoverCandidates: async (jobId: string, query?: string, filters?: any): Promise<{
    job_id: string;
    job_title: string;
    total_candidates_evaluated: number;
    total_matches_returned: number;
    top_candidates: CandidateDiscoveryMatchData[];
  }> => {
    const res = await client.post("/recruiter-intel/discover", {
      job_id: jobId,
      query,
      filters
    });
    return res.data;
  },

  compareCandidates: async (jobId: string, candidateIds: string[]) => {
    const res = await client.post("/recruiter-intel/compare", {
      job_id: jobId,
      candidate_ids: candidateIds
    });
    return res.data;
  },

  getShortlistForJob: async (jobId: string) => {
    const res = await client.get(`/recruiter-intel/shortlists/${jobId}`);
    return res.data;
  },

  addCandidateToShortlist: async (jobId: string, candidateId: string, stage: string = "SHORTLISTED") => {
    const res = await client.post("/recruiter-intel/shortlists", {
      job_id: jobId,
      candidate_id: candidateId,
      stage
    });
    return res.data;
  },

  addPrivateRecruiterNote: async (shortlistId: string, noteText: string) => {
    const res = await client.post(`/recruiter-intel/shortlists/${shortlistId}/notes`, {
      note_text: noteText
    });
    return res.data;
  },

  // Phase 6 Talent Passport & Verified Credentials
  getTalentPassport: async (targetRole: string = "Backend Engineer"): Promise<TalentPassportData> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/passport", { params });
    return res.data;
  },

  createPassportShareLink: async (targetRole: string = "Backend Engineer", visibleCompetencies?: string[], expiresInDays: number = 30) => {
    const res = await client.post("/passport/share", {
      target_role: targetRole,
      visible_competencies: visibleCompetencies,
      expires_in_days: expiresInDays
    });
    return res.data;
  },

  revokePassportShareLink: async (shareToken: string) => {
    const res = await client.post("/passport/revoke-share", { share_token: shareToken });
    return res.data;
  },

  getPublicPassport: async (shareToken: string): Promise<TalentPassportData> => {
    const res = await client.get(`/passport/public/${shareToken}`);
    return res.data;
  },

  listCandidateCredentials: async () => {
    const res = await client.get("/credentials");
    return res.data;
  },

  issueCredential: async (competency: string) => {
    const res = await client.post("/credentials/issue", { competency });
    return res.data;
  },

  revokeCredential: async (credentialId: string, reason?: string) => {
    const res = await client.post(`/credentials/${credentialId}/revoke`, { reason });
    return res.data;
  },

  verifyPublicCredential: async (publicReference: string): Promise<PublicVerificationResult> => {
    const res = await client.get(`/credentials/verify/${publicReference}`);
    return res.data;
  },

  // Phase 5 Career OS & Interventions
  generateInterventionPlan: async (targetRole: string = "Backend Engineer", strategy: string = "BALANCED", dailyTimeBudgetMinutes: number = 60, focusSkill?: string): Promise<InterventionPlanData> => {
    const res = await client.post("/interventions/generate", {
      target_role: targetRole,
      strategy,
      daily_time_budget_minutes: dailyTimeBudgetMinutes,
      focus_skill: focusSkill
    });
    return res.data;
  },

  getActiveInterventionPlan: async (): Promise<InterventionPlanData | null> => {
    const res = await client.get("/interventions/active");
    return res.data;
  },

  getDailyMission: async (targetRole?: string): Promise<DailyMissionData> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/interventions/daily-mission", { params });
    return res.data;
  },

  getDailyCareerMission: async (targetRole?: string, refresh: boolean = false, cycle: number = 0): Promise<DailyMissionData> => {
    const params: Record<string, any> = {};
    if (targetRole) params.target_role = targetRole;
    if (refresh) params.refresh = true;
    if (cycle) params.cycle = cycle;
    const res = await client.get("/interventions/daily-mission", { params });
    return res.data;
  },

  completeInterventionTask: async (taskId: string) => {
    const res = await client.post(`/interventions/tasks/${taskId}/complete`);
    return res.data;
  },

  replanIntervention: async (planId: string, triggerReason?: string) => {
    const res = await client.post(`/interventions/${planId}/replan`, {
      trigger_reason: triggerReason || "ASSESSMENT_PREREQUISITE_IDENTIFIED"
    });
    return res.data;
  },

  logRecommendationFeedback: async (feedbackType: string, interventionId?: string, actionId?: string, comment?: string) => {
    const res = await client.post("/interventions/feedback", {
      feedback_type: feedbackType,
      intervention_id: interventionId,
      action_id: actionId,
      comment
    });
    return res.data;
  },

  getWeeklyCareerReview: async (targetRole?: string): Promise<WeeklyCareerReviewData> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/interventions/weekly-review", { params });
    return res.data;
  },

  // Phase 4 Assessment Engine
  startAssessmentSession: async (targetRole: string = "Backend Engineer", mode: "ASSESSMENT" | "PRACTICE" = "ASSESSMENT") => {
    const res = await client.post("/assessments/start", { target_role: targetRole, mode });
    return res.data;
  },

  getNextAssessmentQuestion: async (sessionId: string): Promise<AssessmentQuestionData> => {
    const res = await client.get(`/assessments/${sessionId}/next-question`);
    return res.data;
  },

  submitAssessmentResponse: async (sessionId: string, questionId: string, responseData: {
    response_text?: string;
    code_submission?: string;
    duration_seconds?: number;
    paste_count?: number;
    paste_chars?: number;
  }) => {
    const res = await client.post(`/assessments/${sessionId}/respond`, {
      question_id: questionId,
      ...responseData
    });
    return res.data;
  },

  completeAssessmentSession: async (sessionId: string): Promise<AssessmentResultData> => {
    const res = await client.post(`/assessments/${sessionId}/complete`);
    return res.data;
  },

  getAssessmentHistory: async () => {
    const res = await client.get("/assessments/history");
    return res.data;
  },

  // Canonical CRI 2.0 (v3.0.0)
  getCareerReadinessV3: async (targetRole?: string): Promise<CareerReadinessV3> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/readiness", { params });
    return res.data;
  },

  getCareerBottlenecks: async (targetRole?: string): Promise<CareerBottleneckReport> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/readiness/bottlenecks", { params });
    return res.data;
  },

  getNextBestCareerActions: async (targetRole?: string): Promise<NextBestActionsResponse> => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/roi-gaps/next-best-actions", { params });
    return res.data;
  },

  recordRecommendationDecision: async (actionId: string, decision: "ACCEPT" | "REJECT" | "POSTPONE", reason?: string) => {
    const res = await client.post("/roi-gaps/recommendations/action", {
      action_id: actionId,
      decision,
      reason
    });
    return res.data;
  },

  runZeroMutationSimulation: async (hypotheticalEvidence: any[], targetRole?: string) => {
    const res = await client.post("/career-simulator/simulate", {
      hypothetical_evidence: hypotheticalEvidence,
      target_role: targetRole
    });
    return res.data;
  },

  getCareerDigitalTwin: async (targetRole?: string) => {
    const params = targetRole ? { target_role: targetRole } : {};
    const res = await client.get("/career-twin", { params });
    return res.data;
  },

  getTwinSkillsWithGraph: async () => {
    const res = await client.get("/career-twin/skills");
    return res.data;
  },

  getTwinEvidence: async (skillName?: string) => {
    const params = skillName ? { skill_name: skillName } : {};
    const res = await client.get("/career-twin/evidence", { params });
    if (res.data && Array.isArray(res.data.evidence_items)) {
      return res.data.evidence_items;
    }
    if (Array.isArray(res.data)) {
      return res.data;
    }
    return [];
  },

  getTwinTrajectory: async () => {
    const res = await client.get("/career-twin/trajectory");
    return res.data;
  },

  getCareerGoals: async () => {
    const res = await client.get("/career-goals");
    return res.data;
  },

  saveCareerGoal: async (goalData: any) => {
    const res = await client.post("/career-goals", goalData);
    return res.data;
  },

  switchTargetRole: async (targetRole: string) => {
    const res = await client.post("/career-goals/target-role", { target_role: targetRole });
    return res.data;
  },

  compareRoles: async (roleA: string, roleB: string) => {
    const res = await client.get("/roles-intelligence/compare", { params: { role_a: roleA, role_b: roleB } });
    return res.data;
  },

  // Phase 11 Privacy & Security Governance
  getPrivacyPreferences: async () => {
    const res = await client.get("/privacy-security/preferences");
    return res.data;
  },

  updatePrivacyPreferences: async (updates: {
    allow_recruiter_discovery?: boolean;
    allow_public_passport?: boolean;
    allow_assessment_sharing?: boolean;
  }) => {
    const res = await client.put("/privacy-security/preferences", { updates });
    return res.data;
  },

  exportUserData: async () => {
    const res = await client.get("/privacy-security/export");
    return res.data;
  },

  deleteAccount: async () => {
    const res = await client.post("/privacy-security/account/delete");
    return res.data;
  },

  getSecurityAuditLogs: async (limit: number = 20) => {
    const res = await client.get("/privacy-security/audit-logs", { params: { limit } });
    return res.data;
  },

  getFairnessAuditReport: async () => {
    const res = await client.get("/privacy-security/fairness-audit");
    return res.data;
  },

  // Phase 12 Outcome Intelligence
  getCareerValueFunnel: async () => {
    const res = await client.get("/outcomes/funnel");
    return res.data;
  },

  getCandidateProgressOutcomes: async (targetRole: string = "Backend Engineer") => {
    const res = await client.get("/outcomes/candidate/progress", { params: { target_role: targetRole } });
    return res.data;
  },

  getExecutiveInsights: async () => {
    const res = await client.get("/outcomes/executive-insights");
    return res.data;
  },

  logAnalyticsEvent: async (eventType: string, resourceId?: string, metadata?: any, idempotencyKey?: string) => {
    const res = await client.post("/outcomes/events", {
      event_type: eventType,
      resource_id: resourceId,
      metadata,
      idempotency_key: idempotencyKey
    });
    return res.data;
  },

  // Phase 13 Developer Platform & Ecosystem
  listPlatformApiKeys: async () => {
    const res = await client.get("/platform/api-keys");
    return res.data;
  },

  generatePlatformApiKey: async (name: string, scopes: string[], rateLimit: number = 120) => {
    const res = await client.post("/platform/api-keys", {
      name,
      scopes,
      rate_limit_per_minute: rateLimit
    });
    return res.data;
  },

  revokePlatformApiKey: async (keyId: string) => {
    const res = await client.delete(`/platform/api-keys/${keyId}`);
    return res.data;
  },

  listWebhookSubscriptions: async () => {
    const res = await client.get("/platform/webhooks");
    return res.data;
  },

  createWebhookSubscription: async (targetUrl: string, subscribedEvents: string[]) => {
    const res = await client.post("/platform/webhooks", {
      target_url: targetUrl,
      subscribed_events: subscribedEvents
    });
    return res.data;
  },

  listPartnerConnectors: async () => {
    const res = await client.get("/platform/connectors");
    return res.data;
  },

  getPlatformEntitlements: async () => {
    const res = await client.get("/platform/entitlements");
    return res.data;
  },

  getPlatformHealthTelemetry: async () => {
    const res = await client.get("/platform/health");
    return res.data;
  },

  // Phase 14 Autonomous Career OS
  getDailyCareerBrief: async () => {
    const res = await client.get("/career-os/brief");
    return res.data;
  },

  getCareerSignals: async () => {
    const res = await client.get("/career-os/signals");
    return res.data;
  },

  dismissCareerSignal: async (signalId: string) => {
    const res = await client.post(`/career-os/signals/${signalId}/dismiss`);
    return res.data;
  },

  getCareerGoalsAndDrift: async (primaryGoal: string = "Backend Engineer") => {
    const res = await client.get("/career-os/goals", { params: { primary_goal: primaryGoal } });
    return res.data;
  },

  submitEvidenceDispute: async (evidenceId: string, reason: string) => {
    const res = await client.post("/career-os/disputes", {
      evidence_id: evidenceId,
      reason
    });
    return res.data;
  },

  executeCareerAction: async (actionType: string, isConfirmed: boolean = false) => {
    const res = await client.post("/career-os/actions/execute", {
      action_type: actionType,
      is_confirmed: isConfirmed
    });
    return res.data;
  },

  getAutomationPreferences: async () => {
    const res = await client.get("/career-os/preferences");
    return res.data;
  },

  // Phase 15 Final Convergence & Production Certification
  getCertificationScorecard: async () => {
    const res = await client.get("/certification/scorecard");
    return res.data;
  },

  getModelRegistry: async () => {
    const res = await client.get("/certification/models");
    return res.data;
  },

  run15StageDemo: async (candidateName: string = "Aarav Sharma", targetRole: string = "Senior Backend Engineer") => {
    const res = await client.post("/certification/demo/run", {
      candidate_name: candidateName,
      target_role: targetRole
    });
    return res.data;
  },

  createIntelligenceReceipt: async (payload: any) => {
    const res = await client.post("/certification/receipts", payload);
    return res.data;
  },

  // Post-Phase 15 MNC Interview & Coding Intelligence Engine
  getMNCCompanyProfile: async (companyName: string = "Google", targetLevel: string = "SDE-2", roleFamily: string = "Backend Engineering") => {
    const res = await client.post("/mnc-interview/profiles", {
      company_name: companyName,
      target_level: targetLevel,
      role_family: roleFamily
    });
    return res.data;
  },

  generateQuestionBlueprint: async (role: string, level: string, roundType: string, topic: string, difficulty: string = "MEDIUM") => {
    const res = await client.post("/mnc-interview/blueprint", {
      role,
      level,
      round_type: roundType,
      topic,
      difficulty
    });
    return res.data;
  },

  generateCodingQuestion: async (blueprint: any, language: string = "python") => {
    const res = await client.post("/mnc-interview/coding/generate", {
      blueprint,
      language
    });
    return res.data;
  },

  startMNCInterviewSession: async (targetCompany: string, targetRole: string, targetLevel: string = "SDE-2", mode: string = "ASSESSMENT") => {
    const res = await client.post("/mnc-interview/sessions/start", {
      target_company: targetCompany,
      target_role: targetRole,
      target_level: targetLevel,
      mode
    });
    return res.data;
  },

  submitTurnAnswer: async (sessionId: string, questionText: string, candidateResponse: string, category: string = "SYSTEM_DESIGN", turnNumber: number = 1) => {
    const res = await client.post(`/mnc-interview/sessions/${sessionId}/answer`, {
      question_text: questionText,
      candidate_response: candidateResponse,
      question_category: category,
      turn_number: turnNumber
    });
    return res.data;
  },

  submitCodeEvaluation: async (sessionId: string, questionPayload: any, codeSubmission: string, language: string = "python") => {
    const res = await client.post(`/mnc-interview/sessions/${sessionId}/code/submit`, {
      question_payload: questionPayload,
      code_submission: codeSubmission,
      language
    });
    return res.data;
  },

  finalizeMNCInterviewSession: async (sessionId: string, targetRole: string) => {
    const res = await client.post(`/mnc-interview/sessions/${sessionId}/finalize`, {
      target_role: targetRole
    });
    return res.data;
  },

  // ─── NATIVE INTELLIGENCE CAPABILITIES (ATS, JD Matching & Developer Portfolio) ───
  computeAtsScore: async (cvText: string, skills: string[] = []) => {
    const res = await client.post("/resume/ats-score", {
      cv_text: cvText,
      skills
    });
    return res.data;
  },

  matchJobDescription: async (cvText: string, jobDescription: string, candidateSkills: string[] = []) => {
    const res = await client.post("/resume/jd-match", {
      cv_text: cvText,
      job_description: jobDescription,
      candidate_skills: candidateSkills
    });
    return res.data;
  },

  rewriteResumeSection: async (section: string, content: string, targetRole: string = "Software Engineer") => {
    const res = await client.post("/resume/rewrite", {
      section,
      content,
      target_role: targetRole
    });
    return res.data;
  },

  analyzeDeveloperPortfolio: async (payload: {
    github_url?: string;
    leetcode_user?: string;
    codeforces_user?: string;
    hackerrank_user?: string;
    linkedin_url?: string;
    skills?: string[];
  }) => {
    const res = await client.post("/skills/portfolio-analyze", payload);
    return res.data;
  },

  inferImplicitSkills: async (skills: string[], threshold: number = 0.5) => {
    const res = await client.post("/skills/infer-implicit-skills", {
      skills,
      threshold
    });
    return res.data;
  },

  predictSalary: async (role: string, experienceYears: number, location: string, skills: string[] = []) => {
    const res = await client.post("/market/salary-predict", {
      role,
      experience_years: experienceYears,
      location,
      skills
    });
    return res.data;
  },

  getSkillGapResources: async (skills: string) => {
    const res = await client.get(`/market/skill-gap-resources?skills=${encodeURIComponent(skills)}`);
    return res.data;
  }
};

