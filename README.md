# PM Agent

[![CI](https://github.com/Dizabu/pm-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Dizabu/pm-agent/actions/workflows/ci.yml)

A **virtual project manager** AI agent. The goal: you chat with it, and it reads and updates a project's
tasks through **MCP tools**, streams its answers to a **React** UI over **server-sent events**, and is
checked by an **evaluation pipeline** in CI. It runs on **Claude** (Anthropic API) or a local **Ollama** model.

> 🚧 **Work in progress.** The backend and both LLM providers work today; the tool-calling agent,
> streaming UI and evals are being built next (see [Status](#status)).

**Stack:** Python 3.12 · FastAPI · Anthropic API · Ollama · pytest · ruff · GitHub Actions
*(planned: MCP · SSE · React + TypeScript · Docker)*

## Run it

```bash
cp .env.example .env          # set LLM_PROVIDER (fake | anthropic | ollama) and keys
cd backend
uv sync
uv run uvicorn app.main:app --reload    # http://localhost:8000/docs
uv run pytest                            # tests use a fake LLM: free and offline
```

## Architecture

```
React UI  --(POST /chat, SSE stream)-->  FastAPI backend  -->  Agent loop  -->  LLMProvider (Claude | Ollama | Fake)
                                                                    |
                                                                    +--> MCP client --> MCP server (task tools) --> tasks.json
```

**Design decisions so far**

- **Provider abstraction:** every model sits behind one `LLMProvider` interface, chosen from config through
  FastAPI dependency injection, so switching between Claude, Ollama or a fake model needs no code changes.
- **Offline, deterministic tests:** a `FakeProvider` replaces the real model in tests, so CI is fast, free
  and doesn't flake on network calls.
- **Quality gates in CI:** every push runs ruff and pytest on GitHub Actions.

## Status

| Area | State |
|---|---|
| FastAPI app (`/health`, `/chat`), config from environment | ✅ Done |
| `LLMProvider` interface, `FakeProvider`, pytest + ruff + CI | ✅ Done |
| Claude provider (`AsyncAnthropic`) and Ollama provider (`httpx`) | ✅ Done |
| MCP server with task tools (`list_tasks`, `create_task`, `update_task_status`, `summarize_project`) and the agent loop | 🚧 In progress |
| `POST /chat/stream` with server-sent events | Planned |
| React + TypeScript chat UI with a live task panel | Planned |
| Evaluation pipeline (`evals/cases.jsonl`, scored in CI) | Planned |
| Structured logging, Docker / docker-compose | Planned |

## Author

**Diego Zamora Bustos**: [GitHub](https://github.com/Dizabu) · [LinkedIn](https://www.linkedin.com/in/diego-zamora-a91b53429)
