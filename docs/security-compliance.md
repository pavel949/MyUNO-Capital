# MyUNO Capital — Security, Privacy & Compliance

MyUNO Capital runs founders' businesses end-to-end, often with real budgets, code, and customer data. Trust is the product. This document describes how the platform protects data, constrains autonomous agents, isolates tenants, and approaches compliance.

For the API-level details of authentication and the activity log, see the [API Reference](./api-reference.md).

---

## 1. Security Practices

- **Encryption in transit.** All traffic is served over HTTPS/TLS. Plain HTTP is redirected; HSTS is enforced.
- **Encryption at rest.** The primary datastore (**PostgreSQL 16 + pgvector**) and object storage are encrypted at rest. Secrets and sensitive fields (integration tokens, API keys) are stored in **encrypted form** and never logged in plaintext.
- **Secrets management.** Integration credentials and OAuth tokens are held in a dedicated secrets store with restricted access, rotated where providers support it, and decrypted only at point of use.
- **Authentication.** JWT bearer tokens with short-lived access tokens and longer-lived refresh tokens (see [Authentication](./api-reference.md#authentication)).
- **MFA.** Multi-factor authentication is available for all accounts and **required for admin and sensitive accounts**.
- **SSO.** Optional **SSO via SAML / OIDC** for higher tiers, allowing founders and studios to centralize identity.

### Role-Based Access Control (RBAC)

Access is governed by roles scoped to a tenant:

| Role | Intended for | Capabilities |
|------|-------------|--------------|
| **Founder (owner)** | The solo founder / account owner | Full control: businesses, agents, autonomy profiles, billing, integrations, member management, approvals |
| **Collaborator** | Trusted teammates or contractors | Operate businesses and approve tasks within granted scopes; cannot manage billing or delete the tenant |
| **Guest** | Advisors, auditors, limited helpers | Read-mostly access to specific businesses/dashboards; no high-risk approvals |

All sensitive actions — by humans and AI — are recorded in **audit logs**.

---

## 2. AI Safety & Guardrails

MyUNO Capital agents act on the founder's behalf, so autonomy is constrained by design. Conservative defaults are the starting point; founders widen autonomy as trust grows.

### Autonomy profiles

Each business runs under one of three configurable autonomy profiles:

- **Ask me first** — everything requires explicit approval.
- **Guided autonomy** — small, low-risk decisions are automatic; big ones require approval.
- **Autonomous within limits** — fully automatic, but only within defined budgets and guardrails.

### Approval checkpoints for high-risk actions

Regardless of profile, certain action classes always pause for human sign-off (surfaced as **pending-approval tasks**; see [Tasks](./api-reference.md#tasks)):

- **Ad spend** above configured caps (e.g., *"Ask before spending > $100/day on ads"*).
- **Production deploys** of code.
- **Payment / billing changes** (pricing changes, refunds, payout configuration).
- Other actions the founder marks as requiring approval.

### Execution safety

- **Sandboxed execution.** Agent code execution and risky tool calls run in sandboxed environments before any change reaches production.
- **Rollbacks.** The DevOpsAgent and orchestrator roll back on failure and notify the founder.
- **Full activity logging.** Every significant agent and human action is written to the **Global Activity Log** — for debugging, trust, compliance, and exit due diligence.
- **Conservative defaults & gradual autonomy.** New businesses start closer to copilot mode; autonomy increases gradually as the founder builds confidence.

---

## 3. Tenant Isolation & Access Control

MyUNO Capital is a **multi-tenant SaaS** with strict isolation:

- **Logical data isolation** in PostgreSQL via per-tenant keys/schemas, so one tenant's data is never visible to another.
- **Tenant scoping at the application layer.** Every request is bound to a tenant (`tenant_id` JWT claim, optionally overridden by the `X-Tenant-Id` header). Queries are filtered by tenant; cross-tenant reads/writes are rejected with `403`.
- **RBAC within each tenant** layers role checks on top of tenant scoping.
- **Isolated integration credentials and semantic memory** (pgvector embeddings) per tenant — no shared retrieval across tenants.

---

## 4. Data Handling & Privacy

- **No training on customer data by default.** Customer data is **not** used to train shared models unless the customer **explicitly opts in**.
- **Per-tenant data export.** Tenants can export their data (businesses, decisions, activity log, artifacts) in machine-readable form.
- **Per-tenant data deletion.** Tenants can request deletion of their data; deletion cascades across primary storage, object storage, and the vector store.
- **Encryption.** Data is encrypted **at rest and in transit** (see Section 1).
- **Secrets management.** Integration tokens and keys are encrypted and access-restricted (see Section 1).
- **Data minimization.** Agents request only the integration scopes they need; high-risk scopes are surfaced to the founder at connect time.

---

## 5. Compliance Roadmap

Compliance is staged to match the platform's growth (see also the [Roadmap](./roadmap.md)):

**Early (now):**
- **GDPR-aware design** — lawful basis, data subject rights (export/deletion), data minimization, regional awareness.
- **Data Processing Agreements (DPAs)** offered to customers.

**Later (as scale and enterprise demand grow):**
- **SOC 2 Type I, then Type II.**
- **ISO 27001.**
- **Domain-specific standards** where particular customer segments require them.

---

## 6. Responsible AI

- **Transparency.** Agents explain their reasoning; the Decision Hub records scores and justifications for every major decision (see [Decision Hub](./decision-hub.md)).
- **Human-in-the-loop.** The founder is always the final decision-maker; high-risk actions require explicit approval, and any agent action can be paused, adjusted, or overridden at any time.
- **Logging of agent decisions for due diligence.** The activity log preserves a complete, timestamped record of agent and human decisions — supporting trust today and **exit due diligence** later.
- **Model routing with oversight.** Tasks are routed to appropriate models (default Anthropic Claude — `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`), balancing capability, cost, and latency, while keeping guardrails and approvals intact.

---

## 7. Vulnerability Reporting / Responsible Disclosure

We welcome reports from security researchers and customers.

- **Contact:** `security@myuno.capital`
- **What to include:** a clear description, reproduction steps, affected endpoints or components, and impact assessment.
- **Our commitment:**
  - Acknowledge receipt within **2 business days**.
  - Provide a triage assessment within **5 business days**.
  - Keep you informed through remediation and coordinate disclosure timing.
- **Safe harbor.** Good-faith research that respects user privacy, avoids data destruction, and does not degrade service will not lead to legal action. **Do not** access or modify other tenants' data, run automated high-volume attacks against production, or publicly disclose an issue before it is resolved.

Please report privately first; do not open public issues for security vulnerabilities.

---

## Related Documentation

- [Product Overview](./overview.md)
- [API Reference](./api-reference.md)
- [Roadmap](./roadmap.md)
- [Decision Hub](./decision-hub.md)

---

*© 2026 MyUNO Capital. All rights reserved.*
