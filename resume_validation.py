"""Low-cost file and resume-content validation used before AI parsing."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
import zipfile


MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024

_INDICATORS = {
    "contact/profile": re.compile(
        r"(?:[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:linkedin\.com|github\.com)/|"
        r"\b(?:phone|email|contact|profile|professional summary|career objective)\b)", re.I
    ),
    "skills": re.compile(r"\b(?:technical )?skills\b|\bcore competencies\b", re.I),
    "education": re.compile(r"\b(?:education|academic background|university|college)\b", re.I),
    "projects": re.compile(r"\b(?:projects|selected projects|personal projects)\b", re.I),
    "experience": re.compile(
        r"\b(?:professional experience|work experience|employment history|work history|"
        r"internships?|experience)\b", re.I
    ),
    "certifications": re.compile(r"\b(?:certifications?|licenses?)\b", re.I),
}
_JOB_DESCRIPTION_CUES = re.compile(
    r"\b(?:job description|role overview|responsibilities|what you(?:'|’)ll do|"
    r"qualifications|who you are|we are looking for|required skills|preferred qualifications)\b", re.I
)
_ACADEMIC_CUES = re.compile(
    r"\b(?:assignment|essay|lab report|coursework|rubric|student name|question \d+|"
    r"submission date|term paper|homework)\b", re.I
)
_PERSONAL_CONTACT = re.compile(
    r"(?:[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\+?\d[\d().\s-]{7,}\d|"
    r"linkedin\.com/|github\.com/)", re.I
)


def document_id(uploaded_file) -> str:
    """Return a content-based identifier without persisting the uploaded file."""
    data = uploaded_file.getvalue()
    return sha256(uploaded_file.name.encode("utf-8", "replace") + b"\0" + data).hexdigest()


def inspect_resume_file(uploaded_file, read_pdf, read_docx, classifier=None) -> dict:
    """Check actual file content, extract text with the existing readers, and classify it."""
    name = str(getattr(uploaded_file, "name", "uploaded file"))
    suffix = Path(name).suffix.lower()
    try:
        data = uploaded_file.getvalue()
    except Exception as error:
        return _result("Unreadable", f"The file could not be read: {error}")

    if suffix not in {".pdf", ".docx"}:
        return _result("Rejected", "Unsupported document type. Upload a PDF or DOCX resume.")
    if not data:
        return _result("Unreadable", "The file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        return _result("Rejected", "The file exceeds the 15 MB safety limit.")

    if suffix == ".pdf":
        if b"%PDF-" not in data[:1024]:
            return _result("Unreadable", "The .pdf file does not have a valid PDF signature.")
        reader = read_pdf
    else:
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                names = set(archive.namelist())
                uncompressed_size = sum(item.file_size for item in archive.infolist())
            if "word/document.xml" not in names:
                return _result("Unreadable", "The DOCX package is missing its main document.")
            if uncompressed_size > MAX_DOCX_UNCOMPRESSED_BYTES:
                return _result("Rejected", "The DOCX expands beyond the 50 MB safety limit.")
        except (zipfile.BadZipFile, OSError, ValueError):
            return _result("Unreadable", "The .docx file is not a readable Word document.")
        reader = read_docx

    try:
        uploaded_file.seek(0)
        text = reader(uploaded_file)
        uploaded_file.seek(0)
    except Exception as error:
        return _result("Unreadable", f"The document could not be extracted: {error}")

    text = text.strip() if isinstance(text, str) else ""
    if not text:
        return _result(
            "Unreadable",
            "No selectable text was found. The file may be empty or image-only; OCR is not enabled.",
        )

    return validate_resume_text(text, classifier=classifier)


def validate_resume_text(text: str, classifier=None) -> dict:
    """Use multiple resume indicators, rejecting clear non-resumes and reviewing ambiguity."""
    content = text.strip()
    if not content:
        return _result("Unreadable", "No selectable text was found in the document.")

    found = [label for label, pattern in _INDICATORS.items() if pattern.search(content)]
    job_cues = len(_JOB_DESCRIPTION_CUES.findall(content))
    academic_cues = len(_ACADEMIC_CUES.findall(content))

    personal_contact = bool(_PERSONAL_CONTACT.search(content))
    if job_cues >= 2 and not personal_contact:
        return _result("Rejected", "This looks like a job description rather than a candidate resume.", found, content)
    if academic_cues >= 2 and not personal_contact and len(found) < 4:
        return _result("Rejected", "This looks like an academic assignment or essay, not a resume.", found, content)
    if len(found) >= 3 and (personal_contact or len(found) >= 4):
        return _result("Valid resume", "Several resume sections were found in the document.", found, content)

    if classifier is not None:
        try:
            classified = classifier(content[:6000])
            if not isinstance(classified, dict):
                raise ValueError("Classifier response was not an object.")
            category = classified.get("classification")
            reason = classified.get("reason")
            if category not in {"resume", "non_resume", "uncertain"} or not isinstance(reason, str) or not reason.strip():
                raise ValueError("Classifier response did not match the expected fields.")
            if category == "resume":
                return _result("Valid resume", reason.strip(), found, content)
            if category == "non_resume":
                return _result("Rejected", reason.strip(), found, content)
            return _result("Needs review", reason.strip(), found, content)
        except Exception:
            # A failed or malformed classifier must never turn uncertain content into an automatic pass.
            pass

    reason = (
        "The document has few recognizable resume sections. Review it before allowing analysis."
        if found else "The text does not clearly identify a resume. Review it before allowing analysis."
    )
    return _result("Needs review", reason, found, content)


def processable_documents(validations: dict, approved_ids=()) -> list[str]:
    """Return only validated resumes and documents explicitly approved after review."""
    approved = set(approved_ids)
    return [
        identifier for identifier, item in validations.items()
        if item.get("status") == "Valid resume"
        or (item.get("status") == "Needs review" and identifier in approved)
    ]


def _result(status: str, reason: str, indicators=None, text="") -> dict:
    return {
        "status": status,
        "reason": reason,
        "indicators": list(indicators or []),
        "text": text,
    }
