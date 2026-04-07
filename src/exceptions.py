class LLMException(Exception):
    pass

class LLMResponseParseException(Exception):
    pass

class PDFParserImportException(Exception):
    pass

class WordParserImportException(Exception):
    pass

class SpacyLoadException(Exception):
    pass

class UnsupportedFileTypeException(Exception):
    pass

class ResumeFileNotFoundException(Exception):
    pass

class ResumeTooLongException(Exception):
    pass