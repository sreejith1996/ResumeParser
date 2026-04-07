import json
import os
import pytest
from unittest.mock import patch, MagicMock
from google.genai import errors as genai_errors
from src.strategies.extraction_strategies import SkillsLLMStrategy
from src.exceptions import LLMException, LLMResponseParseException
from src.constants import GEMINI_API_KEY_ENV, SKILLS_SYSTEM_INSTRUCTION


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_strategy(response_text=None, api_side_effect=None):
    """
    Build a SkillsLLMStrategy with a mocked genai.Client.
    - response_text: string that mock_response.text will return
    - api_side_effect: exception to raise from generate_content
    """
    with patch("src.strategies.extraction_strategies.genai.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        if api_side_effect is not None:
            mock_client.models.generate_content.side_effect = api_side_effect
        else:
            mock_response = MagicMock()
            mock_response.text = response_text
            mock_client.models.generate_content.return_value = mock_response

        strategy = SkillsLLMStrategy()
        # Expose the mock so callers can introspect calls
        strategy._mock_client = mock_client
        return strategy


# ── Constructor ───────────────────────────────────────────────────────────────

class TestSkillsLLMStrategyConstructor:
    def test_initializes_with_api_key_from_env(self):     
        with patch("src.strategies.extraction_strategies.genai.Client") as mock_cls:
            with patch.dict(os.environ, {GEMINI_API_KEY_ENV: "test-key-123"}):
                SkillsLLMStrategy()
                mock_cls.assert_called_once_with(api_key="test-key-123")

    def test_initializes_with_none_when_key_missing(self):
        # When env var is absent, os.getenv returns None (default=None in code)
        with patch("src.strategies.extraction_strategies.genai.Client") as mock_cls:
            env = {k: v for k, v in os.environ.items() if k != GEMINI_API_KEY_ENV}
            with patch.dict(os.environ, env, clear=True):
                SkillsLLMStrategy()
                mock_cls.assert_called_once_with(api_key=None)


# ── Successful extraction ─────────────────────────────────────────────────────

class TestSkillsLLMStrategyExtract:
    def test_returns_list_of_strings(self):               
        strategy = _make_strategy('["Python", "Docker"]')
        result = strategy.extract("I know Python and Docker.")
        assert result == ["Python", "Docker"]

    def test_returns_empty_list_for_empty_json_array(self):  
        strategy = _make_strategy("[]")
        result = strategy.extract("No skills found.")
        assert result == []

    def test_returns_single_skill(self):                 
        strategy = _make_strategy('["Python"]')
        result = strategy.extract("I only know Python.")
        assert result == ["Python"]

    def test_returns_many_skills(self):                  
        skills = ["Python", "Docker", "Kubernetes", "AWS", "React", "PostgreSQL"]
        strategy = _make_strategy(json.dumps(skills))
        result = strategy.extract("Senior engineer with extensive skills.")
        assert result == skills

    def test_passes_text_as_content_to_api(self):
        strategy = _make_strategy('["Python"]')
        resume_text = "Experienced Python developer."
        strategy.extract(resume_text)
        call_kwargs = strategy._mock_client.models.generate_content.call_args
        assert call_kwargs[1]["contents"] == resume_text or call_kwargs[0][1] == resume_text

    def test_passes_system_instruction(self):
        strategy = _make_strategy('["Python"]')
        strategy.extract("some text")
        call_kwargs = strategy._mock_client.models.generate_content.call_args
        args, kwargs = call_kwargs
        config = kwargs.get("config") or args[2]
        assert config.system_instruction == SKILLS_SYSTEM_INSTRUCTION


# ── Error handling ────────────────────────────────────────────────────────────

class TestSkillsLLMStrategyErrors:
    def test_raises_llm_exception_on_api_failure(self):
        api_error = genai_errors.APIError(500, {"error": "API is down"})
        strategy = _make_strategy(api_side_effect=api_error)
        with pytest.raises(LLMException):
            strategy.extract("some text")

    def test_raises_parse_exception_on_invalid_json(self):
        strategy = _make_strategy("not valid json at all")
        with pytest.raises(LLMResponseParseException):
            strategy.extract("some text")

    def test_raises_parse_exception_on_partial_json(self):
        strategy = _make_strategy('["Python", "Doc')
        with pytest.raises(LLMResponseParseException):
            strategy.extract("some text")

    def test_json_object_response_not_an_array(self):
        strategy = _make_strategy('{"skill": "Python"}')
        with pytest.raises(LLMResponseParseException):
            strategy.extract("some text")
