from src.models.schema import ResumeData
from src.strategies.extraction_strategies import NameNERStrategy, EmailRegexStrategy, SkillsLLMStrategy, ExtractionStrategy
from src.parsers.parser import ParserFactory
from src.constants import ExtractionField
from src.logger import get_logger

logger = get_logger()


class ResumeExtractor:
    def __init__(self, extraction_strategy: dict[ExtractionField, ExtractionStrategy]):
        self.extraction_strategy = extraction_strategy

    def extract(self, text: str) -> ResumeData:
        logger.debug("Running extraction strategies")
        name = self.extraction_strategy[ExtractionField.NAME].extract(text)
        logger.debug("Extracted name: %s", name)
        email = self.extraction_strategy[ExtractionField.EMAIL].extract(text)
        logger.debug("Extracted email: %s", email)
        skills = self.extraction_strategy[ExtractionField.SKILLS].extract(text)
        logger.debug("Extracted %d skill(s)", len(skills))
        return ResumeData(name=name, email=email, skills=skills)


class ResumeParserFramework:

    def parse_resume(self, file_path: str) -> ResumeData:
        logger.info("Parsing resume: %s", file_path)
        parser = ParserFactory.get_parser(file_path=file_path)
        text = parser.parse(file_path)
        logger.debug("Parsed %d characters of text", len(text))

        extractor = ResumeExtractor(extraction_strategy={
            ExtractionField.NAME: NameNERStrategy(),
            ExtractionField.EMAIL: EmailRegexStrategy(),
            ExtractionField.SKILLS: SkillsLLMStrategy(),
        })

        result = extractor.extract(text)
        logger.info("Extraction complete")
        return result

        