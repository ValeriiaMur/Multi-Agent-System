# Multi-Agent System — Take-Home

**Time:** 2–3 hours · **Stack:** Python, LangGraph, LangChain, any LLM provider

Build a hub agent that routes user requests to specialized sub-agents using LangGraph. The router classifies intent with LLM structured output and dispatches to a coach, a workout generator, or a workout logger.

| Route | Example |
|-------|---------|
| `COACH` | "What muscles does a deadlift work?" |
| `WORKOUT_GENERATE` | "Build me a 30 min upper body session with dumbbells" |
| `WORKOUT_LOG` | "I just did 3x10 bench press at 185 lbs" |

## Files

- **[`ASSESSMENT.md`](./ASSESSMENT.md)** — the full prompt: task, requirements, stretch goals
- **[`backend/data/exercises.json`](./backend/data/exercises.json)** — the exercise dataset (50 exercises), single source of truth (override with `EXERCISES_PATH`)

## Submitting

Build in a **public** GitHub repo. Include a runnable demo or transcript and a README covering setup. See [`ASSESSMENT.md`](./ASSESSMENT.md) for the complete requirements.

---

## Build (this repo's scaffold)

- **[`PLAN.md`](./PLAN.md)** — phased, test-first work breakdown (router → tools → sub-agents → hub → resilience → UI → all stretch goals).
- **[`AGENTS.md`](./AGENTS.md)** — the red-green-refactor loop and conventions every coding agent must follow (BE + FE).

Layout:

```
backend/app/    hub (router + graph), agents (coach/generator/logger), tools (schemas + search/build/normalize),
                evals (routing golden set), security (API key + rate limit), state, shaping, llm, memory, observability
backend/tests/  router, tools, logger, resilience, graphs, normalize, context, evals, security, coach grounding
frontend/       Vite + React + TS + Tailwind chat UI ("Future Coach", iMessage-style): live SSE streaming,
                route badge + agent trace, workout/log cards, grounded coach references, 👍/👎→LangSmith; vitest tests
backend/data/   exercises.json (50 exercises) — the dataset (single source of truth)
```

Run:

```bash
# backend
pip install -e ".[dev]"          # needs langgraph/langchain/anthropic
cp .env.example .env             # add ANTHROPIC_API_KEY
pytest -q                        # excludes @live tests by default
uvicorn app.server:app --reload --app-dir backend

# frontend
cd frontend && npm install && npm test   # vitest
npm run dev
```

## Deployment (Railway)

Two services — a static frontend and the FastAPI backend — each deployed from `main`.

- **Frontend:** `https://multi-agent-system.up.railway.app`
- **Backend:** `https://multi-agent-system-be-production.up.railway.app` (`/healthz` for liveness)

Env vars (set in the respective Railway service; build the frontend after changing its vars,
since Vite inlines `VITE_*` at build time):

| Service | Variable | Purpose |
|---|---|---|
| frontend | `VITE_API_BASE` | Backend public URL (same-origin if unset; needed in prod) |
| frontend | `VITE_API_KEY` | Optional shared secret, sent as `X-API-Key` (must match backend) |
| backend | `ANTHROPIC_API_KEY` | LLM key (required) |
| backend | `LLM_MODEL` / `ROUTER_MODEL` | Global model + per-role overrides (router → Sonnet, rest → Haiku) |
| backend | `ALLOWED_ORIGINS` | CORS allowlist; set to the frontend origin in prod |
| backend | `API_KEY` | Optional shared secret enforced on `/chat`, `/feedback`, `/chat/stream` |
| backend | `RATE_LIMIT_PER_MIN` | Per-IP rate limit (default 30; `0` disables) |
| backend | `LANGSMITH_TRACING` / `LANGSMITH_API_KEY` | Enable tracing + 👍/👎 feedback |
| backend | `EXERCISES_PATH` | Override the dataset path (defaults to `backend/data/exercises.json`) |

> Note: an API key baked into a browser bundle is readable by anyone — it raises the bar
> but isn't real auth. The real protection is CORS locked to the frontend origin + rate limiting.

## Status

All phases implemented and **green**:

- Backend: `63 passed` (router + threshold + context, tools + vocab normalization, resilience, fuzzy logging,
  bilateral, observability + feedback, the three sub-agent graphs, hub composition, multi-turn memory,
  response shaping, coach grounding, routing-eval harness, API-key/rate-limit security).
- Frontend: `11 passed` (route badge, workout/log cards, viewport, components).

```bash
cd backend && pytest -q          # 63 passed (excludes @live)
cd frontend && npm test          # 11 passed
```

The LLM is stubbed in tests (deterministic, offline). Live runs use Anthropic via
`app/llm.py`; set `ANTHROPIC_API_KEY` and start `uvicorn app.server:app`.

### Live demo & golden tests

```bash
cd backend
export ANTHROPIC_API_KEY=sk-ant-...
python -m scripts.demo        # runs all three routes + an ambiguous (CLARIFY) case
python -m scripts.eval_routing  # scores the router on the golden set (exits non-zero below floor)
pytest -m live                # golden tests against the real model (skipped without a key)
```

### Routing evals

Routing is the highest-leverage decision (a silent misroute is the worst
failure), so it has a labeled golden set and a scoring harness in
[`app/evals/routing.py`](backend/app/evals/routing.py). The dataset covers every
route, the "act over clarify" cases (e.g. `"next workout"` → `WORKOUT_GENERATE`),
the CLARIFY safety net (`"bench press"` alone), and **context-dependent
follow-ups** (`"make it harder"` after a generated workout). The harness is
provider-agnostic — pass any `route_fn(messages) -> route`.

