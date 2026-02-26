from app.config import settings
from app.services.llm.base import LLMProvider


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        from app.services.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    from app.services.llm.ollama_provider import OllamaProvider
    return OllamaProvider()
