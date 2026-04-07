import argparse
from src.resume_extractor import ResumeParserFramework
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Parse a resume and extract structured data.")
    parser.add_argument("resume", help="Path to the resume file (PDF or DOCX)")
    args = parser.parse_args()

    resumer_parser_framework = ResumeParserFramework()
    print(resumer_parser_framework.parse_resume(args.resume))

if __name__ == "__main__":
    main()