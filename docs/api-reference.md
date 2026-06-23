# MyUNO Capital — REST API Reference

The MyUNO Capital backend is a **Python 3.12 / FastAPI** service. It exposes a JSON REST API secured with JWT bearer authentication and scoped to a tenant per request.

- **Base URL (production):** `https://api.myuno.capital`
- **API version prefix:** `/api/v1`
- **Full example endpoint:** `https://api.myuno.capital/api/v1/businesses`

### Interactive Documentation

FastAPI auto-generates an OpenAPI 3.1 schema. Live, interactive documentation is available at:

- **Swagger UI:** [`/docs`](https://api.myuno.capital/docs)
- **ReDoc:** [`/redoc`](https://api.myuno.capital/redoc)
- **Raw OpenAPI schema:** `/openapi.json`

---

## Authentication

MyUNO Capital uses **JWT bearer tokens**. The flow is: register (or log in) → receive an `access_token` and `refresh_token` → send the access token on every subsequent request.

### Authorization header

```http
Authorization: Bearer <access_token>
```

- **Access tokens** are short-lived (default 30 minutes).
- **Refresh tokens** are long-lived (default 30 days) and used at `POST /api/v1/auth/refresh` to mint a new access token.
- Higher tiers may authenticate via **SSO (SAML/OIDC)**; see [Security & Compliance](./security-compliance.md).

### Tenant scoping

Every authenticated principal belongs to one or more **tenants** (workspaces). The active tenant is encoded in the JWT claims (`tenant_id`). All resources (businesses, goals, agent runs, etc.) are isolated per tenant; requests can only read or write data within the caller's tenant. To act within a specific tenant when you belong to several, include the header:

```http
X-Tenant-Id: 7f1c0b2a-1d3e-4c5a-9b8f-0a1b2c3d4e5f
```

If omitted, the user's default tenant is used.

---

## Conventions

### Content type

All request and response bodies are `application/json; charset=utf-8`. Request bodies are validated with **Pydantic v2**; invalid payloads return `422`.

### Identifiers and timestamps

- All resource `id` values are **UUID v4** strings.
- All timestamps are **ISO 8601 / RFC 3339** in UTC (e.g., `2026-06-23T14:05:00Z`).
- All score fields (risk, complexity, potential, exit-readiness, advisor scores) are integers in the range **0–100**.

### Pagination

List endpoints use **limit/offset** pagination.

| Query param | Default | Max | Description |
|-------------|---------|-----|-------------|
| `limit` | `20` | `100` | Number of items to return |
| `offset` | `0` | — | Number of items to skip |

Paginated responses are wrapped:

```json
{
  "items": [],
  "total": 137,
  "limit": 20,
  "offset": 0
}
```

### Error envelope

All errors share one envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Field 'name' is required.",
    "details": [
      { "field": "name", "issue": "missing" }
    ],
    "request_id": "req_3a8f12c9d4e1"
  }
}
```

| HTTP status | `error.code` | Meaning |
|-------------|--------------|---------|
| `400` | `bad_request` | Malformed request |
| `401` | `unauthorized` | Missing/invalid/expired token |
| `403` | `forbidden` | Authenticated but not allowed (RBAC / tenant) |
| `404` | `not_found` | Resource does not exist in this tenant |
| `409` | `conflict` | Duplicate or state conflict |
| `422` | `validation_error` | Pydantic validation failure |
| `429` | `rate_limited` | Rate limit exceeded |
| `500` | `internal_error` | Unexpected server error |

### Rate limiting

Limits are applied per tenant and per token. Every response includes:

```http
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 598
X-RateLimit-Reset: 1750684800
```

When exceeded, the API returns `429` with a `Retry-After` header (seconds).

### Idempotency

For unsafe, non-idempotent `POST` operations (e.g., triggering an agent run, creating a business), send a client-generated key:

```http
Idempotency-Key: 1f8e6d4c-2b3a-4e5f-8a7b-9c0d1e2f3a4b
```

Replaying the same key within 24 hours returns the original response instead of creating a duplicate.

---

## Endpoints

### Auth

#### `POST /api/v1/auth/register`

Create a new founder account and its default tenant.

**Request**

```json
{
  "email": "pavel@ignatevestate.com",
  "password": "S3cure-passphrase!",
  "full_name": "Pavel Ignatev",
  "tenant_name": "Ignatev Ventures"
}
```

**Response `201`**

```json
{
  "user": {
    "id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
    "email": "pavel@ignatevestate.com",
    "full_name": "Pavel Ignatev",
    "created_at": "2026-06-23T14:05:00Z"
  },
  "tenant": {
    "id": "7f1c0b2a-1d3e-4c5a-9b8f-0a1b2c3d4e5f",
    "name": "Ignatev Ventures",
    "role": "owner"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `POST /api/v1/auth/login`

Exchange credentials for tokens.

**Request**

```json
{ "email": "pavel@ignatevestate.com", "password": "S3cure-passphrase!" }
```

**Response `200`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `POST /api/v1/auth/refresh`

Mint a new access token from a refresh token.

**Request**

```json
{ "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Response `200`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `GET /api/v1/auth/me`

Return the currently authenticated user and active tenant.

**Response `200`**

```json
{
  "id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
  "email": "pavel@ignatevestate.com",
  "full_name": "Pavel Ignatev",
  "active_tenant_id": "7f1c0b2a-1d3e-4c5a-9b8f-0a1b2c3d4e5f",
  "role": "owner",
  "mfa_enabled": true
}
```

---

### Tenants & Users

#### `GET /api/v1/users/me/profile`

Get the current user's profile and preferences.

**Response `200`**

```json
{
  "id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
  "full_name": "Pavel Ignatev",
  "email": "pavel@ignatevestate.com",
  "locale": "en",
  "timezone": "Asia/Bangkok",
  "default_autonomy_profile": "guided"
}
```

#### `PATCH /api/v1/users/me/profile`

Update profile fields.

**Request**

```json
{ "timezone": "Asia/Bangkok", "default_autonomy_profile": "guided" }
```

**Response `200`** — returns the updated profile object.

#### `GET /api/v1/users/me/memberships`

List the tenants the user belongs to and their role in each.

**Response `200`**

```json
{
  "items": [
    {
      "tenant_id": "7f1c0b2a-1d3e-4c5a-9b8f-0a1b2c3d4e5f",
      "tenant_name": "Ignatev Ventures",
      "role": "owner",
      "joined_at": "2026-06-23T14:05:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

> Roles: `owner` (Founder), `collaborator`, `guest`. See [RBAC](./security-compliance.md).

---

### Businesses

A **business** is a company/project managed inside a tenant. A tenant may hold one or many businesses depending on its plan tier (see [Roadmap → Pricing](./roadmap.md)).

#### `GET /api/v1/businesses`

List businesses in the active tenant. Supports `limit`/`offset` and `?stage=` filtering.

**Response `200`**

```json
{
  "items": [
    {
      "id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
      "name": "InboxZero SaaS",
      "model_template": "b2b_saas_micro",
      "stage": "validate",
      "created_at": "2026-06-10T09:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### `POST /api/v1/businesses`

Create a business.

**Request**

```json
{
  "name": "InboxZero SaaS",
  "model_template": "b2b_saas_micro",
  "description": "AI inbox triage for solo consultants.",
  "autonomy_profile": "guided"
}
```

**Response `201`**

```json
{
  "id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "name": "InboxZero SaaS",
  "model_template": "b2b_saas_micro",
  "description": "AI inbox triage for solo consultants.",
  "stage": "ideation",
  "autonomy_profile": "guided",
  "created_at": "2026-06-23T14:10:00Z"
}
```

#### `GET /api/v1/businesses/{business_id}`

Get a single business. **Response `200`** — the business object above.

#### `PATCH /api/v1/businesses/{business_id}`

Update fields (name, description, stage, autonomy profile).

**Request**

```json
{ "stage": "build", "autonomy_profile": "autonomous_within_limits" }
```

**Response `200`** — the updated business object.

#### `DELETE /api/v1/businesses/{business_id}`

Soft-delete a business. **Response `204`** (no content).

---

### Goals & OKRs

#### `POST /api/v1/businesses/{business_id}/goals`

Create a high-level goal in plain language.

**Request**

```json
{
  "title": "Profitably reach $10k MRR in 12 months",
  "target_date": "2027-06-23",
  "metric": "mrr",
  "target_value": 10000
}
```

**Response `201`**

```json
{
  "id": "c2e5f8b1-3d4a-4b6c-9e0f-2a3b4c5d6e7f",
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "title": "Profitably reach $10k MRR in 12 months",
  "metric": "mrr",
  "target_value": 10000,
  "target_date": "2027-06-23",
  "status": "active",
  "created_at": "2026-06-23T14:12:00Z"
}
```

#### `GET /api/v1/businesses/{business_id}/goals`

List goals. **Response `200`** — paginated list of goal objects.

#### `POST /api/v1/businesses/{business_id}/goals/{goal_id}/okrs`

Have the StrategyAgent generate OKRs from a goal.

**Request**

```json
{ "horizon": "quarter" }
```

**Response `202`**

```json
{
  "goal_id": "c2e5f8b1-3d4a-4b6c-9e0f-2a3b4c5d6e7f",
  "objectives": [
    {
      "id": "d3f6a9c2-4e5b-4c7d-8f1a-3b4c5d6e7f80",
      "objective": "Validate demand and ship a payable MVP",
      "key_results": [
        { "kr": "Land 200 unique landing-page visitors", "target": 200, "current": 0 },
        { "kr": "Reach 5% signup conversion", "target": 5, "current": 0 },
        { "kr": "Onboard 3 paying customers", "target": 3, "current": 0 }
      ]
    }
  ],
  "generated_by": "StrategyAgent",
  "generated_at": "2026-06-23T14:13:00Z"
}
```

---

### Agents

Agents are the virtual team members (IdeaValidationAgent, StrategyAgent, DevAgent, AdsAgent, etc.). See the full roster in [Product overview](./overview.md).

#### `GET /api/v1/agents`

List available agents (catalog), with availability per plan tier.

**Response `200`**

```json
{
  "items": [
    {
      "agent": "IdeaValidationAgent",
      "category": "strategy",
      "description": "Researches market, runs validation experiments, scores ideas.",
      "min_tier": "free"
    },
    {
      "agent": "AdsAgent",
      "category": "growth",
      "description": "Sets up and optimizes ad campaigns within budget guardrails.",
      "min_tier": "solo_starter"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/v1/agents/{agent}`

Get one agent's capabilities, required scopes, and high-risk actions.

**Response `200`**

```json
{
  "agent": "AdsAgent",
  "category": "growth",
  "description": "Sets up and optimizes ad campaigns within budget guardrails.",
  "inputs": ["budget_cap_daily", "channels", "target_audience"],
  "high_risk_actions": ["increase_daily_budget", "launch_campaign"],
  "required_integrations": ["google_ads", "meta_ads"],
  "min_tier": "solo_starter"
}
```

#### `POST /api/v1/businesses/{business_id}/agents/{agent}/run`

Trigger an agent run. Honors the business autonomy profile; high-risk steps may generate **pending-approval tasks**. Send an `Idempotency-Key`.

**Request**

```json
{
  "objective": "Validate demand for InboxZero with a landing page and $50/day ad test.",
  "inputs": {
    "budget_cap_daily": 50,
    "channels": ["google_ads"],
    "duration_days": 7
  }
}
```

**Response `202`**

```json
{
  "run_id": "e4a7b0c3-5d6e-4f8a-9b1c-4d5e6f7a8b90",
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "agent": "AdsAgent",
  "status": "queued",
  "created_at": "2026-06-23T14:15:00Z"
}
```

#### `GET /api/v1/businesses/{business_id}/agents/runs/{run_id}`

Get run status and output.

**Response `200`**

```json
{
  "run_id": "e4a7b0c3-5d6e-4f8a-9b1c-4d5e6f7a8b90",
  "agent": "AdsAgent",
  "status": "awaiting_approval",
  "progress": 0.6,
  "started_at": "2026-06-23T14:15:05Z",
  "pending_task_id": "f5b8c1d4-6e7f-4a9b-8c2d-5e6f7a8b9c01",
  "output": {
    "summary": "Campaign drafted; awaiting approval to launch at $50/day.",
    "artifacts": ["landing_page_url", "ad_creatives"]
  }
}
```

> `status` values: `queued`, `running`, `awaiting_approval`, `succeeded`, `failed`, `cancelled`.

#### `GET /api/v1/businesses/{business_id}/agents/runs`

List runs for a business. Filter with `?agent=` and `?status=`. **Response `200`** — paginated list of run objects.

---

### Decisions (Decision Hub)

The [Decision Hub](./decision-hub.md) compares options with **Risk / Complexity / Potential** scores plus advisor scores, all `0–100`.

#### `POST /api/v1/businesses/{business_id}/decisions`

Create a decision and its options.

**Request**

```json
{
  "title": "Which idea to build first?",
  "type": "idea",
  "options": [
    { "name": "SaaS A" },
    { "name": "Info Product B" },
    { "name": "Marketplace C" }
  ]
}
```

**Response `201`**

```json
{
  "id": "a6c9d2e5-7f8a-4b0c-9d1e-6f7a8b9c0d12",
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "title": "Which idea to build first?",
  "type": "idea",
  "status": "scoring",
  "created_at": "2026-06-23T14:18:00Z"
}
```

#### `GET /api/v1/businesses/{business_id}/decisions/{decision_id}/options`

List options with their (possibly still-computing) scores.

**Response `200`**

```json
{
  "items": [
    {
      "id": "b7d0e3f6-8a9b-4c1d-9e2f-7a8b9c0d1e23",
      "name": "SaaS A",
      "risk": 35,
      "complexity": 60,
      "potential": 82,
      "time_to_impact": "3-6 months",
      "capital_required": "$3k-$5k",
      "ai_recommendation": "Strong candidate"
    }
  ],
  "total": 3,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/v1/businesses/{business_id}/decisions/{decision_id}`

Get the decision with fully scored options, advisor scores, and justifications.

**Response `200`**

```json
{
  "id": "a6c9d2e5-7f8a-4b0c-9d1e-6f7a8b9c0d12",
  "title": "Which idea to build first?",
  "status": "ready",
  "options": [
    {
      "id": "b7d0e3f6-8a9b-4c1d-9e2f-7a8b9c0d1e23",
      "name": "SaaS A",
      "risk": 35,
      "complexity": 60,
      "potential": 82,
      "advisor_scores": {
        "yc_pmf": 80,
        "tech_feasibility": 78,
        "moonshot_potential": 55,
        "global_scale_ease": 75,
        "monetization_strength": 84
      },
      "overall_call": "Build now",
      "justification": "Strong potential and monetization with manageable risk."
    }
  ]
}
```

#### `POST /api/v1/businesses/{business_id}/decisions/{decision_id}/select`

Select the chosen option. The decision and reasoning are written to the activity log.

**Request**

```json
{ "option_id": "b7d0e3f6-8a9b-4c1d-9e2f-7a8b9c0d1e23", "note": "Best risk/reward." }
```

**Response `200`**

```json
{
  "id": "a6c9d2e5-7f8a-4b0c-9d1e-6f7a8b9c0d12",
  "status": "decided",
  "selected_option_id": "b7d0e3f6-8a9b-4c1d-9e2f-7a8b9c0d1e23",
  "decided_at": "2026-06-23T14:25:00Z"
}
```

---

### Tasks

Tasks are units of work produced by agents. Some require human sign-off (high-risk actions such as ad-spend increases, production deploys, or payment changes).

#### `GET /api/v1/businesses/{business_id}/tasks`

List tasks. Filter with `?status=` (e.g., `pending_approval`).

**Response `200`**

```json
{
  "items": [
    {
      "id": "f5b8c1d4-6e7f-4a9b-8c2d-5e6f7a8b9c01",
      "title": "Launch Google Ads campaign at $50/day",
      "agent": "AdsAgent",
      "status": "pending_approval",
      "risk_level": "high",
      "created_at": "2026-06-23T14:16:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/v1/businesses/{business_id}/tasks/{task_id}`

Get a single task with its full proposed action and context. **Response `200`** — the task object.

#### `POST /api/v1/businesses/{business_id}/tasks/{task_id}/approve`

Approve a pending-approval task; the agent proceeds.

**Request**

```json
{ "note": "Approved within the $50/day cap." }
```

**Response `200`**

```json
{
  "id": "f5b8c1d4-6e7f-4a9b-8c2d-5e6f7a8b9c01",
  "status": "approved",
  "approved_by": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
  "approved_at": "2026-06-23T14:20:00Z"
}
```

#### `POST /api/v1/businesses/{business_id}/tasks/{task_id}/reject`

Reject a pending-approval task.

**Request**

```json
{ "reason": "Hold ad spend until the landing page copy is revised." }
```

**Response `200`** — the task object with `status: "rejected"`.

---

### Metrics & Dashboards

#### `GET /api/v1/businesses/{business_id}/metrics`

Get current business metrics. Optional `?period=` (`mtd`, `30d`, `90d`).

**Response `200`**

```json
{
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "period": "30d",
  "mrr": 4200,
  "mrr_growth_pct": 18.5,
  "churn_rate_pct": 3.1,
  "cac": 120,
  "ltv": 540,
  "ltv_cac_ratio": 4.5,
  "signups": 86,
  "nps": 42,
  "updated_at": "2026-06-23T14:00:00Z"
}
```

#### `GET /api/v1/businesses/{business_id}/exit-readiness`

Get the exit-readiness score (0–100) maintained by the ExitPlanningAgent, with its component breakdown.

**Response `200`**

```json
{
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "exit_readiness_score": 68,
  "components": {
    "financials": 72,
    "metrics": 70,
    "documentation": 60,
    "operational_stability": 71
  },
  "recommendation": "Improve documentation and data room before outreach.",
  "updated_at": "2026-06-23T14:00:00Z"
}
```

---

### Integrations

#### `GET /api/v1/businesses/{business_id}/integrations`

List available and connected integrations.

**Response `200`**

```json
{
  "items": [
    {
      "provider": "stripe",
      "category": "payments",
      "status": "connected",
      "connected_at": "2026-06-15T08:00:00Z"
    },
    {
      "provider": "google_ads",
      "category": "ads",
      "status": "available"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

#### `POST /api/v1/businesses/{business_id}/integrations/{provider}/connect`

Start the OAuth connect flow. Returns an authorization URL to redirect the founder to.

**Request**

```json
{ "redirect_uri": "https://app.myuno.capital/integrations/callback" }
```

**Response `200`**

```json
{
  "provider": "google_ads",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "c8e1f4a7-9b0c-4d2e-8f3a-9b0c1d2e3f44"
}
```

#### `GET /api/v1/integrations/oauth/callback`

OAuth redirect target. Exchanges the authorization `code` for tokens and stores them encrypted, then redirects back to the app. Query params: `code`, `state`.

**Response `302`** — redirect to the app with `?status=connected`.

#### `POST /api/v1/businesses/{business_id}/integrations/{provider}/disconnect`

Revoke and remove a connected integration. **Response `204`** (no content).

---

### Activity Log

The **Global Activity Log** captures every significant agent and human action — used for debugging, trust, compliance, and exit due diligence. See [Security & Compliance](./security-compliance.md).

#### `GET /api/v1/businesses/{business_id}/activity`

List activity entries (most recent first). Filter with `?actor_type=` (`agent`|`human`), `?agent=`, `?since=`.

**Response `200`**

```json
{
  "items": [
    {
      "id": "d9f2a5b8-0c1d-4e3f-9a4b-0c1d2e3f4a55",
      "actor_type": "human",
      "actor_id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
      "action": "task.approved",
      "target": "task:f5b8c1d4-6e7f-4a9b-8c2d-5e6f7a8b9c01",
      "summary": "Approved Google Ads launch at $50/day.",
      "created_at": "2026-06-23T14:20:00Z"
    },
    {
      "id": "e0a3b6c9-1d2e-4f4a-8b5c-1d2e3f4a5b66",
      "actor_type": "agent",
      "actor_id": "AdsAgent",
      "action": "campaign.launched",
      "target": "business:b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
      "summary": "Launched Google Ads campaign within the $50/day cap.",
      "created_at": "2026-06-23T14:20:30Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

---

## Webhooks

### Outbound: webhooks MyUNO Capital sends to you

Register endpoints to receive event notifications (e.g., a task needs approval, an agent run finished, exit-readiness changed).

#### `POST /api/v1/webhooks`

```json
{
  "url": "https://your-app.example.com/hooks/myuno",
  "events": ["task.pending_approval", "agent_run.succeeded", "exit_readiness.changed"]
}
```

**Response `201`**

```json
{
  "id": "f1b4c7d0-2e3f-4a5b-9c6d-2e3f4a5b6c77",
  "url": "https://your-app.example.com/hooks/myuno",
  "events": ["task.pending_approval", "agent_run.succeeded", "exit_readiness.changed"],
  "signing_secret": "whsec_8f3a9b0c1d2e3f4a5b6c7d8e9f0a1b2c",
  "status": "active"
}
```

**Delivery format.** Each delivery is a `POST` to your URL with a signed JSON body:

```json
{
  "id": "evt_3a8f12c9d4e1",
  "type": "task.pending_approval",
  "tenant_id": "7f1c0b2a-1d3e-4c5a-9b8f-0a1b2c3d4e5f",
  "business_id": "b1d4e7a0-2c3f-4a5b-8d9e-1f2a3b4c5d6e",
  "created_at": "2026-06-23T14:16:00Z",
  "data": {
    "task_id": "f5b8c1d4-6e7f-4a9b-8c2d-5e6f7a8b9c01",
    "title": "Launch Google Ads campaign at $50/day",
    "risk_level": "high"
  }
}
```

**Verification.** Each request carries:

```http
X-MyUNO-Signature: t=1750684560,v1=5257a869e7ec...
```

`v1` is the HMAC-SHA256 of `"{t}.{raw_body}"` using your `signing_secret`. Reject requests older than 5 minutes or with a mismatched signature. Respond `2xx` within 10 seconds; failed deliveries retry with exponential backoff.

### Inbound: webhooks MyUNO Capital receives from integrations

When you connect an integration (Stripe, GitHub, Google Ads, etc.), MyUNO Capital provisions a per-tenant inbound endpoint and registers it with the provider during OAuth:

```
POST https://api.myuno.capital/api/v1/integrations/{provider}/events/{tenant_id}
```

Inbound payloads are verified using the provider's own signature scheme (e.g., the `Stripe-Signature` header) before being normalized into MyUNO events (such as `payment.succeeded` or `repo.push`) and routed to the relevant agents and the activity log.

---

## Related Documentation

- [Product Overview](./overview.md)
- [Security & Compliance](./security-compliance.md)
- [Roadmap](./roadmap.md)
- [Decision Hub](./decision-hub.md)

---

*© 2026 MyUNO Capital. All rights reserved.*
