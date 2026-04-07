import pytest
from unittest.mock import patch, MagicMock
from src.resume_extractor import ResumeParserFramework
from src.models.schema import ResumeData
from src.constants import ExtractionField
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
    Returns a (patch_ctx, strategy) tuple. patch_ctx patches ParserFactory only.
    strategy is a dict of ExtractionField -> mock strategy, ready to pass to ResumeParserFramework.
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

    strategy = {
        ExtractionField.NAME: mock_ner,
        ExtractionField.EMAIL: mock_email_strategy,
        ExtractionField.SKILLS: mock_llm,
    }

    return (
        patch("src.resume_extractor.ParserFactory.get_parser", return_value=mock_parser),
        strategy,
    )


def _dummy_strategy():
    return {
        ExtractionField.NAME: MagicMock(),
        ExtractionField.EMAIL: MagicMock(),
        ExtractionField.SKILLS: MagicMock(),
    }


class TestResumeParserFramework:
    def _run(self, path="resume.pdf", **kwargs):
        patch_ctx, strategy = _patch_framework(**kwargs)
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
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
            framework = ResumeParserFramework(extraction_strategy=_dummy_strategy())
            with pytest.raises(ResumeFileNotFoundException):
                framework.parse_resume("/nonexistent/path/resume.pdf")

    def test_unsupported_type_raises_exception(self):
        with patch(
            "src.resume_extractor.ParserFactory.get_parser",
            side_effect=UnsupportedFileTypeException("unsupported"),
        ):
            framework = ResumeParserFramework(extraction_strategy=_dummy_strategy())
            with pytest.raises(UnsupportedFileTypeException):
                framework.parse_resume("resume.txt")

    def test_pdf_parse_failure_raises_pdf_exception(self, single_page_pdf):
        patch_ctx, strategy = _patch_framework(parse_side_effect=PDFParserImportException("pdf failed"))
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
            with pytest.raises(PDFParserImportException):
                framework.parse_resume(single_page_pdf)

    def test_docx_parse_failure_raises_word_exception(self, paragraph_docx):
        patch_ctx, strategy = _patch_framework(parse_side_effect=WordParserImportException("docx failed"))
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
            with pytest.raises(WordParserImportException):
                framework.parse_resume(paragraph_docx)

    def test_spacy_load_failure_raises_spacy_exception(self, single_page_pdf):
        patch_ctx, strategy = _patch_framework(ner_side_effect=SpacyLoadException("model not found"))
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
            with pytest.raises(SpacyLoadException):
                framework.parse_resume(single_page_pdf)

    def test_llm_api_failure_raises_llm_exception(self, single_page_pdf):
        patch_ctx, strategy = _patch_framework(llm_side_effect=LLMException("api down"))
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
            with pytest.raises(LLMException):
                framework.parse_resume(single_page_pdf)

    def test_llm_parse_failure_raises_parse_exception(self, single_page_pdf):
        patch_ctx, strategy = _patch_framework(llm_side_effect=LLMResponseParseException("bad json"))
        with patch_ctx:
            framework = ResumeParserFramework(extraction_strategy=strategy)
            with pytest.raises(LLMResponseParseException):
                framework.parse_resume(single_page_pdf)
