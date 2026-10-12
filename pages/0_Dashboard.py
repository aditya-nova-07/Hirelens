import streamlit as st

from ui import apply_styles, candidates, page_header, sidebar

apply_styles()
sidebar()
page_header("Workspace", "Welcome to HireLens", "A focused view of candidate fit, from resume upload to ranked shortlist.")

results = candidates()
if results:
    try:
        top_score = max(float(item.get("score", 0)) for item in results)
    except (TypeError, ValueError):
        top_score = 0.0

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Candidates analyzed", len(results))
    metric_b.metric("Highest match", f"{top_score:.1f}%")
    metric_c.metric("Latest role", st.session_state.get("analysis_role") or "Analysis complete")

    st.markdown("### Recent candidates")
    ranking = sorted(results, key=lambda item: float(item.get("score", 0)), reverse=True)
    st.dataframe(
        [{"Rank": i + 1, "Candidate": item.get("name") or item.get("filename") or "Unnamed candidate",
          "Match": f"{float(item.get('score', 0)):.1f}%", "Resume": item.get("filename", "—")}
         for i, item in enumerate(ranking[:5])],
        width="stretch", hide_index=True,
    )
    st.page_link("pages/2_Candidates.py", label="View all candidates", icon=":material/arrow_forward:")
else:
    with st.container(border=True):
        st.markdown("### Your candidate workspace is ready")
        st.write("Start with a job description and a set of resumes. HireLens will rank the candidates and keep the results available as you move between pages.")
        st.page_link("pages/1_New_Analysis.py", label="Start a new analysis", icon=":material/arrow_forward:")

st.markdown("### Quick action")
st.page_link("pages/1_New_Analysis.py", label="New analysis")
