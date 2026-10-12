import streamlit as st

import backend
from ui import apply_styles, candidates, candidate_label, page_header, sidebar

apply_styles()
sidebar()
page_header("Shortlist", "Candidates", "Explore the ranked results and open a candidate profile.")
values = candidates()
if not values:
    with st.container(border=True):
        st.markdown("### No candidates to show yet")
        st.write("Run a new analysis to build your ranked shortlist.")
        st.page_link("pages/1_New_Analysis.py", label="Start a new analysis")
else:
    sort_order = st.selectbox("Sort candidates", ["Highest match first", "Lowest match first", "Name A–Z"])
    if sort_order == "Lowest match first":
        ranked = sorted(values, key=lambda item: float(item.get("score", 0)))
    elif sort_order == "Name A–Z":
        ranked = sorted(values, key=lambda item: str(item.get("name", "")).casefold())
    else:
        ranked = sorted(values, key=lambda item: float(item.get("score", 0)), reverse=True)
    st.dataframe(
        [{"Rank": i + 1, "Candidate": item.get("name") or item.get("filename") or "Unnamed candidate",
          "Match score": f"{float(item.get('score', 0)):.1f}%", "Resume": item.get("filename", "—")}
         for i, item in enumerate(ranked)],
        width="stretch", hide_index=True,
    )
    st.markdown("### Inspect a candidate")
    choice = st.selectbox("Choose a candidate", range(len(ranked)), format_func=lambda i: candidate_label(ranked[i]), key="ranked_candidate")
    selected = ranked[choice]
    st.session_state["selected_candidate_id"] = (selected.get("filename"), selected.get("name"))
    st.page_link("pages/3_Candidate_Details.py", label="Open candidate details", icon=":material/arrow_forward:")
