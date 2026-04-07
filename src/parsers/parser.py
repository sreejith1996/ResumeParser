import pdfplumber
import docx
from abc import ABC, abstractmethod
from pathlib import Path
from src.exceptions import PDFParserImportException, WordParserImportException
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
            raise PDFParserImportException(f"PDF parsing failed: {e}")
        
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
            raise WordParserImportException(f"Word parsing failed: {e}")
    
class ParserFactory:
    _registry = {
        FileExtension.PDF: PDFParser,
        FileExtension.DOCX: WordParser,
    }

    @classmethod
    def get_parser(cls, file_path: str) -> FileParser:
        ext = Path(file_path).suffix
        parser_class = cls._registry.get(ext)
        if parser_class is None:
            raise ValueError(f"Unsupported file type: {ext}")
        return parser_class()