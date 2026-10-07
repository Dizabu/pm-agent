from app.llm.base import Message
from app.llm.ollama_provider import OllamaProvider


def test_build_messages_with_system():
    provider = OllamaProvider()
    result = provider.build_messages([Message(role="user", content="bye")], system="You are a PM")
    assert result == [
        {"role": "system", "content": "You are a PM"},
        {"role": "user", "content": "bye"},
    ]


def test_build_messages_without_system():
    provider = OllamaProvider()
    result = provider.build_messages([Message(role="user", content="hi")])
    assert result == [{"role": "user", "content": "bye"}]
    """I dont get it how iam able to know if the message has no system systme is given in the build messages??"""