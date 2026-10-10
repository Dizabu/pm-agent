from anthropic import AsyncAnthropic

from app.config import settings
from app.llm.base import LLMResponse, Message, ToolCall, ToolSpec


class AnthropicProvider:
    """Calls Claude through the official Anthropic SDK."""
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    def _build_payload(self, messages: list[Message], system: str) -> dict:
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": settings.anthropic_max_tokens,
            "messages": [m.to_dict() for m in messages],
        }
        if system:
            payload["system"] = system
        return payload

    async def complete(self, messages: list[Message], system: str = "") -> str:
        payload = self._build_payload(messages, system)
        response = await self.client.messages.create(**payload)
        return response.content[0].text

    async def chat(
        self, messages: list[Message], system: str = "", tools: list[ToolSpec] | None = None
    ) -> LLMResponse:
        payload = self._build_payload(messages, system)
        if tools:
            payload["tools"] = [t.to_dict() for t in tools]

        response = await self.client.messages.create(**payload)

        text = "".join(block.text for block in response.content if block.type == "text")
        tool_calls = [
            ToolCall(id=block.id, name=block.name, arguments=block.input)
            for block in response.content
            if block.type == "tool_use"
        ]
        return LLMResponse(text=text, tool_calls=tool_calls)
