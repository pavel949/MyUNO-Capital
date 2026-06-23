// TypeScript types mirroring the MyUNO Capital REST API (docs/api-reference.md).

// ---------------------------------------------------------------------------
// Shared
// ---------------------------------------------------------------------------

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: { field: string; issue: string }[];
    request_id?: string;
  };
}

// ---------------------------------------------------------------------------
// Auth & Users
// ---------------------------------------------------------------------------

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at?: string;
}

export interface Tenant {
  id: string;
  name: string;
  role: TenantRole;
}

export type TenantRole = "owner" | "collaborator" | "guest";

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterResponse extends AuthTokens {
  user: User;
  tenant: Tenant;
}

export type LoginResponse = AuthTokens;

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  active_tenant_id: string;
  role: TenantRole;
  mfa_enabled: boolean;
}

// ---------------------------------------------------------------------------
// Businesses
// ---------------------------------------------------------------------------

export type BusinessStage =
  | "ideation"
  | "validate"
  | "build"
  | "launch"
  | "grow"
  | "scale"
  | "exitprep"
  | "exit";

export type AutonomyProfile =
  | "ask_me_first"
  | "guided"
  | "autonomous_within_limits";

export interface Business {
  id: string;
  name: string;
  model_template: string;
  description?: string;
  stage: BusinessStage;
  autonomy_profile?: AutonomyProfile;
  created_at: string;
}

export interface CreateBusinessInput {
  name: string;
  model_template: string;
  description?: string;
  autonomy_profile?: AutonomyProfile;
}

// ---------------------------------------------------------------------------
// Goals
// ---------------------------------------------------------------------------

export type GoalStatus = "active" | "achieved" | "archived";

export interface Goal {
  id: string;
  business_id: string;
  title: string;
  metric: string;
  target_value: number;
  target_date: string;
  status: GoalStatus;
  created_at: string;
}

export interface CreateGoalInput {
  title: string;
  target_date: string;
  metric: string;
  target_value: number;
}

// ---------------------------------------------------------------------------
// Agents
// ---------------------------------------------------------------------------

export interface Agent {
  agent: string;
  category: string;
  description: string;
  min_tier: string;
  inputs?: string[];
  high_risk_actions?: string[];
  required_integrations?: string[];
}

export type AgentRunStatus =
  | "queued"
  | "running"
  | "awaiting_approval"
  | "succeeded"
  | "failed"
  | "cancelled";

export interface AgentRun {
  run_id: string;
  business_id?: string;
  agent: string;
  status: AgentRunStatus;
  progress?: number;
  created_at?: string;
  started_at?: string;
  pending_task_id?: string;
  output?: {
    summary?: string;
    artifacts?: string[];
  };
}

export interface TriggerAgentRunInput {
  objective: string;
  inputs?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Decisions (Decision Hub)
// ---------------------------------------------------------------------------

export type DecisionType =
  | "idea"
  | "feature"
  | "channel"
  | "pricing"
  | "tech_stack";

export type DecisionStatus = "scoring" | "ready" | "decided";

export interface AdvisorScores {
  yc_pmf: number;
  tech_feasibility: number;
  moonshot_potential: number;
  global_scale_ease: number;
  monetization_strength: number;
}

export interface DecisionOption {
  id: string;
  name: string;
  risk: number;
  complexity: number;
  potential: number;
  time_to_impact?: string;
  capital_required?: string;
  ai_recommendation?: string;
  advisor_scores?: AdvisorScores;
  overall_call?: string;
  justification?: string;
}

export interface Decision {
  id: string;
  business_id?: string;
  title: string;
  type?: DecisionType;
  status: DecisionStatus;
  options?: DecisionOption[];
  selected_option_id?: string;
  decided_at?: string;
  created_at?: string;
}

export interface CreateDecisionInput {
  title: string;
  type: DecisionType;
  options: { name: string }[];
}

export interface SelectDecisionInput {
  option_id: string;
  note?: string;
}

// ---------------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------------

export type TaskStatus =
  | "pending_approval"
  | "approved"
  | "rejected"
  | "completed";

export type RiskLevel = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  agent: string;
  status: TaskStatus;
  risk_level: RiskLevel;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Metrics & Exit Readiness
// ---------------------------------------------------------------------------

export interface Metrics {
  business_id: string;
  period: string;
  mrr: number;
  mrr_growth_pct: number;
  churn_rate_pct: number;
  cac: number;
  ltv: number;
  ltv_cac_ratio: number;
  signups: number;
  nps: number;
  updated_at: string;
}

export interface ExitReadiness {
  business_id: string;
  exit_readiness_score: number;
  components: {
    financials: number;
    metrics: number;
    documentation: number;
    operational_stability: number;
  };
  recommendation: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Integrations
// ---------------------------------------------------------------------------

export type IntegrationStatus = "connected" | "available" | "error";

export interface Integration {
  provider: string;
  category: string;
  status: IntegrationStatus;
  connected_at?: string;
}

export interface ConnectIntegrationResponse {
  provider: string;
  authorization_url: string;
  state: string;
}

// ---------------------------------------------------------------------------
// Activity Log
// ---------------------------------------------------------------------------

export type ActorType = "agent" | "human";

export interface ActivityEntry {
  id: string;
  actor_type: ActorType;
  actor_id: string;
  action: string;
  target: string;
  summary: string;
  created_at: string;
}
