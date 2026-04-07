import re
from enum import Enum


class ExtractionField(str, Enum):
    NAME = "name"
    EMAIL = "email"
    SKILLS = "skills"


class FileExtension(str, Enum):
    PDF = ".pdf"
    DOCX = ".docx"


class SpacyModel(str, Enum):
    EN_CORE_WEB_LG = "en_core_web_lg"


class GeminiModel(str, Enum):
    FLASH_LITE = "gemini-2.5-flash-lite"


class NEREntityLabel(str, Enum):
    PERSON = "PERSON"


GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,7}",
    re.IGNORECASE,
)

SKILLS_SYSTEM_INSTRUCTION = (
    "You are a precise resume skills extractor. "
    "Given resume text, extract ALL technical and professional skills mentioned anywhere in it. "
    "Include programming languages, frameworks, tools, platforms, methodologies, and soft skills. "
    "Normalize names (e.g., 'k8s' → 'Kubernetes', 'ML' → 'Machine Learning'). "
    "Return ONLY a valid JSON array of strings. No explanation, no markdown, no preamble. "
    'Example output: ["Python", "Machine Learning", "Docker", "REST APIs"]'
)


NER_HEADER_LINES = 10       
NAME_FALLBACK_LINES = 5     
NAME_MIN_WORDS = 2          
NAME_MAX_WORDS = 4          
