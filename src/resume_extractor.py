from src.models.schema import ResumeData
from src.strategies.extraction_strategies import NameNERStrategy, EmailRegexStrategy, SkillsLLMStrategy, ExtractionStrategy
from src.parsers.parser import ParserFactory
from src.constants import ExtractionField


class ResumeExtractor:
    def __init__(self, extraction_strategy: dict[ExtractionField, ExtractionStrategy]) -> ResumeData:
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> ResumeData:
        name = self.extraction_strategy[ExtractionField.NAME].extract(text)
        email = self.extraction_strategy[ExtractionField.EMAIL].extract(text)
        skills = self.extraction_strategy[ExtractionField.SKILLS].extract(text)
        return ResumeData(name=name, email=email, skills=skills)


class ResumeParserFramework:

    def parse_resume(self, file_path: str) -> ResumeData:
        parser = ParserFactory.get_parser(file_path=file_path)
        text = parser.parse(file_path)

        extractor = ResumeExtractor(extraction_strategy={
            ExtractionField.NAME: NameNERStrategy(),
            ExtractionField.EMAIL: EmailRegexStrategy(),
            ExtractionField.SKILLS: SkillsLLMStrategy(),
        })

        return extractor.extract(text)

        