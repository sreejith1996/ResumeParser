# Resume Parser

Extracts structured information (name, email, skills) from resumes in PDF or DOCX format.  
Uses spaCy for NER-based name extraction and Gemini for skills extraction.

## Prerequisites

- A [Gemini API key](https://aistudio.google.com/apikey)
- Python 3.13+ **or** Docker

## Supported Files

| Format | Max Size | Max Pages |
|--------|----------|-----------|
| `.pdf` | 5 MB     | 3 pages   |
| `.docx`| 5 MB     | 3 pages   |

---

## Setup

Copy the example env file and add your Gemini API key:

```bash
cp .env.example .env
# open .env and set GEMINI_API_KEY=your_key_here
```

---

## Option 1 — Terminal (CLI)

**Install dependencies:**

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run:**

```bash
python main.py path/to/resume.pdf
```

---

## Option 2 — Streamlit (Web UI)

**Install dependencies** (same as above if not already done):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run:**

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser, upload a resume, and view the extracted results.

---

## Option 3 — Docker

**No Python installation required.**

**Build the image:**

```bash
docker build -t resume-parser .
```

**Run the container:**

```bash
docker run -p 8501:8501 --env-file .env resume-parser
```

Open [http://localhost:8501](http://localhost:8501) in your browser.
