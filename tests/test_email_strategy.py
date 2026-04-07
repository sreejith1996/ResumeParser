import pytest
from src.strategies.extraction_strategies import EmailRegexStrategy


@pytest.fixture
def strategy():
    return EmailRegexStrategy()


class TestEmailRegexStrategyMatches:
    def test_standard_email_in_text(self, strategy):         
        assert strategy.extract("Email: john@example.com") == "john@example.com"

    def test_email_at_start(self, strategy):                 
        assert strategy.extract("john@example.com is my address") == "john@example.com"

    def test_email_at_end(self, strategy):                    
        assert strategy.extract("Contact me at john@example.com") == "john@example.com"

    def test_email_in_middle_of_paragraph(self, strategy):   
        text = "Please send your resume to hr@company.org for consideration."
        assert strategy.extract(text) == "hr@company.org"

    def test_email_with_subdomain(self, strategy):            
        assert strategy.extract("user@mail.company.org") == "user@mail.company.org"

    def test_email_with_plus_in_local_part(self, strategy):  
        assert strategy.extract("user+tag@domain.com") == "user+tag@domain.com"

    def test_email_with_dot_in_local_part(self, strategy):   
        assert strategy.extract("first.last@domain.com") == "first.last@domain.com"

    def test_email_returned_in_lowercase(self, strategy):    
        result = strategy.extract("Contact: JOHN.DOE@EXAMPLE.COM")
        assert result == "john.doe@example.com"

    def test_returns_first_email_when_multiple(self, strategy):  
        text = "Primary: alice@first.com, Secondary: bob@second.com"
        assert strategy.extract(text) == "alice@first.com"

    def test_email_with_seven_char_tld(self, strategy):      
        assert strategy.extract("user@example.abcdefg") == "user@example.abcdefg"


class TestEmailRegexStrategyNoMatch:
    def test_no_email_returns_empty_string(self, strategy):  
        assert strategy.extract("No email address here") == ""

    def test_plain_text_no_at_sign(self, strategy):          
        assert strategy.extract("just some plain text without any at sign") == ""

    def test_missing_local_part(self, strategy):             
        # "@domain.com" — no local part before @
        assert strategy.extract("@domain.com") == ""

    def test_missing_domain(self, strategy):                 
        # "user@" — nothing after @
        assert strategy.extract("user@") == ""

    def test_empty_string_returns_empty(self, strategy):
        assert strategy.extract("") == ""
