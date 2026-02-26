from typing import Dict, List

import openai

from app.config import settings
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self._client = openai.OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def chat(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = self._client.chat.completions.create(
            model=self._model,
            messages=full_messages,
            temperature=0.1,
            max_tokens=500,
        )
        return response.choices[0].message.content
