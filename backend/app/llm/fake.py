from app.llm.base import LLMResponse, Message, ToolSpec


class FakeProvider:
    """Deterministic provider for tests and CI: no network, no API key, no cost."""

    async def complete(self, messages: list[Message], system: str = "") -> str:
        return f"echo: {messages[-1].content}"

    async def chat(
        self, messages: list[Message], system: str = "", tools: list[ToolSpec] | None = None
    ) -> LLMResponse:
        return LLMResponse(text=f"echo: {messages[-1].content}")
