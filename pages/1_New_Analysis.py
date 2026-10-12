import time

import streamlit as st

from backend import (
    classify_resume_document,
    final_score,
    parse_job_description,
    parse_resume,
    read_docx,
    read_pdf,
)
from resume_validation import document_id, inspect_resume_file, processable_documents
from job_validation import validate_job_description_text
from ui import apply_styles, page_header, sidebar

apply_styles()
sidebar()
page_header(
    "Candidate matching",
    "New analysis",
    "Validate candidate documents, then compare eligible resumes against the role.",
)

left, right = st.columns([1.1, 0.9], gap="large")
with left:
    with st.container(border=True):
        st.subheader("Job description")
        job_description = st.text_area(
            "Paste role requirements",
            height=270,
            placeholder="Include responsibilities, required skills, and experience...",
            label_visibility="collapsed",
            key="job_description_input",
        )
with right:
    with st.container(border=True):
        st.subheader("Resume files")
        st.caption("Upload PDF or DOCX files. Unsupported formats will be reported and skipped.")
        st.caption(
            "Resume text and extracted details are sent to Groq for AI analysis. "
            "Upload documents only when you have permission to process them."
        )
        uploaded_files = st.file_uploader(
            "Choose documents",
            accept_multiple_files=True,
            max_upload_size=15,
            label_visibility="collapsed",
            key="resume_uploads",
        )
        if uploaded_files:
            st.caption(f"{len(uploaded_files)} document(s) uploaded")
            for resume_file in uploaded_files:
                st.caption(resume_file.name)
        else:
            st.caption("No documents selected yet.")

current_ids = {document_id(item): item for item in uploaded_files or []}
validations = st.session_state.setdefault("resume_validation_results", {})

if st.button("Validate documents", type="secondary", disabled=not current_ids):
    validations = {}
    progress = st.progress(0, text="Checking uploaded documents…")
    for index, (identifier, uploaded_file) in enumerate(current_ids.items()):
        outcome = inspect_resume_file(
            uploaded_file,
            read_pdf=read_pdf,
            read_docx=read_docx,
            classifier=classify_resume_document,
        )
        validations[identifier] = {
            **outcome,
            "filename": uploaded_file.name,
        }
        progress.progress(
            (index + 1) / len(current_ids),
            text=f"Checked {index + 1} of {len(current_ids)} documents",
        )
    st.session_state["resume_validation_results"] = validations

validations = st.session_state.get("resume_validation_results", {})
approved_ids = []
if uploaded_files:
    st.markdown("### Document validation")
    for identifier, uploaded_file in current_ids.items():
        record = validations.get(identifier)
        if not record:
            st.info(f"{uploaded_file.name} · Not validated yet")
            continue

        status = record["status"]
        with st.container(border=True):
            status_col, reason_col = st.columns([0.28, 0.72])
            with status_col:
                st.markdown(f"**{uploaded_file.name}**")
                if status == "Valid resume":
                    st.success(status)
                elif status == "Needs review":
                    st.warning(status)
                else:
                    st.error(status)
            with reason_col:
                st.write(record["reason"])
                if record.get("indicators"):
                    st.caption("Resume indicators found: " + ", ".join(record["indicators"]))
            if status == "Needs review":
                if st.checkbox(
                    "Approve this document for resume analysis",
                    key=f"approve_resume_{identifier}",
                ):
                    approved_ids.append(identifier)

processable_ids = processable_documents(validations, approved_ids)
processable_ids = [identifier for identifier in processable_ids if identifier in current_ids]

if not processable_ids and uploaded_files:
    st.caption("Only validated resumes or documents you explicitly approve can be analyzed.")

submitted = st.button(
    "Analyze valid and approved resumes",
    type="primary",
    width="stretch",
    disabled=not processable_ids,
)

if submitted:
    word_count = len(job_description.split())
    if word_count < 25:
        st.error(f"A job description must contain at least 25 words. This one has {word_count}.")
    else:
        try:
            job = parse_job_description(job_description)
            valid, reason, role = validate_job_description_text(job_description, job)
            if not valid:
                st.error(reason)
            else:
                job.role = role
                results = []
                total_files = len(processable_ids)
                progress = st.progress(0, text="Preparing analysis…")

                for index, identifier in enumerate(processable_ids):
                    record = validations[identifier]
                    filename = record["filename"]
                    progress.progress(
                        index / total_files,
                        text=f"Analyzing {filename} ({index + 1} of {total_files})",
                    )
                    try:
                        # Only validator-approved text reaches the existing parser.
                        parsed_resume = parse_resume(record["text"])
                        time.sleep(5)  # Retain the existing pause between Groq calls.
                        result = final_score(job, parsed_resume)
                        results.append(
                            {
                                "name": parsed_resume.name or filename,
                                "filename": filename,
                                "score": result.score,
                                "details": result.details,
                                "resume": parsed_resume.model_dump(),
                            }
                        )
                    except Exception as error:
                        st.warning(f"Could not analyze {filename}: {error}")
                    progress.progress(
                        (index + 1) / total_files,
                        text=f"Processed {index + 1} of {total_files}",
                    )

                if results:
                    results.sort(key=lambda item: item["score"], reverse=True)
                    st.session_state["results"] = results
                    st.session_state["analysis_complete"] = True
                    st.session_state["analysis_role"] = job.role
                    st.session_state["analysis_job_description"] = job_description
                    st.session_state["analysis_job"] = job.model_dump()
                    first = results[0]
                    st.session_state["selected_candidate_id"] = (
                        first.get("filename"),
                        first.get("name"),
                    )
                    progress.progress(1.0, text="Analysis complete")
                    st.success(f"Analysis complete. {len(results)} candidate(s) ranked.")
                    st.page_link(
                        "pages/2_Candidates.py",
                        label="View candidate rankings",
                        icon=":material/arrow_forward:",
                    )
                else:
                    st.error("No validated resumes could be analyzed successfully.")
        except Exception as error:
            st.error("The job description could not be analyzed. Please try again.")
            st.caption(str(error))