- Offline (`test_evals.py`): self-tests the harness + asserts dataset coverage — runs in the default suite.
- Live (`test_routing_accuracy_live`, marked `@live`): runs the real router over the set and asserts accuracy ≥ 0.8. Run with `pytest -m live` or `python -m scripts.eval_routing` (the latter can gate CI).

### Observability (LangSmith)

LangChain auto-traces LLM calls and graph nodes; the tools (`search_exercises`,
`build_workout`, `fuzzy_match_exercise`) are wrapped with a `@traced` decorator
(`app/observability.py`) so tool invocations appear as nested spans. Enable it:

```bash
export LANGCHAIN_TRACING_V2=true LANGCHAIN_API_KEY=lsv2_... LANGCHAIN_PROJECT=fitness-coach-agents
```

`@traced` is a no-op when `langsmith` isn't installed, so the offline test suite
stays deterministic. A `log_event()` helper also emits structured JSON lines as a
local, always-on fallback. (`LANGSMITH_TRACING` and the legacy `LANGCHAIN_TRACING_V2`
are both honored.)

**Feedback loop:** the UI's 👍/👎 posts to `POST /feedback` with the turn's `run_id`
(captured server-side via `collect_runs`), which `submit_feedback()` records as
LangSmith run feedback — so you can score real conversations in the trace UI. It's a
graceful no-op when tracing/langsmith isn't configured.

## Architecture

```
HumanMessage ─▶ router (LLM structured output + confidence threshold + recent context)
                 │  confidence < threshold ─▶ CLARIFY
                 ├─ COACH ───────────▶ coach StateGraph: retrieve catalog context → grounded answer + references
                 ├─ WORKOUT_GENERATE ▶ generator StateGraph: spec → normalize → search_exercises → build_workout
                 └─ WORKOUT_LOG ─────▶ logger StateGraph: extract → fuzzy-match catalog
```

Each sub-agent is its own compiled `StateGraph` composed as a node in the hub
(`app/hub/graph.py`), with typed `HubState` and explicit edges. Tools have Pydantic
input schemas. Highlights beyond the base task:

- **Grounding everywhere** — generate/log/coach all run over the real `exercises.json`
  (validated IDs, fuzzy match, retrieved context + `references`); nothing is invented.
- **Per-agent models** — routing runs on a stronger model (Sonnet) for intent quality;
  prose/extraction run on Haiku for speed/cost (`get_model(role)`, env-overridable).
- **Context-aware routing** — the router sees recent turns, so follow-ups ("make it
  harder") resolve correctly; a labeled **routing eval** harness guards quality.
- **Vocab normalization** (`tools/normalize.py`) — maps loose LLM output ("upper body",
  "dumbbells") onto the dataset's exact names; benches/racks are ambient so sessions fill out.
- **Live streaming to the UI** — SSE (`/chat/stream`) emits `meta` (route) → `token`*
  (prose) → `final` (payload + `run_id`); the React app renders it in real time.
- **Feedback loop** — 👍/👎 in the UI posts to `/feedback`, recorded as LangSmith run feedback.
- **Hardening** — env-driven CORS lockdown, per-IP rate limit, optional `X-API-Key`.
- Plus thread-scoped memory (`app/memory.py`), injury avoidance, bilateral pairing
  (`app/bilateral.py`), and structured observability (`app/observability.py`).

## Critical paths chosen to test

1. **Router classification + low-confidence fallback** (`test_router.py`, `test_graphs.py::test_hub_clarifies_on_low_confidence`) — routing gates the whole system; a silent misroute is the worst failure, so ambiguous inputs must fall back to CLARIFY rather than guess.
2. **Workout-generator resilience** (`test_resilience.py`, `test_graphs.py::test_generator_recovers_on_no_results`) — tool-calling is where crashes and hallucination are most likely; empty search results and invalid exercise IDs must recover without inventing data.

## How I would evaluate this system in production

**Routing quality** is the top metric. I'd track the router's confidence distribution
and the CLARIFY rate over time: a rising CLARIFY rate signals drift or a new class of
inputs, while overconfident misroutes are the dangerous case. I'd sample real
conversations and label the correct route to compute routing precision/recall per
class, and alert if accuracy on a held-out labeled set drops below threshold.

**Tool and grounding integrity.** Every generated workout should reference only real
exercise IDs — I'd assert this server-side and count any fabricated-ID attempts as a
hard failure metric (it should be zero because `build_workout` validates IDs, but
monitoring catches regressions). For the logger, I'd track the fuzzy-match rate and the
distribution of match scores; a spike in unmatched entries means the matcher or the
catalog needs attention.

**Failure modes to monitor:** empty `search_exercises` results (is equipment filtering
too strict?), invalid tool calls caught by the recovery path, LLM timeouts/errors,
and structured-output parse failures. All of these are emitted as structured log events
(`app/observability.py`), so they're countable and alertable; in production I'd export
them to Langfuse/OTel and build a dashboard of route mix, tool latency, recovery
events, and per-route token cost.

**How I'd know it's working:** low and stable CLARIFY/misroute rates, zero fabricated
exercise IDs, high logger match rate, recovery paths firing rarely, and p95 latency and
cost per turn within budget. I'd add a small golden-transcript suite run in CI against
the live model (the `@live` marker) so behavioral regressions surface before release.
