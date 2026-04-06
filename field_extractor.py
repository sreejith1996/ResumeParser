from abc import ABC, abstractmethod
from extraction_strategies import ExtractionStrategy

class FieldExtractor(ABC):
    @abstractmethod
    def extract(self):
        pass

class NameExtractor(FieldExtractor):
    def __init__(self, strategy: ExtractionStrategy[str]):
        self.strategy = strategy

    def extract(self, text: str) -> str:
        return self.strategy.extract(text=text)

class EmailExtactor(FieldExtractor):
    def __init__(self, strategy: ExtractionStrategy[str]):
        self.strategy = strategy

    def extract(self, text: str) -> str:
        return self.strategy.extract(text=text)

class SkillsExtractor(FieldExtractor):
    def __init__(self, strategy: ExtractionStrategy[list[str]]):
        self.strategy = strategy

    def extract(self, text: str) -> list[str]:
        return self.strategy.extract(text=text)
    