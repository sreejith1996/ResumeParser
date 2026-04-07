import spacy
import os
import json

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from google import genai
from google.genai import types, errors as genai_errors
from src.exceptions import LLMException, LLMResponseParseException, SpacyLoadException
from src.logger import get_logger
from src.constants import (
    EMAIL_PATTERN,
    GEMINI_API_KEY_ENV,
    SKILLS_SYSTEM_INSTRUCTION,
    PROMPT_INJECTION_PATTERNS,
    NER_HEADER_LINES,
    NAME_FALLBACK_LINES,
    NAME_MIN_WORDS,
    NAME_MAX_WORDS,
    MAX_SKILL_LENGTH,
    MAX_OUTPUT_TOKENS,
    TEMPRATURE,
    GeminiModel,
    NEREntityLabel,
    SpacyModel,
)

logger = get_logger()

T = TypeVar('T')

class ExtractionStrategy(ABC, Generic[T]):
    @abstractmethod
    def extract(self, text: str) -> T:
        pass

class EmailRegexStrategy(ExtractionStrategy[str]):
    def extract(self, text: str) -> str:
        match = EMAIL_PATTERN.search(text)
        return match.group(0).lower() if match else ""


class SkillsLLMStrategy(ExtractionStrategy[list[str]]):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv(GEMINI_API_KEY_ENV, default=None))

    @staticmethod
    def _sanitize(text: str) -> str:
        lines = text.splitlines()
        cleaned = [
            PROMPT_INJECTION_PATTERNS.sub("[removed]", line)
            for line in lines
        ]
        return chr(10).join(cleaned)

    def extract(self, text: str) -> list[str]:
        safe_text = self._sanitize(text)
        try:
            response = self.client.models.generate_content(
                model=GeminiModel.FLASH_LITE,
                contents=safe_text,
                config=types.GenerateContentConfig(
                    system_instruction=SKILLS_SYSTEM_INSTRUCTION,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    temperature=TEMPRATURE
                )
            )
        except genai_errors.APIError as e:
            logger.error("Gemini API call failed: %s", e)
            raise LLMException(f"Gemini API call failed: {e}") from e
        try:
            result = json.loads(response.text)
            if not isinstance(result, list):
                logger.error("Unexpected LLM response type: expected list, got %s", type(result).__name__)
                raise LLMResponseParseException(f"Expected list, got {type(result).__name__}")
            if not all(isinstance(s, str) and len(s) <= MAX_SKILL_LENGTH for s in result):
                logger.error("LLM response contained non-string or oversized skill entries")
                raise LLMResponseParseException("Response contained non-string or oversized skill entries")
            return result
        except json.JSONDecodeError as e:
            logger.error("Gemini returned invalid JSON: %r", response.text)
            raise LLMResponseParseException(f"Gemini returned invalid JSON: {response.text!r}") from e
        
class NameNERStrategy(ExtractionStrategy[str]):
    def __init__(self, spacy_model: str = SpacyModel.EN_CORE_WEB_LG):
        self._nlp = None
        self._model_name = spacy_model
        self._load_model()
 
    def _load_model(self) -> None:
        try:
            logger.debug("Loading spaCy model: %s", self._model_name)
            self._nlp = spacy.load(self._model_name)
            logger.debug("spaCy model loaded successfully")
        except OSError as e:
            logger.error("spaCy model '%s' not found", self._model_name)
            raise SpacyLoadException(
                f"spaCy model '{self._model_name}' not found.\n"
                f"Download it with: python -m spacy download {self._model_name}"
            ) from e
        except Exception as e:
            logger.error("spaCy loading failed: %s", e)
            raise SpacyLoadException(f"spaCy loading failed: {e}") from e
        
    def extract(self, text: str) -> str:
        # Work with the first NER_HEADER_LINES non-empty lines — the name is almost always there
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        header_text = "\n".join(lines[:NER_HEADER_LINES])

        # spaCy NER is trained on mixed-case text and will miss ALL-CAPS names.
        # Normalise to title case so "JOHN DOE" becomes "John Doe".
        normalized = header_text.title() if header_text.isupper() else header_text

        doc = self._nlp(normalized)
        for ent in doc.ents:
            if ent.label_ == NEREntityLabel.PERSON:
                name = ent.text.strip()
                # Sanity check: a real name shouldn't contain digits or be a single word
                if name and not EMAIL_PATTERN.search(name) and not any(c.isdigit() for c in name) and " " in name:
                    return name

        # Fallback: pick the first short line with no email/digits/punctuation — likely the name
        for line in lines[:NAME_FALLBACK_LINES]:
            candidate = line.title() if line.isupper() else line
            if (
                not EMAIL_PATTERN.search(candidate)
                and not any(c.isdigit() for c in candidate)
                and NAME_MIN_WORDS <= len(candidate.split()) <= NAME_MAX_WORDS
                and not any(c in candidate for c in r"|/\:,")
            ):
                return candidate

        return ""
        
    
class NameRegexStrategy(ExtractionStrategy[str]):
    def extract(self, text: str) -> str:
        pass
    

