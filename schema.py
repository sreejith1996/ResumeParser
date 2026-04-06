from pydantic import BaseModel

class ResumeData(BaseModel):
    name: str
    email: str
    skills: list[str]