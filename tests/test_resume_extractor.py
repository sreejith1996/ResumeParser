import pytest
from unittest.mock import MagicMock
from src.resume_extractor import ResumeExtractor
from src.constants import ExtractionField
from src.models.schema import ResumeData


def _make_strategy(return_value):
    """Build a mock extraction strategy that returns the given value."""
    mock = MagicMock()
    mock.extract.return_value = return_value
    return mock


def _make_extractor(name="Alice Brown", email="alice@example.com", skills=None):
    """Build a ResumeExtractor with three mock strategies."""
    if skills is None:
        skills = ["Python", "Docker"]
    strategies = {
        ExtractionField.NAME: _make_strategy(name),
        ExtractionField.EMAIL: _make_strategy(email),
        ExtractionField.SKILLS: _make_strategy(skills),
    }
    return ResumeExtractor(extraction_strategy=strategies), strategies


class TestResumeExtractorExtract:
    def test_returns_resume_data_instance(self):           
        extractor, _ = _make_extractor()
        result = extractor.extract("some resume text")
        assert isinstance(result, ResumeData)

    def test_calls_all_three_strategies(self):            
        extractor, strategies = _make_extractor()
        extractor.extract("resume text")
        strategies[ExtractionField.NAME].extract.assert_called_once_with("resume text")
        strategies[ExtractionField.EMAIL].extract.assert_called_once_with("resume text")
        strategies[ExtractionField.SKILLS].extract.assert_called_once_with("resume text")

    def test_maps_name_correctly(self):                   
        extractor, _ = _make_extractor(name="Bob Williams")
        result = extractor.extract("text")
        assert result.name == "Bob Williams"

    def test_maps_email_correctly(self):                  
        extractor, _ = _make_extractor(email="bob@example.com")
        result = extractor.extract("text")
        assert result.email == "bob@example.com"

    def test_maps_skills_correctly(self):                  
        extractor, _ = _make_extractor(skills=["Go", "Kubernetes"])
        result = extractor.extract("text")
        assert result.skills == ["Go", "Kubernetes"]

    def test_empty_string_text_passed_to_strategies(self):  
        extractor, strategies = _make_extractor()
        extractor.extract("")
        strategies[ExtractionField.NAME].extract.assert_called_once_with("")

    def test_missing_strategy_key_raises_key_error(self): 
        # Providing only NAME and EMAIL strategies — SKILLS missing
        strategies = {
            ExtractionField.NAME: _make_strategy("Alice"),
            ExtractionField.EMAIL: _make_strategy("alice@x.com"),
            # ExtractionField.SKILLS intentionally omitted
        }
        extractor = ResumeExtractor(extraction_strategy=strategies)
        with pytest.raises(KeyError):
            extractor.extract("text")

    def test_works_with_stub_strategies(self):
        # Verify the extractor is decoupled from concrete strategy implementations
        extractor, _ = _make_extractor(
            name="",
            email="",
            skills=[],
        )
        result = extractor.extract("empty resume")
        assert result.name == ""
        assert result.email == ""
        assert result.skills == []
