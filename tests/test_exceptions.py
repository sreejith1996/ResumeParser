import pytest
from src.exceptions import (
    LLMException,
    LLMResponseParseException,
    PDFParserImportException,
    WordParserImportException,
    SpacyLoadException,
    UnsupportedFileTypeException,
    ResumeFileNotFoundException,
)

ALL_EXCEPTIONS = [
    LLMException,
    LLMResponseParseException,
    PDFParserImportException,
    WordParserImportException,
    SpacyLoadException,
    UnsupportedFileTypeException,
    ResumeFileNotFoundException,
]


class TestExceptionInheritance:
    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_is_subclass_of_exception(self, exc_cls):   
        assert issubclass(exc_cls, Exception)

    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_can_be_raised_and_caught_as_exception(self, exc_cls):  
        with pytest.raises(Exception):
            raise exc_cls("test message")

    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_can_be_caught_by_own_type(self, exc_cls):  
        with pytest.raises(exc_cls):
            raise exc_cls("test message")


class TestExceptionMessage:
    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_preserves_message(self, exc_cls):           
        msg = "something went wrong"
        exc = exc_cls(msg)
        assert str(exc) == msg


class TestExceptionDistinctness:
    def test_llm_exception_not_caught_as_parse_exception(self):    
        with pytest.raises(LLMResponseParseException):
            raise LLMResponseParseException("parse error")
        # LLMException should NOT be caught if we only catch LLMResponseParseException
        with pytest.raises(LLMException):
            raise LLMException("api error")

    def test_pdf_exception_not_caught_as_word_exception(self):      
        with pytest.raises(PDFParserImportException):
            raise PDFParserImportException("pdf error")
        with pytest.raises(WordParserImportException):
            raise WordParserImportException("word error")

    def test_all_exceptions_are_distinct_types(self):              
        types_set = set(ALL_EXCEPTIONS)
        assert len(types_set) == len(ALL_EXCEPTIONS), "Duplicate exception types found"
