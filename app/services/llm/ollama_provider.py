from typing import Dict, List

import ollama

from app.config import settings
from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self._client = ollama.Client(host=settings.ollama_host)
        self._model = settings.ollama_model

    def chat(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = self._client.chat(
            model=self._model,
            messages=full_messages,
            options={"temperature": 0.1, "num_predict": 500},
        )
        return response["message"]["content"]
