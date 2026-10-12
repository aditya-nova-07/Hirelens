import hashlib
import json

import streamlit as st

from backend import generate_skill_recommendations
from ui import apply_styles, candidates, candidate_label, choose_candidate, detail_value, page_header, show_value_list, sidebar

apply_styles()
sidebar()
page_header("Candidate profile", "Candidate details", "Review the match score and the evidence returned for this candidate.")
values = candidates()
if not values:
    with st.container(border=True):
        st.markdown("### No candidate selected")
        st.write("Analyze resumes to see candidate match details here.")
        st.page_link("pages/1_New_Analysis.py", label="Start a new analysis")
else:
    selected = choose_candidate(values, key="details_candidate")
    details = selected.get("details")
    details = details if isinstance(details, dict) else {}
    try:
        score = max(0.0, min(100.0, float(selected.get("score", 0))))
    except (TypeError, ValueError):
        score = 0.0

    st.markdown(f"## {selected.get('name') or selected.get('filename') or 'Unnamed candidate'}")
    score_col, progress_col = st.columns([0.3, 0.7])
    with score_col:
        st.metric("Match score", f"{score:.1f}%")
    with progress_col:
        st.caption("Overall role match")
        st.progress(score / 100)

    matching = detail_value(details, "Matching skills", "matching_skills")
    missing = detail_value(details, "Missing important skills", "Missing skills", "missing_skills")
    experience = detail_value(details, "Whether the experience requirement is met", "Experience suitability", "experience_suitability", "experience_requirement_met", "experience_met", "experience requirement met")
    verdict = detail_value(details, "A short final verdict", "Final verdict", "Verdict", "final_verdict")

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Matching skills")
            show_value_list(matching)
        with st.container(border=True):
            st.subheader("Experience suitability")
            if experience is None:
                st.caption("Not provided in this analysis.")
            elif isinstance(experience, bool):
                st.success("Requirement met" if experience else "Requirement not met")
            else:
                st.write(experience)
    with right:
        with st.container(border=True):
            st.subheader("Missing skills")
            show_value_list(missing)
        with st.container(border=True):
            st.subheader("Verdict")
            if verdict is not None and str(verdict).strip():
                st.write(verdict)
            else:
                st.caption("No verdict was returned for this candidate.")

    if selected.get("filename"):
        st.caption(f"Source resume: {selected['filename']}")


    st.divider()
    st.markdown("## Improve Yourself")
    st.write("Build practical next steps from this candidate's resume evidence and the role requirements.")

    resume_data = selected.get("resume")
    job_data = st.session_state.get("analysis_job")
    has_recommendation_context = isinstance(resume_data, dict) and isinstance(job_data, dict)
    if not has_recommendation_context:
        st.info("Improvement recommendations are available for candidates analyzed with the current version of HireLens. Run a new analysis to include the resume and role context.")
    else:
        cache_material = json.dumps(
            {
                "candidate": [selected.get("filename"), selected.get("name")],
                "resume": resume_data,
                "job": job_data,
                "details": details,
            },
            sort_keys=True,
            default=str,
        )
        cache_key = hashlib.sha256(cache_material.encode("utf-8")).hexdigest()
        recommendation_cache = st.session_state.setdefault("skill_recommendations", {})
        generate_clicked = st.button(
            "Generate improvement plan",
            type="primary",
            key=f"generate_recommendations_{cache_key[:12]}",
        )
        if generate_clicked and cache_key not in recommendation_cache:
            try:
                with st.spinner("Building a role-specific improvement plan?"):
                    recommendation_cache[cache_key] = generate_skill_recommendations(
                        resume_data,
                        job_data,
                        details,
                    )
                st.session_state["skill_recommendations"] = recommendation_cache
            except Exception as error:
                st.error("Could not generate recommendations right now. You can try again.")
                st.caption(str(error))

        if cache_key in recommendation_cache:
            recommendations = recommendation_cache[cache_key]
            if not recommendations:
                st.info("No additional development recommendations were identified from the available role and resume data.")
            for recommendation in recommendations:
                with st.container(border=True):
                    title_col, priority_col = st.columns([0.78, 0.22])
                    with title_col:
                        st.markdown(f"### {recommendation['skill']}")
                        st.caption(recommendation["category"])
                    with priority_col:
                        st.metric("Priority", recommendation["priority"])
                    st.markdown("**Why it matters for this role**")
                    st.write(recommendation["role_relevance"])
                    st.markdown("**Current evidence**")
                    st.write(recommendation["candidate_evidence"])
                    st.markdown("**Practice action**")
                    st.write(recommendation["learning_action"])
                    if recommendation.get("estimated_time"):
                        st.caption(f"Estimated learning time: {recommendation['estimated_time']}")
