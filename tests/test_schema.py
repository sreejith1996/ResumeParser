import pytest
from pydantic import ValidationError
from src.models.schema import ResumeData


class TestResumeDataConstruction:
    def test_valid_construction(self):                    
        data = ResumeData(name="John Smith", email="john@example.com", skills=["Python"])
        assert data.name == "John Smith"
        assert data.email == "john@example.com"
        assert data.skills == ["Python"]

    def test_skills_accepts_empty_list(self):             
        data = ResumeData(name="Jane Doe", email="jane@example.com", skills=[])
        assert data.skills == []

    def test_skills_accepts_multiple_items(self):         
        skills = ["Python", "Docker", "Kubernetes", "Machine Learning"]
        data = ResumeData(name="Bob Lee", email="bob@example.com", skills=skills)
        assert data.skills == skills


class TestResumeDataValidation:
    def test_missing_name_raises(self):                   
        with pytest.raises(ValidationError):
            ResumeData(email="a@b.com", skills=[])

    def test_missing_email_raises(self):                  
        with pytest.raises(ValidationError):
            ResumeData(name="Alice", skills=[])

    def test_missing_skills_raises(self):                 
        with pytest.raises(ValidationError):
            ResumeData(name="Alice", email="a@b.com")

    def test_name_must_be_string(self):                   
        with pytest.raises(ValidationError):
            ResumeData(name=123, email="a@b.com", skills=[])

    def test_email_must_be_string(self):                  
        with pytest.raises(ValidationError):
            ResumeData(name="Alice", email=456, skills=[])

    def test_skills_must_be_list(self):                   
        with pytest.raises(ValidationError):
            ResumeData(name="Alice", email="a@b.com", skills="Python")


class TestResumeDataSerialization:
    def test_model_dump_has_all_fields(self):             
        data = ResumeData(name="Alice", email="a@b.com", skills=["Go"])
        d = data.model_dump()
        assert d == {"name": "Alice", "email": "a@b.com", "skills": ["Go"]}

    def test_extra_fields_ignored_by_default(self):       
        # Pydantic v2 default: extra fields are ignored
        data = ResumeData(name="Alice", email="a@b.com", skills=[], unknown_field="x")
        assert not hasattr(data, "unknown_field")
