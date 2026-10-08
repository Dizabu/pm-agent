from dataclasses import dataclass
from typing import Protocol


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class LLMProvider(Protocol):
    """Every provider (Anthropic, Ollama, Fake) implements this same interface,
    so the rest of the app never needs to know which LLM is behind it."""

    async def complete(self, messages: list[Message], system: str = "") -> str: ...
