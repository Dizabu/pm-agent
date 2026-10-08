from anthropic import AsyncAnthropic

from app.config import settings
from app.llm.base import Message


class AnthropicProvider:
    """Calls a local Anthropic API through its HTTP API."""   

    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(self, messages: list[Message], system: str = "") -> str:
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": settings.anthropic_max_tokens,
            "messages": [m.to_dict() for m in messages],
        }
        if system:
            payload["system"] = system

        response = await self.client.messages.create(**payload)
        return response.content[0].text
    

    
