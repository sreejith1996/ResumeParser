import pytest
from unittest.mock import patch, MagicMock
from src.strategies.extraction_strategies import NameNERStrategy
from src.exceptions import SpacyLoadException
from src.constants import NEREntityLabel


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_nlp(entities=None):
    """
    Build a mock spaCy NLP callable that returns a doc with the given entities.
    entities: list of (text, label_) tuples, e.g. [("John Smith", "PERSON")]
    """
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    ents = []
    for text, label in (entities or []):
        ent = MagicMock()
        ent.text = text
        ent.label_ = label
        ents.append(ent)
    mock_doc.ents = ents
    mock_nlp.return_value = mock_doc
    return mock_nlp


def _make_strategy(nlp_mock):
    """Instantiate NameNERStrategy with a patched spacy.load."""
    with patch("src.strategies.extraction_strategies.spacy.load", return_value=nlp_mock):
        return NameNERStrategy()


# ── Model loading ─────────────────────────────────────────────────────────────

class TestModelLoading:
    def test_spacy_load_exception_on_os_error(self):
        with patch(
            "src.strategies.extraction_strategies.spacy.load",
            side_effect=OSError("model not found"),
        ):
            with pytest.raises(SpacyLoadException):
                NameNERStrategy()

    def test_spacy_load_exception_on_generic_error(self):
        with patch(
            "src.strategies.extraction_strategies.spacy.load",
            side_effect=RuntimeError("unexpected"),
        ):
            with pytest.raises(SpacyLoadException):
                NameNERStrategy()

    def test_custom_model_name_passed_to_spacy(self):
        with patch("src.strategies.extraction_strategies.spacy.load") as mock_load:
            mock_load.return_value = _make_nlp()
            NameNERStrategy(spacy_model="en_core_web_sm")
            mock_load.assert_called_once_with("en_core_web_sm")


# ── NER extraction ────────────────────────────────────────────────────────────

class TestNERExtraction:
    def test_extracts_name_mixed_case(self):
        nlp = _make_nlp([("John Smith", NEREntityLabel.PERSON)])
        strategy = _make_strategy(nlp)
        result = strategy.extract("John Smith\nSoftware Engineer\nNew York")
        assert result == "John Smith"

    def test_extracts_name_all_caps_header(self):
        # ALL-CAPS header should be normalized to title case before NER
        nlp = _make_nlp([("John Smith", NEREntityLabel.PERSON)])
        strategy = _make_strategy(nlp)
        result = strategy.extract("JOHN SMITH\nSOFTWARE ENGINEER\nNEW YORK")
        assert result == "John Smith"

    def test_skips_entity_containing_email(self):
        # PERSON entity that contains an email → skipped
        nlp = _make_nlp([
            ("john@example.com", NEREntityLabel.PERSON),
            ("Jane Doe", NEREntityLabel.PERSON),
        ])
        strategy = _make_strategy(nlp)
        result = strategy.extract("john@example.com\nJane Doe")
        assert result == "Jane Doe"

    def test_skips_entity_containing_digits(self):
        # PERSON entity with digits → skipped
        nlp = _make_nlp([
            ("John123 Smith", NEREntityLabel.PERSON),
            ("Alice Brown", NEREntityLabel.PERSON),
        ])
        strategy = _make_strategy(nlp)
        result = strategy.extract("John123 Smith\nAlice Brown")
        assert result == "Alice Brown"

    def test_skips_single_word_entity(self):              
        # PERSON entity with no space (single word) → skipped
        nlp = _make_nlp([
            ("John", NEREntityLabel.PERSON),
            ("Jane Doe", NEREntityLabel.PERSON),
        ])
        strategy = _make_strategy(nlp)
        result = strategy.extract("John\nJane Doe")
        assert result == "Jane Doe"

    def test_returns_first_valid_person_entity(self):
        # First valid PERSON entity is returned
        nlp = _make_nlp([
            ("Alice Johnson", NEREntityLabel.PERSON),
            ("Bob Williams", NEREntityLabel.PERSON),
        ])
        strategy = _make_strategy(nlp)
        result = strategy.extract("Alice Johnson\nBob Williams")
        assert result == "Alice Johnson"

    def test_uses_only_first_ten_lines_for_ner(self):
        # Name on line 11 should NOT be found by NER (only first 10 used)
        nlp = _make_nlp([])  # NER finds nothing
        strategy = _make_strategy(nlp)
        lines = ["Line {}".format(i) for i in range(1, 11)]  # 10 filler lines
        lines.append("Hidden Name")                           # line 11
        text = "\n".join(lines)
        result = strategy.extract(text)
        # NER finds nothing; fallback also won't reach line 11
        assert result == ""

    def test_ner_receives_only_header_text(self):
        # Verify NLP is called with only the first 10 non-empty lines
        nlp = _make_nlp([])
        strategy = _make_strategy(nlp)
        lines = ["Line {}".format(i) for i in range(1, 12)]  # 11 lines
        strategy.extract("\n".join(lines))
        called_with = nlp.call_args[0][0]
        assert "Line 10" in called_with
        assert "Line 11" not in called_with


