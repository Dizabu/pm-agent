from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from app.llm import get_provider
from app.llm.base import LLMProvider, Message

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
