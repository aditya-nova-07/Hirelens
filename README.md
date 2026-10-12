# HireLens

HireLens is a Streamlit workspace for validating resume files, comparing resumes with a job description, and reviewing ranked candidate matches.

## Features

- Upload PDF and DOCX resumes and check whether each file appears to be a resume.
- Review ambiguous documents before allowing them into analysis.
- Require at least 25 words and job-related details in the job description.
- Parse job and resume details with Groq, then rank candidate matches.
- Review candidate profiles and grounded skill recommendations.

## Requirements

- Python 3.11
- [uv](https://docs.astral.sh/uv/)
- A Groq API key

## Run locally

Install the locked dependencies:

```powershell
uv sync --locked
```

Copy `.env.example` to `.env` and set `GROQ_API_KEY` to your key. Keep `.env` private; it is excluded from Git.

Start the app:

```powershell
uv run streamlit run app.py
```

Run the automated tests:

```powershell
uv run python -m unittest discover -s tests -v
```

## Deploy with Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Community Cloud, create an app using the repository, branch, and `app.py` entrypoint.
3. Add the following to the app's Secrets settings (replace the placeholder with your key):

   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

The app reads the key from Streamlit secrets in the cloud and from `.env` for local development. The root `uv.lock` provides the deployment dependencies; keep it synchronized with `pyproject.toml` when dependencies change.

## Privacy and limitations

Resume text, including extracted contact and career details, and the job description are sent to Groq for AI parsing and matching. Only upload documents when you have permission to process them. Analysis scores and recommendations are AI-generated estimates; review them before making hiring decisions. Results are held in the Streamlit session and no database is configured.

The document checks identify common file and content issues, but they do not verify candidate identity, employment history, or qualifications.
