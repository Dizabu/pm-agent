import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import Message


def make_provider(reply_text: str) -> AnthropicProvider:
    """An AnthropicProvider whose client is a fake that always answers reply_text."""
    fake_response = SimpleNamespace(content=[SimpleNamespace(text=reply_text)])
    provider = AnthropicProvider()
    provider.client = SimpleNamespace(
        messages=SimpleNamespace(create=AsyncMock(return_value=fake_response))
    )
    return provider


def test_complete_returns_text():
    provider = make_provider("Hi from Claude")
    reply = asyncio.run(provider.complete([Message(role="user", content="hi")]))
    assert reply == "Hi from Claude"


def test_system_is_sent_separately():
    provider = make_provider("ok")
    asyncio.run(provider.complete([Message(role="user", content="hi")], system="You are a PM"))
    sent = provider.client.messages.create.call_args.kwargs
    assert sent["system"] == "You are a PM"
    assert sent["messages"] == [{"role": "user", "content": "hi"}]


def test_no_system_key_when_empty():
    provider = make_provider("ok")
    asyncio.run(provider.complete([Message(role="user", content="hi")], system=""))
    sent = provider.client.messages.create.call_args.kwargs
    assert "system" not in sent