# ── Case normalization ────────────────────────────────────────────────────────

class TestCaseNormalization:
    def test_all_caps_normalized_to_title_case(self):
        nlp = _make_nlp([])
        strategy = _make_strategy(nlp)
        strategy.extract("JOHN SMITH\nSOME COMPANY")
        called_with = nlp.call_args[0][0]
        # Should be title-cased, not all-caps
        assert called_with == "John Smith\nSome Company"

    def test_mixed_case_not_altered(self):                 
        nlp = _make_nlp([])
        strategy = _make_strategy(nlp)
        strategy.extract("John Smith\nGoogle Inc")
        called_with = nlp.call_args[0][0]
        assert called_with == "John Smith\nGoogle Inc"


# ── Fallback extraction ───────────────────────────────────────────────────────

class TestFallbackExtraction:
    def _strategy_no_ner(self):
        """Strategy whose NER returns no entities → always falls back."""
        return _make_strategy(_make_nlp([]))

    def test_fallback_finds_two_word_name(self):           
        strategy = self._strategy_no_ner()
        result = strategy.extract("John Smith\nSoftware Engineer at Google")
        assert result == "John Smith"

    def test_fallback_finds_four_word_name(self):          
        strategy = self._strategy_no_ner()
        result = strategy.extract("John Michael Van Smith\nEngineer")
        assert result == "John Michael Van Smith"

    def test_fallback_rejects_single_word(self):           
        strategy = self._strategy_no_ner()
        # Only single-word lines in fallback range → no match
        result = strategy.extract("John\nEngineer\nDeveloper\nManager\nCoder")
        assert result == ""

    def test_fallback_rejects_five_words(self):            
        strategy = self._strategy_no_ner()
        result = strategy.extract("One Two Three Four Five\nAnother Long Line Here Too")
        assert result == ""

    def test_fallback_skips_line_with_email(self):          
        strategy = self._strategy_no_ner()
        # Line 1 has an email → rejected by fallback; line 2 is a valid name → found
        result = strategy.extract("john@example.com\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_line_with_digits(self):      
        strategy = self._strategy_no_ner()
        result = strategy.extract("John Smith 2\nAnother line here")
        # "John Smith 2" has a digit → skipped; "Another line here" has 3 words → skipped (>4? no, 3 words is OK)
        # Wait: "Another line here" = 3 words, no digits, no email, no special chars → valid
        result = strategy.extract("John Smith 2\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_pipe_character(self):        
        strategy = self._strategy_no_ner()
        result = strategy.extract("John | Smith\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_forward_slash(self):         
        strategy = self._strategy_no_ner()
        result = strategy.extract("John/Smith\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_backslash(self):            
        strategy = self._strategy_no_ner()
        result = strategy.extract("John\\Smith\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_colon(self): 
        strategy = self._strategy_no_ner()
        result = strategy.extract("Name: John\nValid Name")
        assert result == "Valid Name"

    def test_fallback_rejects_comma(self):                
        strategy = self._strategy_no_ner()
        result = strategy.extract("Smith, John\nValid Name")
        assert result == "Valid Name"

    def test_fallback_searches_only_first_five_lines(self):
        strategy = self._strategy_no_ner()
        # Lines 1-5: all single-word (rejected by word count)
        # Line 6: valid name → should NOT be found
        lines = ["Word"] * 5 + ["Valid Name"]
        result = strategy.extract("\n".join(lines))
        assert result == ""

    def test_fallback_finds_name_in_line_five(self):
        strategy = self._strategy_no_ner()
        # Lines 1-4: invalid; line 5: valid name
        lines = ["Word", "Word", "Word", "Word", "Valid Name"]
        result = strategy.extract("\n".join(lines))
        assert result == "Valid Name"


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_text_returns_empty_string(self):
        strategy = _make_strategy(_make_nlp([]))
        assert strategy.extract("") == ""

    def test_no_match_returns_empty_string(self):  
        strategy = _make_strategy(_make_nlp([]))
        # All lines are single words or have special chars
        result = strategy.extract("Engineer\nDeveloper\nManager\nCoder\nLead")
        assert result == ""

    def test_fewer_than_ten_lines_no_error(self):   
        nlp = _make_nlp([("Alice Brown", NEREntityLabel.PERSON)])
        strategy = _make_strategy(nlp)
        # Only 3 lines — should not raise
        result = strategy.extract("Alice Brown\nEngineer\nNew York")
        assert result == "Alice Brown"

    def test_fewer_than_five_lines_fallback_no_error(self): 
        strategy = _make_strategy(_make_nlp([]))
        # Only 2 lines — fallback should not raise
        result = strategy.extract("Valid Name\nSomething")
        assert result == "Valid Name"

    def test_empty_lines_ignored_in_header(self):
        # Empty lines should be skipped when building header
        nlp = _make_nlp([("Alice Brown", NEREntityLabel.PERSON)])
        strategy = _make_strategy(nlp)
        text = "\n\n\nAlice Brown\n\nEngineer"
        result = strategy.extract(text)
        assert result == "Alice Brown"
