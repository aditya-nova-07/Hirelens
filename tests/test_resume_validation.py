import io
import unittest
import zipfile
from unittest.mock import Mock

from resume_validation import inspect_resume_file, processable_documents, validate_resume_text


VALID_TEXT = """
Jordan Lee
jordan.lee@example.org | 555-010-2000
Technical Skills: Python, SQL
Education: BSc Computer Science
Projects: Built an inventory dashboard
"""


class FakeUpload(io.BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name

    def getvalue(self):
        return super().getvalue()


def docx_package():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("word/document.xml", "<document/>")
    return stream.getvalue()


class ResumeValidationTests(unittest.TestCase):
    def test_multiple_resume_indicators_pass_without_classifier(self):
        result = validate_resume_text(VALID_TEXT, classifier=lambda text: self.fail("not needed"))
        self.assertEqual(result["status"], "Valid resume")
        self.assertGreaterEqual(len(result["indicators"]), 3)

    def test_unrelated_assignment_is_rejected_before_classifier(self):
        text = "Student Name: Alex\nCoursework Assignment\nEssay prompt\nSubmission date: Monday"
        result = validate_resume_text(text, classifier=lambda _: self.fail("clear non-resume"))
        self.assertEqual(result["status"], "Rejected")

    def test_job_description_uploaded_as_resume_is_rejected(self):
        text = "Job Description\nResponsibilities include reporting.\nQualifications required: SQL.\nWhat you will do: build dashboards."
        result = validate_resume_text(text, classifier=lambda _: self.fail("clear job ad"))
        self.assertEqual(result["status"], "Rejected")
        self.assertIn("job description", result["reason"].lower())

    def test_ambiguous_document_can_be_classified_or_sent_for_review(self):
        result = validate_resume_text("Python and data work across several years.", lambda _: {
            "classification": "resume", "reason": "Profile and skills are described."
        })
        self.assertEqual(result["status"], "Valid resume")

        uncertain = validate_resume_text("Python and data work.", lambda _: {
            "classification": "uncertain", "reason": "Not enough context."
        })
        self.assertEqual(uncertain["status"], "Needs review")

    def test_classifier_failure_or_malformed_output_never_auto_approves(self):
        failed = validate_resume_text("A short document about work.", lambda _: (_ for _ in ()).throw(RuntimeError()))
        malformed = validate_resume_text("A short document about work.", lambda _: {"classification": "maybe"})
        self.assertEqual(failed["status"], "Needs review")
        self.assertEqual(malformed["status"], "Needs review")

    def test_empty_unreadable_and_image_only_uploads_are_reported(self):
        empty = inspect_resume_file(FakeUpload("empty.pdf", b""), lambda _: "", lambda _: "")
        broken = inspect_resume_file(FakeUpload("broken.pdf", b"not a pdf"), lambda _: "", lambda _: "")
        image_only = inspect_resume_file(FakeUpload("scan.pdf", b"%PDF-1.7 payload"), lambda _: "", lambda _: "")
        self.assertEqual(empty["status"], "Unreadable")
        self.assertEqual(broken["status"], "Unreadable")
        self.assertEqual(image_only["status"], "Unreadable")
        self.assertIn("image-only", image_only["reason"])

    def test_unsupported_file_type_is_rejected(self):
        result = inspect_resume_file(FakeUpload("notes.txt", b"plain text"), lambda _: "", lambda _: "")
        self.assertEqual(result["status"], "Rejected")
        self.assertIn("PDF or DOCX", result["reason"])

    def test_document_signature_and_existing_extractor_are_used(self):
        calls = []
        valid_pdf = FakeUpload("resume.pdf", b"%PDF-1.7 fake content")
        result = inspect_resume_file(
            valid_pdf,
            lambda upload: calls.append(("pdf", upload.name)) or VALID_TEXT,
            lambda upload: calls.append(("docx", upload.name)) or "",
        )
        self.assertEqual(result["status"], "Valid resume")
        self.assertEqual(calls, [("pdf", "resume.pdf")])

        mismatch = inspect_resume_file(FakeUpload("fake.pdf", docx_package()), lambda _: VALID_TEXT, lambda _: VALID_TEXT)
        self.assertEqual(mismatch["status"], "Unreadable")

        docx = inspect_resume_file(FakeUpload("resume.docx", docx_package()), lambda _: "", lambda _: VALID_TEXT)
        self.assertEqual(docx["status"], "Valid resume")

    def test_invalid_documents_never_enter_the_parse_and_score_queue(self):
        outcomes = {
            "good": {"status": "Valid resume"},
            "ambiguous": {"status": "Needs review"},
            "rejected": {"status": "Rejected"},
            "unreadable": {"status": "Unreadable"},
        }
        queue = processable_documents(outcomes, approved_ids={"ambiguous", "rejected"})
        parse_resume = Mock(side_effect=lambda text: {"parsed": text})
        final_score = Mock(return_value={"score": 90})
        for identifier in queue:
            parsed = parse_resume(outcomes[identifier]["status"])
            final_score("job", parsed)
        self.assertEqual(queue, ["good", "ambiguous"])
        self.assertEqual(parse_resume.call_count, 2)
        self.assertEqual(final_score.call_count, 2)
        self.assertEqual([call.args[0] for call in parse_resume.call_args_list], ["Valid resume", "Needs review"])


if __name__ == "__main__":
    unittest.main()
