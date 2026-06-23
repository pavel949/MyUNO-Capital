# Deployment — MyUNO Capital (Production)

This document describes how MyUNO Capital is built, shipped, and operated
beyond local development. It assumes familiarity with
[`getting-started.md`](./getting-started.md) for the local stack and shared
environment variables.

---

## 1. Environment overview

| Environment | Purpose | Infra | Data |
|-------------|---------|-------|------|
| **local** | Day-to-day development | Docker Compose (`docker-compose.yml`) | Disposable volumes; `make seed` data |
| **staging** | Pre-production verification, runs against real-shaped data | Kubernetes namespace `myuno-staging` | Managed Postgres + Redis (small tier), versioned object storage |
| **production** | Live customer traffic | Kubernetes namespace `myuno-prod` (multi-replica, HPA) | Managed Postgres (HA) + pgvector, managed Redis (HA), versioned object storage |

The same container images flow through all environments. Configuration differs
only via environment variables / secrets (see §4), never via separate builds.

---

## 2. Container build & registry

Images are built and pushed by CI on every merge to `main` and on tagged
releases. Two images are produced:

- `ghcr.io/your-org/myuno-backend` — FastAPI API **and** the Celery worker
  (the worker is the same image run with a different command).
- `ghcr.io/your-org/myuno-frontend` — Next.js 14 console.

Images are tagged with both the short Git SHA (immutable, used by deployments)
and a moving environment tag (`:staging`, `:latest`).

See §10 for the reference GitHub Actions workflow.

---

## 3. Kubernetes deployment overview

Traffic enters through an Ingress (TLS terminated there or at a managed load
balancer). The frontend and backend run as separate Deployments behind
ClusterIP Services. The Celery worker is its own Deployment with a Horizontal
Pod Autoscaler so agent workloads can scale independently of the API.
Stateful dependencies — Postgres (with pgvector), Redis, and object storage —
are **managed services**, not pods in the cluster.

```mermaid
flowchart TD
    User([Users / Browsers]) -->|HTTPS| Ingress[Ingress + TLS]

    Ingress -->|/| FE[Frontend Service<br/>Next.js 14]
    Ingress -->|/api, /docs| BE[Backend Service<br/>FastAPI]

    FE --> FEDeploy[Frontend Deployment<br/>replicas: 2..N]
    BE --> BEDeploy[Backend Deployment<br/>replicas: 2..N]

    BEDeploy -->|enqueue jobs| Redis[(Managed Redis<br/>broker + cache)]
    Worker[Worker Deployment<br/>Celery + HPA] -->|consume jobs| Redis
    HPA{{HPA: CPU / queue depth}} -.scales.-> Worker

    BEDeploy -->|SQL + vector| PG[(Managed PostgreSQL 16<br/>+ pgvector)]
    Worker -->|SQL + vector| PG

    BEDeploy -->|artifacts / logs| S3[(Object Storage<br/>S3-compatible, versioned)]
    Worker -->|artifacts / logs| S3

    BEDeploy -->|LLM calls| Anthropic[[Anthropic Claude API]]
    Worker -->|LLM calls| Anthropic
```

### Notes
- **Frontend / Backend**: 2+ replicas each, behind the Ingress. Stateless;
  scale on CPU/RPS.
- **Worker**: separate Deployment so a burst of agent tasks never starves the
  API. Autoscaled (see §8).
- **Postgres + pgvector**: managed service with the `vector` extension enabled.
  Schema applied via the migration job (§5).
- **Redis**: managed, used as both the Celery broker/result backend and the
  application cache.
- **Object storage**: S3-compatible bucket with versioning enabled (MinIO in
  local dev maps to e.g. AWS S3 / GCS in production).

---

## 4. Environment variables & secrets management

Non-sensitive config lives in a `ConfigMap`; all secrets live in a `Secret`
(ideally backed by an external secrets manager such as AWS Secrets Manager,
GCP Secret Manager, or Vault via the External Secrets Operator). Never bake
secrets into images.

