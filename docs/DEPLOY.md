# Deploying to Railway

Two services in one Railway project, both deploying from the same public GitHub
repo: a **backend** (FastAPI/uvicorn) and a **frontend** (Vite build served as
static files). They are distinguished by their **Root Directory**.

## Prerequisites

- Repo pushed to a public GitHub repo.
- An Anthropic API key. Optional: LangSmith key for tracing.

---

## Service 1 — Backend (FastAPI)

In Railway: **New Project → Deploy from GitHub repo**, then in the created
service open **Settings**:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Builder | Nixpacks (auto) |
| Install | `pip install -r requirements.txt` (auto-detected) |
| Start Command | `uvicorn app.server:app --host 0.0.0.0 --port $PORT` |
| Healthcheck Path | `/healthz` |

(The Start Command and healthcheck are already declared in `backend/railway.json`
and `backend/Procfile`, so Railway picks them up automatically — you don't have to
type them in unless you want to override.)

**Variables** (Settings → Variables):

```
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-latest
ROUTER_CONFIDENCE_THRESHOLD=0.6
# optional tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=fitness-coach-agents
# optional hardening
ALLOWED_ORIGINS=https://your-frontend.up.railway.app   # default "*"
CHECKPOINT_DB=/data/memory.sqlite                       # durable memory (needs a volume); default in-memory
```

> For durable memory across redeploys, set `CHECKPOINT_DB` to a path on a mounted
> Railway **Volume** and add `langgraph-checkpoint-sqlite` to requirements. Without
> a volume the file is ephemeral; without the package it safely falls back to
> in-memory.

Then **Settings → Networking → Generate Domain**. Note the URL, e.g.
`https://fitness-be-production.up.railway.app`. Verify it: opening `/docs` should
show the FastAPI Swagger page.

> `$PORT` is injected by Railway — do not hardcode a port. The app binds `0.0.0.0`.

---

## Service 2 — Frontend (Vite static)

In the same project: **New → GitHub Repo** (select the same repo again), then
**Settings**:

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Builder | Nixpacks (auto) |
| Build | `npm install && npm run build` (auto) |
| Start Command | `serve -s dist -l $PORT` |

(Declared in `frontend/railway.json` + `frontend/Procfile`; `serve` is a runtime
dependency so it's available after build.)

**Variables** — point the UI at the backend's public URL. This is read at
**build time** by Vite, so set it before the build runs:

```
VITE_API_BASE=https://fitness-be-production.up.railway.app
```

Then **Generate Domain** for the frontend too. Open it and send a message — it
calls `${VITE_API_BASE}/chat`.

> If you change `VITE_API_BASE` later, trigger a **redeploy** so Vite re-inlines it.

---

## CORS

The backend already allows all origins (`allow_origins=["*"]` in
`app/server.py`), so the frontend domain works out of the box. To lock it down,
replace `"*"` with your frontend's Railway URL.

## Deploy from the CLI instead (optional)

```bash
npm i -g @railway/cli
railway login
railway link            # select the project
# backend
cd backend && railway up --service <backend-service>
# frontend
cd ../frontend && railway up --service <frontend-service>
```

## Troubleshooting

- **Backend build has no deps** — ensure `backend/requirements.txt` exists (it does); Nixpacks installs from it.
- **`exercises.json` not found** — the dataset ships at `backend/data/exercises.json` and `app/data.py` resolves it relative to the package, or via the `EXERCISES_PATH` env var.
- **Frontend calls localhost / 404 on /chat** — `VITE_API_BASE` wasn't set at build time; set it and redeploy.
- **Healthcheck failing** — confirm the start command uses `$PORT` and host `0.0.0.0`.
