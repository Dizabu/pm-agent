import asyncio
from unittest.mock import AsyncMock

from app.llm.base import Message, ToolCall, ToolSpec
from app.llm.ollama_provider import OllamaProvider


def test_build_messages_with_system():
    provider = OllamaProvider()
    result = provider.build_messages([Message(role="user", content="hi")], system="You are a PM")
    assert result == [
        {"role": "system", "content": "You are a PM"},
        {"role": "user", "content": "hi"},
    ]


def test_build_messages_without_system():
    provider = OllamaProvider()
    result = provider.build_messages([Message(role="user", content="hi")])
    assert result == [{"role": "user", "content": "hi"}]


CREATE_TASK = ToolSpec(
    name="create_task",
    description="Create a task",
    input_schema={"type": "object", "properties": {"title": {"type": "string"}}},
)


def make_chat_provider(reply_message: dict) -> OllamaProvider:
    """An OllamaProvider whose _send returns reply_message instead of calling Ollama."""
    provider = OllamaProvider()
    provider._send = AsyncMock(return_value=reply_message)
    return provider


def test_chat_sends_tools_in_ollama_format():
    provider = make_chat_provider({"role": "assistant", "content": "ok"})
    asyncio.run(provider.chat([Message(role="user", content="hi")], tools=[CREATE_TASK]))
    sent = provider._send.call_args.args[0]
    assert sent["tools"] == [
        {
            "type": "function",
            "function": {
                "name": CREATE_TASK.name,
                "description": CREATE_TASK.description,
                "parameters": CREATE_TASK.input_schema,
            },
        }
    ]


def test_chat_reads_tool_calls():
    provider = make_chat_provider(
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {"name": "create_task", "arguments": {"title": "Write README"}},
                }
            ],
        }
    )
    response = asyncio.run(
        provider.chat([Message(role="user", content="add a task")], tools=[CREATE_TASK])
    )
    assert response.tool_calls == [
        ToolCall(id="call_1", name="create_task", arguments={"title": "Write README"})
    ]


def test_chat_with_only_text_has_no_tool_calls():
    provider = make_chat_provider({"role": "assistant", "content": "Hello!"})
    response = asyncio.run(provider.chat([Message(role="user", content="hi")]))
    assert response.text == "Hello!"
    assert response.tool_calls == []
