import argparse
from src.resume_extractor import ResumeParserFramework
from dotenv import load_dotenv
from src.constants import ExtractionField
from src.strategies.extraction_strategies import NameNERStrategy, EmailRegexStrategy, SkillsLLMStrategy

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Parse a resume and extract structured data.")
    parser.add_argument("resume", help="Path to the resume file (PDF or DOCX)")
    args = parser.parse_args()

    resumer_parser_framework = ResumeParserFramework(extraction_strategy={
        ExtractionField.NAME: NameNERStrategy(),
        ExtractionField.EMAIL: EmailRegexStrategy(),
        ExtractionField.SKILLS: SkillsLLMStrategy(),
    })
    print(resumer_parser_framework.parse_resume(args.resume))

if __name__ == "__main__":
    main()