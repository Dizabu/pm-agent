from app.llm.base import Message
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
