from field_extractor import FieldExtractor
from schema import ResumeData
from parser import FileParser

from field_extractor import NameExtractor, EmailExtactor, SkillsExtractor
from extraction_strategies import NERStrategy, RegexStrategy, SkillsLLMStrategy
from parser import ParserFactory

class ResumeExtractor:
    def __init__(self, field_extractors: dict[str, FieldExtractor]) -> ResumeData:
        self.field_extractors = field_extractors

    def extract(self, text: str) -> ResumeData:
        name = self.field_extractors["name"].extract(text)
        email = self.field_extractors["email"].extract(text)
        skills = self.field_extractors["skills"].extract(text)
        return ResumeData(name=name, email=email, skills=skills)

class ResumeParserFramework:

    def parse_resume(self, file_path: str) -> ResumeData:

        parser = ParserFactory.get_parser(file_path=file_path)
        text = parser.parse(file_path)

        name_extractor = NameExtractor(strategy=NERStrategy())
        email_extractor = EmailExtactor(strategy=RegexStrategy())
        skills_extractor = SkillsExtractor(strategy=SkillsLLMStrategy())

        extractor = ResumeExtractor(field_extractors={
            "name": name_extractor,
            "email": email_extractor,
            "skills": skills_extractor,
        })

        return extractor.extract(text)
        