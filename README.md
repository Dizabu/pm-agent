# PM Agent

[![CI](https://github.com/Dizabu/pm-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Dizabu/pm-agent/actions/workflows/ci.yml)

A **virtual project manager** AI agent. You chat with it in plain English ("mark the README task as
done"), and it reads and updates the project's tasks through **MCP tools**, streaming every step to a
**React** UI over **server-sent events**. It runs on a local **Ollama** model or on **Claude**, and an
**evaluation pipeline** measures how reliably it does the right thing.

![PM Agent: the chat streams each tool call live, and the task panel refreshes when the agent finishes](docs/screenshot.png)

**Stack:** Python 3.12 · FastAPI · MCP · Ollama · Anthropic API · SSE · React 19 + TypeScript · Vite ·
pytest · ruff · Docker Compose · nginx · GitHub Actions

## Try it in one command

You only need [Docker](https://docs.docker.com/get-docker/).

```bash
git clone https://github.com/Dizabu/pm-agent.git && cd pm-agent
docker compose up --build -d
docker compose exec ollama ollama pull qwen2.5:7b   # one time, ~4.7 GB
```

Open **http://localhost:3000** and try:

- "Create a task called Write the docs"
- "What tasks do I have?"
- "Mark the docs task as done"

> The model runs on your CPU, so an answer can take a minute or two. The UI shows each tool call as it
> happens. To use Claude instead, copy `.env.example` to `.env`, set `LLM_PROVIDER=anthropic` and your
> `ANTHROPIC_API_KEY`, and run `docker compose up --build -d` again.

## How it works

```
Browser ── POST /agent/stream (SSE) ──► nginx ──► FastAPI ──► Agent loop ──► LLMProvider ──► Ollama | Claude
   ▲                                                              │
   │                                                              ▼
   └───────────── GET /tasks ◄───────── TaskStore ◄───── MCP server: list_tasks · create_task · update_task_status
```

1. The user's message goes to the **agent loop** along with the list of tools the **MCP server** exposes.
2. The model either answers or asks for a tool call. The loop runs the tool, feeds the result back, and
   repeats until the model gives a final answer (with a step limit to stop runaway loops).
3. Every step (`tool_call`, `tool_result`, `text`) is **streamed to the browser as an SSE event**, and
   the task panel reloads when the agent finishes.

## Evaluations

Unit tests use scripted fake models, so they prove the **code** is correct but say nothing about whether
the **model** makes good decisions. `backend/evals/` covers that: 8 cases run the real agent against a
real model and are graded on what it **did** (which tools it called, and the final state of the
tasks), never on what it said.

The cases come from real failures found while building it, for example the model **guessing a task id**
instead of looking it up, and **writing a tool call as text** instead of actually calling the tool.

| System prompt | qwen2.5:7b (Ollama) |
|---|---|
| Original: "If you don't know a task's id, call list_tasks first" | 4/8 (50%) |
| Strict: "You MUST call list_tasks before updating a task... Never guess an id" | **8/8 (100%)** |

*(One run per prompt. LLM output varies between runs, so repeated runs are the next step.)*

```bash
cd backend && uv run python -m evals.run    # uses the LLM_PROVIDER from .env
```

## Design decisions

- **Provider abstraction:** every model sits behind one `LLMProvider` interface, chosen from config
  through FastAPI dependency injection, so switching between Ollama, Claude or a fake model needs no code
  changes.
- **Common tool-calling format:** Claude's `tool_use` blocks and Ollama's `tool_calls` are translated
  into one `ToolCall` type, so the agent loop works with either model.
- **Tools through MCP:** the task tools live in an MCP server (`MCPServer` from the official SDK), the
  standard way to expose tools to AI apps. The same server also runs standalone over stdio
  (`python -m app.mcp_server`), so other MCP clients can use it.
- **Errors are data for the model:** tool errors come back to the LLM as text instead of crashing the
  loop, so it can correct itself.
- **One loop, two outputs:** `run_events()` is an async generator. The SSE endpoint streams its events,
  and `run()` reuses it for a plain answer, so the loop logic exists once.
- **Offline, deterministic tests:** fake and scripted LLMs replace the real model in tests, so CI is fast,
  free and doesn't flake. The Claude provider is tested against a mocked SDK client.
- **Configuration from the environment:** the LLM, model, tasks file and log level all come from
  settings, so the same code runs locally and in Docker unchanged.
- **Quality gates in CI:** every push runs ruff + pytest (37 tests) for the backend and lint +
  type-check + build for the frontend.

## Known limitations

- **Tool results are sent back as plain text**, not as each provider's native tool-result messages.
  It keeps the loop provider-independent, but a small model sometimes imitates that text instead of
  calling the tool. Native tool messages are the planned improvement.
- **Tasks are stored in a JSON file**: fine for a single user, not for concurrent writers.
- **No authentication**: it's meant to run locally.

## Local development

```bash
cp .env.example .env

# Terminal 1: backend
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8001   # API docs: http://localhost:8001/docs
uv run pytest

# Terminal 2: frontend (Node 22+)
cd frontend
npm install
npm run dev                                         # Vite proxies /agent and /tasks to :8001
```

```
backend/
  app/          FastAPI app, agent loop, LLM providers, MCP server, task store
  tests/        pytest suite (fake and scripted LLMs)
  evals/        eval cases, grader and runner
frontend/       React + TypeScript chat UI (Vite in development, nginx in Docker)
docker-compose.yml
```

## Author

**Diego Zamora Bustos**: [GitHub](https://github.com/Dizabu) · [LinkedIn](https://www.linkedin.com/in/diego-zamora-a91b53429)
