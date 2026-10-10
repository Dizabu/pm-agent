import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import Message, ToolCall, ToolSpec


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


def make_chat_provider(*blocks) -> AnthropicProvider:
    """An AnthropicProvider whose fake Claude answers with the given content blocks."""
    provider = AnthropicProvider()
    fake_response = SimpleNamespace(content=list(blocks))
    provider.client = SimpleNamespace(
        messages=SimpleNamespace(create=AsyncMock(return_value=fake_response))
    )
    return provider


CREATE_TASK = ToolSpec(
    name="create_task",
    description="Create a task",
    input_schema={"type": "object", "properties": {"title": {"type": "string"}}},
)


def test_chat_sends_tools_in_claude_format():
    provider = make_chat_provider(SimpleNamespace(type="text", text="ok"))
    asyncio.run(provider.chat([Message(role="user", content="hi")], tools=[CREATE_TASK]))
    sent = provider.client.messages.create.call_args.kwargs
    assert sent["tools"] == [CREATE_TASK.to_dict()]


def test_chat_separates_text_and_tool_calls():
    provider = make_chat_provider(
        SimpleNamespace(type="text", text="Sure, I'll create it."),
        SimpleNamespace(
            type="tool_use", id="toolu_01", name="create_task", input={"title": "Write README"}
        ),
    )
    response = asyncio.run(
        provider.chat([Message(role="user", content="add a task")], tools=[CREATE_TASK])
    )
    assert response.text == "Sure, I'll create it."
    assert response.tool_calls == [
        ToolCall(id="toolu_01", name="create_task", arguments={"title": "Write README"})
    ]
