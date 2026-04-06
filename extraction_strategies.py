from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class ExtractionStrategy(ABC, Generic[T]):
    @abstractmethod
    def extract(self, text: str) -> T:
        pass

class RegexStrategy(ExtractionStrategy[str]):
    def extract(self, text: str) -> str:
        return "REGEX strategy executed!"

class LLMStrategy(ExtractionStrategy[str]):
    def extract(self, text: str) -> str:
        return "LLM strategy executed!"

class NERStrategy(ExtractionStrategy[str]):
    def extract(self, text: str) -> str:
        return "NER strategy executed!"

class SkillsLLMStrategy(ExtractionStrategy[list[str]]):
    def extract(self, text: str) -> list[str]:
        return ["LLM strategy executed!"]
