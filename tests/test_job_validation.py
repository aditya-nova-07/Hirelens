import unittest
from types import SimpleNamespace

from job_validation import validate_job_description_text


SAMPLE_JOB = """# Software Development Engineer Intern

**Company:** TechNova Solutions
**Location:** Bengaluru, India
**Job Type:** Internship

## About the Role

We are looking for an intern to build scalable applications, develop APIs, debug software, and collaborate with experienced developers.

## Responsibilities
- Develop and maintain applications using Python, Java, or C++.
- Build and integrate REST APIs and work with databases.

## Required Skills
- Strong programming fundamentals and data structures.
- Proficiency in Python, Java, or C++.

## Eligibility
- Pursuing a Bachelor's degree in Computer Science or a related field.
"""


def parsed_job(role="", **overrides):
    values = {
        "role": role,
        "required_skills": [],
        "preferred_skills": [],
        "minimum_experience": None,
        "education_requirements": [],
        "responsibilities": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class JobDescriptionValidationTests(unittest.TestCase):
    def test_structured_job_ad_passes_when_model_misses_fields(self):
        valid, _, role = validate_job_description_text(SAMPLE_JOB, parsed_job())
        self.assertTrue(valid)
        self.assertEqual(role, "Software Development Engineer Intern")

    def test_model_extracted_job_details_pass_without_markdown_sections(self):
        valid, _, role = validate_job_description_text(
            "Backend developer role building reliable services for internal teams. The engineer will collaborate with product partners, review code, troubleshoot production issues, and contribute to API design and maintenance.",
            parsed_job("Backend Developer", required_skills=["Python"]),
        )
        self.assertTrue(valid)
        self.assertEqual(role, "Backend Developer")

    def test_unstructured_text_without_requirements_does_not_pass(self):
        valid, _, _ = validate_job_description_text(
            "I enjoy software and want a new opportunity.", parsed_job()
        )
        self.assertFalse(valid)

    def test_description_with_fewer_than_25_words_is_rejected(self):
        valid, reason, _ = validate_job_description_text(
            "# Backend Developer\nBuild APIs and maintain Python services.",
            parsed_job("Backend Developer", required_skills=["Python"]),
        )
        self.assertFalse(valid)
        self.assertIn("at least 25 words", reason)

    def test_description_with_at_least_25_words_can_pass(self):
        valid, _, _ = validate_job_description_text(SAMPLE_JOB, parsed_job())
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
