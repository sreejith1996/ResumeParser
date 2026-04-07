from src.resume_extractor import ResumeParserFramework
from dotenv import load_dotenv

load_dotenv()

def main():
    resumer_parser_framework = ResumeParserFramework()
    print(resumer_parser_framework.parse_resume('./samples/Resume.pdf'))

if __name__ == "__main__":
    main()