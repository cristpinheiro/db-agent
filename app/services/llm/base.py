from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        ...
