# Contributing to MyUNO Capital

Thank you for your interest in contributing to **MyUNO Capital** — the Autonomous AI Operating System for solo entrepreneurs (idea → exit). This guide explains how to set up your environment, our workflow, coding standards, and how to add new agents.

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Branching Model](#branching-model)
- [Commit Message Conventions](#commit-message-conventions)
- [Code Style](#code-style)
- [Running Tests](#running-tests)
- [Pull Request Process](#pull-request-process)
- [Adding a New Agent](#adding-a-new-agent)
- [Reporting Issues](#reporting-issues)

---

## Development Environment Setup

The fastest path to a working environment is the local Docker stack described in the [Getting Started guide](docs/getting-started.md):

```bash
git clone https://github.com/myuno-capital/myuno-capital.git
cd myuno-capital
cp .env.example .env        # add your ANTHROPIC_API_KEY and integration keys
docker compose up
```

For native (non-Docker) development of individual services:

**Backend (Python 3.12, FastAPI):**

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head            # apply migrations against your local PostgreSQL
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

**Frontend (Next.js 14):**

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

See [docs/getting-started.md](docs/getting-started.md) for full prerequisites (PostgreSQL 16 + pgvector, Redis 7, MinIO) and configuration details.

---

## Branching Model

We use a trunk-based model with short-lived feature branches off `main`.

- `main` — always deployable. Protected; no direct pushes.
- Feature branches — branch from `main`, named by type and scope:
  - `feat/decision-hub-scoring`
  - `fix/celery-retry-backoff`
  - `docs/agents-reference`
  - `chore/bump-pydantic`
  - `refactor/orchestrator-routing`

Keep branches focused and rebase on `main` before opening a PR to minimize merge conflicts.

---

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/). The format is:

```text
<type>(<optional scope>): <short summary>

<optional body>

<optional footer(s)>
```

Common types:

| Type | Use for |
|------|---------|
| `feat` | A new feature (e.g., a new agent or endpoint) |
| `fix` | A bug fix |
| `docs` | Documentation-only changes |
| `style` | Formatting, no logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Build, tooling, dependencies |
| `ci` | CI/CD configuration |

Examples:

```text
feat(agents): add SEOAgent keyword research workflow
fix(orchestrator): respect per-tenant autonomy budget guardrails
docs(decision-hub): document Potential Score formula inputs
```

---

## Code Style

All style checks run in CI via GitHub Actions and must pass before merge.

### Python (`backend/`)

- **Formatting:** [Black](https://black.readthedocs.io/)
- **Linting:** [Ruff](https://docs.astral.sh/ruff/) (includes import sorting)
- **Type checking:** [mypy](https://mypy-lang.org/) with Pydantic v2 plugin
- Target Python 3.12. Use type hints everywhere; prefer Pydantic v2 models for I/O schemas and SQLAlchemy 2.x typed mappings for models.

```bash
cd backend
ruff check . --fix
black .
mypy app
```

### TypeScript / Frontend (`frontend/`)

- **Linting:** [ESLint](https://eslint.org/) (Next.js + TypeScript config)
- **Formatting:** [Prettier](https://prettier.io/)
- Use TypeScript strict mode. Style with Tailwind CSS utility classes.

```bash
cd frontend
npm run lint
npm run format
```

> Tip: install the repo's pre-commit hooks (`pre-commit install`) so Ruff, Black, ESLint, and Prettier run automatically before each commit.

---

## Running Tests

### Backend (pytest)

```bash
cd backend
pytest                       # full suite
pytest --cov=app            # with coverage
pytest tests/agents/test_idea_validation_agent.py   # a single file
```

### Frontend

```bash
cd frontend
npm test                     # unit / component tests
npm run test:e2e             # end-to-end (if configured)
```

All new features should include tests. Bug fixes should include a regression test that fails before the fix and passes after.

---

## Pull Request Process

1. **Open an issue first** for non-trivial changes so we can align on approach.
2. **Branch** from `main` using the naming convention above.
3. **Keep PRs small and focused** — one logical change per PR.
4. **Ensure quality gates pass locally:** linting, type checks, and tests.
5. **Write a clear PR description:** what changed, why, how to test, and link the related issue (`Closes #123`).
6. **Update documentation** in `docs/` when behavior, APIs, agents, or scoring change.
7. **Request review.** At least one maintainer approval is required.
8. **CI must be green** before merge. PRs are merged with a squash merge using a Conventional Commit title.

---

## Adding a New Agent

Agents are the heart of MyUNO Capital. New agents (or advisor agents in the Elite Advisor & Accelerator Layer) live under `backend/app/agents/`. To add one:

1. **Create the agent module** in `backend/app/agents/`, e.g. `backend/app/agents/seo_agent.py`. Follow the existing base-agent interface (config, tools, `run`/`plan` methods) used by agents such as `IdeaValidationAgent` and `StrategyAgent`.
2. **Register the agent** with the orchestrator so it can be routed tasks and scheduled (e.g., in the agent registry under `backend/app/agents/registry.py`).
3. **Declare its tools** — which capabilities it may call (HTTP, DB, repo access, third-party APIs). Respect tenant-level **Autonomy Profiles** and guardrails; high-risk actions must route through the approvals flow.
4. **Wire LLM access** through the provider-agnostic orchestrator. Choose a default model by task type (`claude-haiku-4-5` for light/fast tasks, `claude-sonnet-4-6` for standard reasoning, `claude-opus-4-8` for complex multi-step reasoning). Never hardcode a provider.
5. **Add Decision Hub scoring** if the agent contributes scores (Risk / Complexity / Potential, advisor dimension scores) — see [docs/decision-hub.md](docs/decision-hub.md).
6. **Emit activity-log events** for every significant action (trust, debugging, compliance, exit due diligence).
7. **Add Pydantic schemas** for the agent's inputs/outputs in `backend/app/schemas/`.
8. **Write tests** under `backend/tests/agents/`.
9. **Document the agent** in [docs/agents.md](docs/agents.md): its responsibilities, stage(s), tools, autonomy considerations, and outputs.

---

## Reporting Issues

Use GitHub Issues to report bugs or request features. For bugs, include:

- A clear title and description.
- Steps to reproduce and expected vs actual behavior.
- Environment (OS, Docker vs native, relevant versions).
- Logs or screenshots where helpful (redact secrets and customer data).

For security vulnerabilities, do **not** open a public issue — see [docs/security-compliance.md](docs/security-compliance.md) for responsible disclosure.

---

Thank you for helping build MyUNO Capital. Every contribution moves solo founders closer to operating like a full team.