| Variable | Kind | Source / Notes |
|----------|------|----------------|
| `APP_ENV` | config | `staging` or `production` |
| `SECRET_KEY` | secret | App signing key |
| `DATABASE_URL` | secret | Managed Postgres connection string (`postgresql+psycopg://...`) |
| `REDIS_URL` | secret | Managed Redis URL (cache, DB 0) |
| `CELERY_BROKER_URL` | secret | Managed Redis (DB 1) |
| `CELERY_RESULT_BACKEND` | secret | Managed Redis (DB 2) |
| `S3_ENDPOINT` | config | Object storage endpoint |
| `S3_BUCKET` | config | Bucket name |
| `S3_ACCESS_KEY` | secret | Object storage access key |
| `S3_SECRET_KEY` | secret | Object storage secret key |
| `ANTHROPIC_API_KEY` | secret | Anthropic API key (required) |
| `DEFAULT_LLM_MODEL` | config | `claude-opus-4-8` |
| `LLM_FALLBACK_MODEL` | config | `claude-haiku-4-5` |
| `JWT_SECRET` | secret | JWT signing secret |
| `JWT_EXPIRE_MINUTES` | config | Access token TTL |
| `STRIPE_API_KEY` | secret | Payments (if enabled) |
| `GITHUB_TOKEN` | secret | Source-control integration |
| `GOOGLE_ADS_*` | secret | Ads integration (if enabled) |
| `SENDGRID_API_KEY` | secret | Email integration (if enabled) |
| `CORS_ORIGINS` | config | Allowed origins for the API |
| `NEXT_PUBLIC_API_URL` | config | Public API base URL (frontend build/runtime) |

> Rotate secrets via the external secrets manager; the External Secrets
> Operator syncs them into the cluster and rolling restarts pick them up.

---

## 5. Database migrations in CI/CD

Migrations are **not** run by application pods on boot. Instead, a dedicated,
one-shot Kubernetes `Job` (or CI step) runs `alembic upgrade head` against the
target database *before* the new app version is rolled out.

A minimal migration Job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: myuno-migrate
  namespace: myuno-prod
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/your-org/myuno-backend:${GIT_SHA}
          command: ["alembic", "upgrade", "head"]
          envFrom:
            - secretRef:
                name: myuno-secrets
            - configMapRef:
                name: myuno-config
```

The deploy pipeline order is: **build & push → run migration Job → wait for
success → roll out new Deployments**. This keeps schema and code in lockstep
and supports zero-downtime rollouts when migrations are backward-compatible.

---

## 6. Observability & health checks

### Health endpoints
The backend exposes two probes that Kubernetes consumes:

| Endpoint | Probe | Meaning |
|----------|-------|---------|
| `/healthz` | liveness | Process is up and responsive |
| `/readyz` | readiness | Dependencies (DB, Redis) reachable; safe to receive traffic |

Example probe config:

```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8000 }
  initialDelaySeconds: 15
  periodSeconds: 20
readinessProbe:
  httpGet: { path: /readyz, port: 8000 }
  initialDelaySeconds: 10
  periodSeconds: 10
```

### Metrics, logs, traces
- **Metrics**: Prometheus scrapes `/metrics` on the backend (request rate,
  latency, error rate; Celery task counts, queue depth, task duration).
  Visualized in Grafana.
- **Logs**: structured JSON to stdout, shipped by the cluster log agent
  (e.g. Loki / CloudWatch / Cloud Logging). Application + agent activity log
  events are correlated by `tenant_id` and `request_id`.
- **Traces**: OpenTelemetry instrumentation on FastAPI and Celery; spans
  exported to an OTLP collector (e.g. Tempo / Jaeger). LLM calls are traced so
  you can attribute latency and cost per agent run.

---

## 7. Backup & disaster recovery

- **PostgreSQL**: managed automated daily snapshots + point-in-time recovery
  (PITR) via WAL archiving. Retention: 30 days (prod), 7 days (staging).
  Periodically test restores into a scratch instance.
- **Object storage**: bucket **versioning enabled** so artifacts/logs/backups
  can be recovered after accidental overwrite or deletion; lifecycle rules
  expire old non-current versions.
- **Redis**: treated as ephemeral (cache + transient queue). Tasks are
  persisted in Postgres, so a Redis loss costs in-flight queue state only,
  which is recovered via task retries (idempotent where applicable).
- **Secrets**: backed up in the external secrets manager, versioned and
  recoverable.
- **DR targets**: RPO ≤ 24h (covered by daily snapshots; near-zero with PITR),
  RTO ≤ 1h for a full region failover using cross-region snapshot copies.

---

## 8. Scaling & reliability

### Scaling
- **Frontend / Backend**: HPA on CPU (target ~60%) and/or RPS; min 2 replicas
  for availability across nodes/zones.
- **Worker**: HPA on CPU and Celery queue depth (custom metric via
  Prometheus Adapter / KEDA) so agent task spikes scale workers out and back.

Example worker HPA:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myuno-worker
  namespace: myuno-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myuno-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 65 }
    - type: Pods
      pods:
        metric: { name: celery_queue_depth }
        target: { type: AverageValue, averageValue: "30" }
```

