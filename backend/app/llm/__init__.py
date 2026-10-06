from app.config import settings
from app.llm.base import LLMProvider
from app.llm.fake import FakeProvider


def get_provider() -> LLMProvider:
    match settings.llm_provider:
        case "fake":
            return FakeProvider()
        case "anthropic":
            # TODO (Phase 1): return AnthropicProvider() from app/llm/anthropic_provider.py
            raise NotImplementedError("Anthropic provider not implemented yet")
        case "ollama":
            # TODO (Phase 1): return OllamaProvider() from app/llm/ollama_provider.py
            raise NotImplementedError("Ollama provider not implemented yet")
