from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from app.agent import Agent
from app.config import settings
from app.llm import get_provider
from app.llm.base import LLMProvider, Message
from app.mcp_server import create_server
from app.task import TaskStore

app = FastAPI(title="PM Agent")


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


def get_agent(llm: Annotated[LLMProvider, Depends(get_provider)]) -> Agent:
    """Build an agent with the configured LLM and the real tasks file."""
    store = TaskStore(Path(settings.tasks_file))
    return Agent(llm, create_server(store))


@app.post("/agent", response_model=ChatResponse)
async def agent(req: ChatRequest, agent: Annotated[Agent, Depends(get_agent)]) -> ChatResponse:
    reply = await agent.run(req.message)
    return ChatResponse(reply=reply)
