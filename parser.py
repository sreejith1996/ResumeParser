from abc import ABC, abstractmethod
from pathlib import Path

class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str):
        pass

class PDFParser(FileParser):
    def parse(self, file_path: str):
        return "Do something with the parsing"
    
class WordParser(FileParser):
    def parse(self, file_path: str):
        return "Do something with the word parser here"
    
class ParserFactory:
    _registry = {
        ".pdf": PDFParser,
        ".docx": WordParser
    }

    @classmethod
    def get_parser(cls, file_path: str) -> FileParser:
        ext = Path(file_path).suffix
        parser_class = cls._registry.get(ext)
        if parser_class is None:
            raise ValueError(f"Unsupported file type: {ext}")
        return parser_class()