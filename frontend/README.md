# MyUNO Capital — Founder Console (Frontend)

The Next.js 14 (App Router) frontend for MyUNO Capital, the Autonomous AI OS
for solo entrepreneurs. It consumes the FastAPI backend described in
[`../docs/api-reference.md`](../docs/api-reference.md).

## Stack

- Next.js 14 (App Router) + React 18 + TypeScript
- Tailwind CSS (dark console theme)
- Client-side JWT auth (access token in `localStorage`)
- Vitest for unit tests

## Configuration

The backend base URL is read from `NEXT_PUBLIC_API_URL` (e.g.
`http://localhost:8000`). All requests go to `${NEXT_PUBLIC_API_URL}/api/v1/...`.

## Scripts

| Command          | Description                                  |
| ---------------- | -------------------------------------------- |
| `npm run dev`    | Dev server on `0.0.0.0:3000`                 |
| `npm run build`  | Production build (also type-checks + lints)  |
| `npm run start`  | Serve the production build                   |
| `npm run lint`   | ESLint (next/core-web-vitals)                |
| `npm test`       | Run the Vitest unit tests                    |
| `npm run format` | Format the codebase with Prettier            |

## Running with Docker Compose

From the repository root:

```bash
cp .env.example .env   # set NEXT_PUBLIC_API_URL etc.
docker compose up
```

The frontend service builds from `./frontend/Dockerfile`, listens on port 3000,
and boots `npm run dev` (no separate build step needed to run).

## Structure

- `app/` — routes. Public: `/login`, `/register`. Authenticated console shell
  under the `(console)` route group: dashboard, businesses (+ detail and
  decision hub), agents, integrations, activity.
- `components/` — reusable UI (Sidebar, Topbar, MetricCard, ScoreBadge,
  OptionsTable, AgentCard, Gauge, EmptyState, Spinner, ...).
- `lib/` — `api.ts` (typed fetch client, JWT + 401 handling), `auth.ts` (token
  storage), `types.ts` (API types), `score.ts` / `format.ts` (pure helpers).
- `__tests__/` — unit tests for the score color logic and formatting helpers.

All pages handle loading, error, and empty states and do not crash when the
backend is unreachable.
