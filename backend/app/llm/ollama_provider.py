import httpx

from app.config import settings
from app.llm.base import LLMResponse, Message, ToolCall, ToolSpec


class OllamaProvider:
    """Calls a local Ollama API through its HTTP API."""

    def build_messages(self, messages: list[Message], system: str = "") -> list[dict]:
        ollama_messages = []
        if system:
            messages = [Message(role="system", content=system)] + messages
        ollama_messages.extend([m.to_dict() for m in messages])
        return ollama_messages

    async def _send(self, payload: dict) -> dict:
        """POST a payload to Ollama's chat endpoint and return the reply's message."""
        async with httpx.AsyncClient(timeout=150) as client:
            response = await client.post(f"{settings.ollama_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()["message"]

    async def complete(self, messages: list[Message], system: str = "") -> str:
        payload = {
            "model": settings.ollama_model,
            "messages": self.build_messages(messages, system),
            "stream": False,
        }
        message = await self._send(payload)
        return message["content"]

    async def chat(
        self, messages: list[Message], system: str = "", tools: list[ToolSpec] | None = None
    ) -> LLMResponse:
        payload = {
            "model": settings.ollama_model,
            "messages": self.build_messages(messages, system),
            "stream": False,
        }
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.input_schema,
                    },
                }
                for t in tools
            ]

        message = await self._send(payload)

        tool_calls = [
            ToolCall(
                id=call.get("id", ""),
                name=call["function"]["name"],
                arguments=call["function"]["arguments"],
            )
            for call in message.get("tool_calls", [])
        ]
        return LLMResponse(text=message.get("content", ""), tool_calls=tool_calls)
