import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent import Agent
from app.config import settings
from app.llm import get_provider
from app.llm.base import LLMProvider, Message
from app.mcp_server import create_server
from app.task import TaskStore
import logging


app = FastAPI(title="PM Agent")




logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest, llm: Annotated[LLMProvider, Depends(get_provider)]
) -> ChatResponse:
    reply = await llm.complete([Message(role="user", content=req.message)])
    return ChatResponse(reply=reply)


def get_store() -> TaskStore:
    """The real task store, from the configured file."""
    return TaskStore(Path(settings.tasks_file))


def get_agent(
    llm: Annotated[LLMProvider, Depends(get_provider)],
    store: Annotated[TaskStore, Depends(get_store)],
) -> Agent:
    return Agent(llm, create_server(store))


@app.post("/agent", response_model=ChatResponse)
async def agent(req: ChatRequest, agent: Annotated[Agent, Depends(get_agent)]) -> ChatResponse:
    reply = await agent.run(req.message)
    return ChatResponse(reply=reply)


@app.post("/agent/stream")
async def agent_stream(
    req: ChatRequest, agent: Annotated[Agent, Depends(get_agent)]
) -> StreamingResponse:
    async def sse():
        async for event in agent.run_events(req.message):
            yield f"data: {json.dumps(event)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")


@app.get("/tasks")
async def list_tasks(store: Annotated[TaskStore, Depends(get_store)]) -> list[dict]:
    return [asdict(t) for t in store.list_tasks()]
