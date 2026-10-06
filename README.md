# PM Agent

A small **virtual project manager** AI agent. You chat with it, and it reads and updates a project's tasks
through **MCP tools**, streams its answers to a **React** UI over **server-sent events**, and is checked by an
**evaluation pipeline** in CI. It works with **Claude** or a local **Ollama** model.

Stack: Python 3.12 · FastAPI · Anthropic API / Ollama · MCP · SSE · React + TypeScript · pytest · GitHub Actions · Docker

## Run it

```bash
cp .env.example .env          # pick LLM_PROVIDER and fill in keys
cd backend
uv sync
uv run uvicorn app.main:app --reload    # http://localhost:8000/docs
uv run pytest                            # tests use a fake LLM: free and offline
```

## Architecture

```
React UI  --(POST /chat, SSE stream)-->  FastAPI backend  -->  Agent loop  -->  LLM provider (Claude | Ollama)
                                                                    |
                                                                    +--> MCP client --> MCP server (task tools) --> tasks.json
```

## Roadmap

Rough estimate: **25-35 hours** in total (about 2-3 weeks at 2 hours/day). Commit and push after each step.

### Phase 0 - Setup (done)
- [x] FastAPI app with `/health` and `/chat`
- [x] `LLMProvider` interface + `FakeProvider` for tests
- [x] pytest + ruff + GitHub Actions CI

### Phase 1 - Real LLM calls (~4-5 h)
- [ ] `app/llm/anthropic_provider.py`: implement `complete()` with the `anthropic` SDK (`AsyncAnthropic`)
- [ ] `app/llm/ollama_provider.py`: implement `complete()` with `httpx` against Ollama's `/api/chat`
- [ ] Wire both into `get_provider()` and try `/chat` from `/docs`
- [ ] Add a system prompt: "You are a project manager assistant..."
- [ ] Test: provider selection from settings (no real API calls in tests)

### Phase 2 - Tools via MCP (~7-9 h), the core of the project
- [ ] `mcp_server/`: a small MCP server (official `mcp` Python SDK, `FastMCP`) exposing
      `list_tasks`, `create_task`, `update_task_status`, `summarize_project` over a `tasks.json` file
- [ ] Unit tests for each tool
- [ ] Extend `LLMProvider` with tool calling (Claude: `tools=`, Ollama: `tools` in `/api/chat`)
- [ ] `app/agent.py`: the agent loop - send message -> model asks for a tool -> call it through the
      MCP client -> send the result back -> repeat until the model answers
- [ ] Limit the loop (max steps) and handle tool errors gracefully

### Phase 3 - Streaming with SSE (~3-4 h)
- [ ] `POST /chat/stream` returning `StreamingResponse` with `text/event-stream`
- [ ] Events as JSON: `{"type": "text", ...}`, `{"type": "tool_call", ...}`, `{"type": "done"}`
- [ ] Test the stream with `curl -N`

### Phase 4 - React frontend (~6-8 h)
- [ ] `frontend/` with Vite + React + TypeScript
- [ ] Chat UI that reads the SSE stream (`fetch` + `ReadableStream`) and renders text as it arrives
- [ ] Show tool calls in the chat ("Created task: Fix login bug")
- [ ] A side panel with the current task list
- [ ] Basic accessibility: labels, keyboard navigation, focus states

### Phase 5 - Evaluation pipeline (~4-5 h)
- [ ] `evals/cases.jsonl`: ~20 prompts with expected behavior
      (e.g. "Add a task to write docs" -> must call `create_task`)
- [ ] `evals/run.py`: runs each case, checks tool calls and output, prints a score and saves a report
- [ ] Run a cheap subset in CI so a prompt change that breaks behavior fails the build

### Phase 6 - Production polish (~3-4 h)
- [ ] Structured logging (JSON logs, one request id per chat, log every tool call)
- [ ] `Dockerfile` + `docker-compose.yml` (backend + frontend, optional Ollama)
- [ ] Secrets only from environment variables, never in code
- [ ] README: screenshot/GIF, architecture diagram, what you learned
- [ ] Optional: deploy (Render/Fly.io/Azure) or a short Terraform file for the cloud setup

## How this maps to the Moody's posting

| They ask for | Where it is |
|---|---|
| Python, tested and reviewed code | backend + pytest + CI |
| LLM services, prompt design, evaluating output | Phases 1, 2, 5 |
| FastAPI | backend |
| MCP tool integrations | Phase 2 |
| SSE streaming to React | Phases 3, 4 |
| Evaluation pipelines that catch regressions | Phase 5 |
| CI/CD, logging, containers, IaC | Phase 6 |