### Reliability targets
Aligned with the product targets in `project.md`:

- **Uptime**: 99.9% for core APIs.
- **Latency**: simple tasks < 2s; complex workflows start within 5–10s with
  streaming progress.
- **Durability**: all tasks persisted; retries with exponential backoff;
  idempotency where applicable.

Supporting practices: multi-replica deployments across zones, PodDisruption
Budgets, rolling updates with readiness gating, and graceful shutdown
(`SIGTERM` handling so in-flight Celery tasks finish or requeue).

---

## 9. Multi-tenancy in production

Tenant isolation is enforced in the application layer (per-tenant keys/scoping
on every query) on top of a shared Postgres instance. All agent and human
actions are written to the global activity log for trust, debugging, and exit
due-diligence. Object storage is namespaced per tenant via key prefixes.

---

## 10. Reference CI workflow (GitHub Actions)

`.github/workflows/ci.yml` — lint, test, build, and push images. Adjust
registry, org, and secret names to your setup.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/your-org/myuno-backend
  IMAGE_FRONTEND: ghcr.io/your-org/myuno-frontend

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install backend dev deps
        run: pip install ruff black
      - name: Ruff
        run: ruff check backend
      - name: Black (check)
        run: black --check backend
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm", cache-dependency-path: frontend/package-lock.json }
      - name: Install frontend deps
        run: npm ci
        working-directory: frontend
      - name: ESLint
        run: npm run lint
        working-directory: frontend

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_USER: myuno
          POSTGRES_PASSWORD: myuno
          POSTGRES_DB: myuno_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U myuno"
          --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgresql+psycopg://myuno:myuno@localhost:5432/myuno_test
      REDIS_URL: redis://localhost:6379/0
      ANTHROPIC_API_KEY: test-key-not-used
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install backend deps
        run: pip install -r backend/requirements.txt
      - name: Apply migrations
        run: alembic upgrade head
        working-directory: backend
      - name: Backend tests
        run: pytest
        working-directory: backend
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm", cache-dependency-path: frontend/package-lock.json }
      - name: Frontend tests
        run: |
          npm ci
          npm test
        working-directory: frontend

  build-and-push:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build & push backend
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.IMAGE_BACKEND }}:latest
            ${{ env.IMAGE_BACKEND }}:${{ github.sha }}
      - name: Build & push frontend
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ env.IMAGE_FRONTEND }}:latest
            ${{ env.IMAGE_FRONTEND }}:${{ github.sha }}
```

After `build-and-push`, a separate deploy job (or GitOps tool such as Argo CD /
Flux) runs the migration Job from §5 and then updates the Deployments to the
new `${{ github.sha }}` tag.

---

## 11. Deployment checklist

- [ ] Secrets populated in the external secrets manager and synced.
- [ ] `vector` extension enabled on the managed Postgres.
- [ ] Migration Job ran successfully (`alembic upgrade head`).
- [ ] Health probes (`/healthz`, `/readyz`) green for backend.
- [ ] HPAs active for backend, frontend, and worker.
- [ ] Metrics/logs/traces flowing to the observability stack.
- [ ] Backups verified (snapshot + object-storage versioning).
- [ ] TLS valid at the Ingress; `CORS_ORIGINS` set to production origins.
