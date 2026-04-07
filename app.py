import tempfile
import os
import streamlit as st
from dotenv import load_dotenv
from src.resume_extractor import ResumeParserFramework
from src.constants import ExtractionField
from src.strategies.extraction_strategies import NameNERStrategy, EmailRegexStrategy, SkillsLLMStrategy

load_dotenv()

st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("Resume Parser")
st.write("Upload a resume (PDF or DOCX) to extract structured information.")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        with st.spinner("Parsing resume..."):
            framework = ResumeParserFramework(extraction_strategy={
                ExtractionField.NAME: NameNERStrategy(),
                ExtractionField.EMAIL: EmailRegexStrategy(),
                ExtractionField.SKILLS: SkillsLLMStrategy(),
            })
            result = framework.parse_resume(tmp_path)

        st.success("Parsing complete!")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Name", result.name)
        with col2:
            st.metric("Email", result.email)

        st.subheader("Skills")
        if result.skills:
            for skill in result.skills:
                st.badge(skill)
        else:
            st.write("No skills detected.")
    finally:
        os.unlink(tmp_path)
