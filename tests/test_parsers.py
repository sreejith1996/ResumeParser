import pytest
from src.parsers.parser import FileParser, PDFParser, WordParser, ParserFactory
from src.exceptions import (
    PDFParserImportException,
    WordParserImportException,
    UnsupportedFileTypeException,
    ResumeFileNotFoundException,
)


# ── PDFParser ────────────────────────────────────────────────────────────────

class TestPDFParser:
    def test_is_subclass_of_file_parser(self):            
        assert issubclass(PDFParser, FileParser)

    def test_parse_single_page(self, single_page_pdf):    
        parser = PDFParser()
        text = parser.parse(single_page_pdf)
        assert "Hello World" in text

    def test_parse_multi_page_joined(self, multi_page_pdf):   
        parser = PDFParser()
        text = parser.parse(multi_page_pdf)
        assert "Page one content" in text
        assert "Page two content" in text
        # Pages joined by newline
        assert "\n" in text

    def test_parse_strips_whitespace(self, single_page_pdf):  
        parser = PDFParser()
        text = parser.parse(single_page_pdf)
        # Result should not have leading/trailing whitespace per page
        for line in text.split("\n"):
            assert line == line.strip() or line == ""

    def test_parse_empty_page_returns_empty_string(self, empty_page_pdf):  
        parser = PDFParser()
        text = parser.parse(empty_page_pdf)
        assert text == ""

    def test_parse_corrupt_raises_pdf_exception(self, corrupt_pdf):  
        parser = PDFParser()
        with pytest.raises(PDFParserImportException):
            parser.parse(corrupt_pdf)


# ── WordParser ───────────────────────────────────────────────────────────────

class TestWordParser:
    def test_is_subclass_of_file_parser(self):            
        assert issubclass(WordParser, FileParser)

    def test_parse_paragraphs_only(self, paragraph_docx): 
        parser = WordParser()
        text = parser.parse(paragraph_docx)
        assert "First paragraph" in text
        assert "Second paragraph" in text

    def test_parse_tables(self, table_docx):              
        parser = WordParser()
        text = parser.parse(table_docx)
        assert "Cell A1" in text
        assert "Cell B2" in text

    def test_parse_paragraphs_and_tables(self, mixed_docx):  
        parser = WordParser()
        text = parser.parse(mixed_docx)
        assert "Paragraph line" in text
        assert "Table cell" in text

    def test_no_duplicate_lines(self, duplicate_docx):    
        parser = WordParser()
        text = parser.parse(duplicate_docx)
        lines = [l for l in text.split("\n") if l.strip()]
        assert lines.count("Shared text") == 1

    def test_strips_whitespace_from_lines(self, paragraph_docx):  
        parser = WordParser()
        text = parser.parse(paragraph_docx)
        for line in text.split("\n"):
            if line:
                assert line == line.strip()

    def test_parse_empty_docx(self, empty_docx):          
        parser = WordParser()
        text = parser.parse(empty_docx)
        assert text == ""

    def test_parse_corrupt_raises_word_exception(self, corrupt_docx):  
        parser = WordParser()
        with pytest.raises(WordParserImportException):
            parser.parse(corrupt_docx)


# ── ParserFactory ────────────────────────────────────────────────────────────

class TestParserFactory:
    def test_get_parser_pdf(self, single_page_pdf):       
        parser = ParserFactory.get_parser(single_page_pdf)
        assert isinstance(parser, PDFParser)

    def test_get_parser_docx(self, paragraph_docx):       
        parser = ParserFactory.get_parser(paragraph_docx)
        assert isinstance(parser, WordParser)

    def test_nonexistent_file_raises_not_found(self, tmp_path):  
        fake_path = str(tmp_path / "ghost.pdf")
        with pytest.raises(ResumeFileNotFoundException):
            ParserFactory.get_parser(fake_path)

    def test_txt_extension_raises_unsupported(self, txt_file):   
        with pytest.raises(UnsupportedFileTypeException):
            ParserFactory.get_parser(txt_file)

    def test_png_extension_raises_unsupported(self, png_file):   
        with pytest.raises(UnsupportedFileTypeException):
            ParserFactory.get_parser(png_file)

    def test_no_extension_raises_unsupported(self, no_extension_file):  
        with pytest.raises(UnsupportedFileTypeException):
            ParserFactory.get_parser(no_extension_file)

    def test_uppercase_pdf_extension_returns_pdf_parser(self, upper_pdf_file):  
        parser = ParserFactory.get_parser(upper_pdf_file)
        assert isinstance(parser, PDFParser)

    def test_uppercase_docx_extension_returns_word_parser(self, upper_docx_file):  
        parser = ParserFactory.get_parser(upper_docx_file)
        assert isinstance(parser, WordParser)

    def test_directory_path_raises_unsupported(self, tmp_path):
        # tmp_path is a directory that exists; its suffix is "" → unsupported
        with pytest.raises(UnsupportedFileTypeException):
            ParserFactory.get_parser(str(tmp_path))
