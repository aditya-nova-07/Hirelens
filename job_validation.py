"""Structural checks for job descriptions, independent of model extraction quality."""

from __future__ import annotations

import re


def validate_job_description_text(text: str, job) -> tuple[bool, str, str]:
    """Accept well-structured job ads even when the model misses extracted fields."""
    word_count = len(text.split())
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    heading = lines[0] if lines else ""
    title = re.sub(r"^#{1,6}\s*", "", heading)
    title = re.sub(r"^\*\*(.*?)\*\*$", r"\1", title).strip(" -*")
    if title.lower().startswith(("job title:", "role:")):
        title = title.split(":", 1)[1].strip()

    content = text.casefold()
    cue_groups = (
        ("responsibilities", "what you will do", "duties", "about the role"),
        ("required skills", "qualifications", "requirements", "skills"),
        ("eligibility", "education requirements", "who you are"),
    )
    structural_cues = sum(any(cue in content for cue in group) for group in cue_groups)
    parsed_requirements = any((
        job.required_skills,
        job.preferred_skills,
        job.minimum_experience is not None,
        job.education_requirements,
        job.responsibilities,
    ))

    role = job.role.strip() or title
    has_role = bool(role and role.casefold() not in {"unknown", "not specified", "n/a"})
    enough_structure = len(text.strip()) >= 120 and structural_cues >= 2
    valid = word_count >= 25 and has_role and (parsed_requirements or enough_structure)
    if word_count < 25:
        return (
            False,
            f"A job description must contain at least 25 words. This one has {word_count}.",
            role,
        )
    if valid:
        return True, "This looks like a job description and includes role details.", role
    return (
        False,
        "Add a clear role title and at least one responsibility, skill, experience, or education requirement.",
        role,
    )
