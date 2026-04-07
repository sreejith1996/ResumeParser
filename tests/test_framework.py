import pytest
from unittest.mock import patch, MagicMock
from src.resume_extractor import ResumeParserFramework
from src.models.schema import ResumeData
from src.exceptions import (
    ResumeFileNotFoundException,
    UnsupportedFileTypeException,
    PDFParserImportException,
    WordParserImportException,
    SpacyLoadException,
    LLMException,
    LLMResponseParseException,
)


RESUME_DATA = ResumeData(name="Alice Brown", email="alice@example.com", skills=["Python"])
RESUME_TEXT = "Alice Brown\nalice@example.com\nPython Developer"


def _patch_framework(
    file_exists=True,
    file_ext=".pdf",
    parse_text=RESUME_TEXT,
    parse_side_effect=None,
    name="Alice Brown",
    email="alice@example.com",
    skills=None,
    ner_side_effect=None,
    llm_side_effect=None,
):
    """
    Context manager that patches ParserFactory, NameNERStrategy, and SkillsLLMStrategy
    so that ResumeParserFramework.parse_resume() can be exercised without real I/O.
    """
    if skills is None:
        skills = ["Python"]

    mock_parser = MagicMock()
    if parse_side_effect:
        mock_parser.parse.side_effect = parse_side_effect
    else:
        mock_parser.parse.return_value = parse_text

    mock_ner = MagicMock()
    if ner_side_effect:
        mock_ner.extract.side_effect = ner_side_effect
    else:
        mock_ner.extract.return_value = name

    mock_email_strategy = MagicMock()
    mock_email_strategy.extract.return_value = email

    mock_llm = MagicMock()
    if llm_side_effect:
        mock_llm.extract.side_effect = llm_side_effect
    else:
        mock_llm.extract.return_value = skills

    return (
        patch("src.resume_extractor.ParserFactory.get_parser", return_value=mock_parser),
        patch("src.resume_extractor.NameNERStrategy", return_value=mock_ner),
        patch("src.resume_extractor.EmailRegexStrategy", return_value=mock_email_strategy),
        patch("src.resume_extractor.SkillsLLMStrategy", return_value=mock_llm),
    )


class TestResumeParserFramework:
    def _run(self, path="resume.pdf", **kwargs):
        patches = _patch_framework(**kwargs)
        with patches[0], patches[1], patches[2], patches[3]:
            framework = ResumeParserFramework()
            return framework.parse_resume(path)

    def test_valid_pdf_returns_resume_data(self, single_page_pdf): 
        result = self._run(path=single_page_pdf)
        assert isinstance(result, ResumeData)

    def test_valid_docx_returns_resume_data(self, paragraph_docx): 
        result = self._run(path=paragraph_docx)
        assert isinstance(result, ResumeData)

    def test_nonexistent_file_raises_not_found(self): 
        with patch(
            "src.resume_extractor.ParserFactory.get_parser",
            side_effect=ResumeFileNotFoundException("not found"),
        ):
            framework = ResumeParserFramework()
            with pytest.raises(ResumeFileNotFoundException):
                framework.parse_resume("/nonexistent/path/resume.pdf")

    def test_unsupported_type_raises_exception(self):      
        with patch(
            "src.resume_extractor.ParserFactory.get_parser",
            side_effect=UnsupportedFileTypeException("unsupported"),
        ):
            framework = ResumeParserFramework()
            with pytest.raises(UnsupportedFileTypeException):
                framework.parse_resume("resume.txt")

    def test_pdf_parse_failure_raises_pdf_exception(self, single_page_pdf): 
        patches = _patch_framework(
            parse_side_effect=PDFParserImportException("pdf failed")
        )
        with patches[0], patches[1], patches[2], patches[3]:
            framework = ResumeParserFramework()
            with pytest.raises(PDFParserImportException):
                framework.parse_resume(single_page_pdf)

    def test_docx_parse_failure_raises_word_exception(self, paragraph_docx):
        patches = _patch_framework(
            parse_side_effect=WordParserImportException("docx failed")
        )
        with patches[0], patches[1], patches[2], patches[3]:
            framework = ResumeParserFramework()
            with pytest.raises(WordParserImportException):
                framework.parse_resume(paragraph_docx)

    def test_spacy_load_failure_raises_spacy_exception(self, single_page_pdf):
        with patch(
            "src.resume_extractor.ParserFactory.get_parser",
        ) as mock_factory, patch(
            "src.resume_extractor.NameNERStrategy",
            side_effect=SpacyLoadException("model not found"),
        ):
            mock_parser = MagicMock()
            mock_parser.parse.return_value = RESUME_TEXT
            mock_factory.return_value = mock_parser
            framework = ResumeParserFramework()
            with pytest.raises(SpacyLoadException):
                framework.parse_resume(single_page_pdf)

    def test_llm_api_failure_raises_llm_exception(self, single_page_pdf):
        patches = _patch_framework(
            llm_side_effect=LLMException("api down")
        )
        with patches[0], patches[1], patches[2], patches[3]:
            framework = ResumeParserFramework()
            with pytest.raises(LLMException):
                framework.parse_resume(single_page_pdf)

    def test_llm_parse_failure_raises_parse_exception(self, single_page_pdf): 
        patches = _patch_framework(
            llm_side_effect=LLMResponseParseException("bad json")
        )
        with patches[0], patches[1], patches[2], patches[3]:
            framework = ResumeParserFramework()
            with pytest.raises(LLMResponseParseException):
                framework.parse_resume(single_page_pdf)
