import api from '../lib/axios';

export interface DashboardOverview {
  ats_score: number;
  skill_match: number;
  interview_readiness: {
    technical: number;
    communication: number;
    confidence: number;
  };
  applications: {
    total: number;
    active: number;
    offers: number;
  };
  top_gaps: string[];
  ai_therapist_insight?: {
    title: string;
    message: string;
    proof: string;
  };
  culture_fit?: {
    google: number;
    amazon: number;
    meta: number;
    startup?: number;
    dominant_trait: string;
  };
  gps_reroute?: {
    status: string;
    next_best_action: string;
    suggested_pivot?: string;
    reason?: string;
    estimated_time_to_ready?: string;
    blockers?: string[];
  };
  milestones?: {
    title: string;
    status: string;
    priority: string;
  }[];
  market_opportunities?: {
    company: string;
    probability: number;
    critical_missing: string[];
    alignment_reasons?: string[];
    market_velocity?: string;
  }[];
  dna_archetype?: string;
}

export interface CareerGPSWaypoint {
  step_number: number;
  type: "ORIGIN" | "DETOUR" | "INTERMEDIATE" | "DESTINATION";
  title: string;
  eta: string;
  description: string;
  action_item: string;
  status: "COMPLETED" | "ACTIVE" | "UPCOMING";
}

export interface CareerGPSRoute {
  route_id: string;
  name: string;
  badge: string;
  eta_days: number;
  offer_probability: number;
  projected_ctc: string;
  traffic_conditions: string;
  description: string;
  turn_by_turn_waypoints: CareerGPSWaypoint[];
}

export interface CareerGPSTrafficHazard {
  severity: "CRITICAL" | "WARNING" | "CLEAR";
  title: string;
  detail: string;
  detour_recommendation: string;
}

export interface CareerGPSCalculateRequest {
  target_role: string;
  experience_years: string;
  target_tier: string;
  time_horizon_days: number;
  navigation_strategy: string;
}

export interface CareerGPSNavigationData {
  current_telemetry: {
    readiness_score: number;
    estimated_market_value: string;
    target_role: string;
    experience_years: string;
    target_tier: string;
    time_horizon_days: number;
    navigation_strategy: string;
    coordinates: Record<string, number>;
    primary_blocker: string;
  };
  active_route: string;
  available_routes: CareerGPSRoute[];
  traffic_hazards: CareerGPSTrafficHazard[];
  market_opportunities: Array<{
    company: string;
    probability: number;
    critical_missing: string[];
    alignment_reasons?: string[];
    market_velocity?: string;
  }>;
  dna_archetype: string;
}

export const analyticsApi = {
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await api.get('/analytics/overview');
    return response.data;
  },

  calculateCareerGPS: async (payload: CareerGPSCalculateRequest): Promise<CareerGPSNavigationData> => {
    const response = await api.post('/analytics/career-gps/calculate', payload);
    return response.data;
  },
  
  logActivity: async (eventType: string, metadata?: any) => {
    const response = await api.post('/analytics/log', {
      event_type: eventType,
      metadata_json: metadata
    });
    return response.data;
  }
};
