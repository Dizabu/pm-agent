from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMProvider(Protocol):
    """Every provider (Anthropic, Ollama, Fake) implements this same interface,
    so the rest of the app never needs to know which LLM is behind it."""

    async def complete(self, messages: list[Message], system: str = "") -> str: ...

    async def chat(
        self, messages: list[Message], system: str = "", tools: list[ToolSpec] | None = None
    ) -> LLMResponse: ...
