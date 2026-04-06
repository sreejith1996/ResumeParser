from resume_extractor import ResumeParserFramework

def main():
    resumer_parser_framework = ResumeParserFramework()
    print(resumer_parser_framework.parse_resume('./Resume.pdf'))




if __name__ == "__main__":
    main()