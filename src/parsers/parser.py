import pdfplumber
import docx
from abc import ABC, abstractmethod
from pathlib import Path
from src.exceptions import PDFParserImportException, WordParserImportException, UnsupportedFileTypeException, ResumeFileNotFoundException
from src.constants import FileExtension

class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str):
        pass

class PDFParser(FileParser):
    def parse(self, file_path: str):
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text.strip())
            return "\n".join(pages)
        except Exception as e:
            raise PDFParserImportException(f"PDF parsing failed: {e}") from e
        
class WordParser(FileParser):
    def parse(self, file_path: str):
        try: 
            doc = docx.Document(file_path)
            lines = []
    
            # Standard paragraphs (headings, bullets, plain text)
            for para in doc.paragraphs:
                if para.text.strip():
                    lines.append(para.text.strip())
    
            # Table cells — many resume templates use tables for layout
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()
                        if text and text not in lines:
                            lines.append(text)
    
            return "\n".join(lines)
        except Exception as e:
            raise WordParserImportException(f"Word parsing failed: {e}") from e

class ParserFactory:
    _registry = {
        FileExtension.PDF: PDFParser,
        FileExtension.DOCX: WordParser,
    }

    @classmethod
    def get_parser(cls, file_path: str) -> FileParser:
        path = Path(file_path)
        if not path.exists():
            raise ResumeFileNotFoundException(f"File not found: {file_path}")
        ext = path.suffix.lower()
        parser_class = cls._registry.get(ext)
        if parser_class is None:
            raise UnsupportedFileTypeException(f"Unsupported file type: {ext}")
        return parser_class()