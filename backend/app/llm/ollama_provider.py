import httpx

from app.config import settings
from app.llm.base import Message


class OllamaProvider:
    """Calls a local Ollama API through its HTTP API."""

    def build_messages(self, messages: list[Message], system: str = "") -> list[dict]:
        ollama_messages = []
        if system:
            messages = [Message(role="system", content=system)] + messages
        ollama_messages.extend(
            [m.to_dict() for m in messages]
        )
        return ollama_messages

    async def complete(self, messages: list[Message], system: str = "") -> str:
        payload = {
            "model": settings.ollama_model,
            "messages": self.build_messages(messages, system),
            "stream": False,
        }
        base_url = getattr(
            settings,
            "ollama_base_url",
            getattr(settings, "ollama_url", "http://localhost:11434"),
        )

        async with httpx.AsyncClient(timeout=150) as client:
            response = await client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        