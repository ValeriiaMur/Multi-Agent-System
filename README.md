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
- **[`exercises.json`](./exercises.json)** — the exercise dataset (50 exercises)

## Submitting

Build in a **public** GitHub repo. Include a runnable demo or transcript and a README covering setup. See [`ASSESSMENT.md`](./ASSESSMENT.md) for the complete requirements.

---

## Build (this repo's scaffold)

- **[`PLAN.md`](./PLAN.md)** — phased, test-first work breakdown (router → tools → sub-agents → hub → resilience → UI → all stretch goals).
- **[`AGENTS.md`](./AGENTS.md)** — the red-green-refactor loop and conventions every coding agent must follow (BE + FE).

Layout:

```
backend/app/    hub (router + graph), agents (coach/generator/logger), tools (Pydantic schemas), state, data, stretch stubs
backend/tests/  RED test suite: router, tools, logger, resilience, stretch
frontend/       Vite + React + TS chat UI (RouteBadge, WorkoutCard, LogEntry) with vitest RED tests
data/           exercises.json (50 exercises)
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

## Status

All phases implemented and **green**:

- Backend: `27 passed` (router + threshold, tools, resilience, fuzzy logging, bilateral, observability, the three sub-agent graphs, hub composition, multi-turn memory, response shaping).
- Frontend: `3 passed` (RouteBadge, WorkoutCard, LogEntry).

```bash
cd backend && pytest -q          # 27 passed (excludes @live)
cd frontend && npm test          # 3 passed
```

The LLM is stubbed in tests (deterministic, offline). Live runs use Anthropic via
`app/llm.py`; set `ANTHROPIC_API_KEY` and start `uvicorn app.server:app`.

## Architecture

```
HumanMessage ─▶ router (LLM structured output + confidence threshold)
                 │  confidence < threshold ─▶ CLARIFY
                 ├─ COACH ───────────▶ coach StateGraph
                 ├─ WORKOUT_GENERATE ▶ generator StateGraph: spec → search_exercises → build_workout
                 └─ WORKOUT_LOG ─────▶ logger StateGraph: extract → fuzzy-match catalog
```

Each sub-agent is its own compiled `StateGraph` composed as a node in the hub
(`app/hub/graph.py`), with typed `HubState` and explicit edges. Tools have Pydantic
input schemas. Stretch goals included: streaming SSE (`/chat/stream`), thread-scoped
memory (`app/memory.py`), injury avoidance via `avoid_joints`/`joints_loaded`,
bilateral pairing (`app/bilateral.py`), and structured observability (`app/observability.py`).

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
