from app.llm.base import Message


class FakeProvider:
    """Deterministic provider for tests and CI: no network, no API key, no cost."""

    async def complete(self, messages: list[Message], system: str = "") -> str:
        return f"echo: {messages[-1].content}"
