import streamlit as st

st.set_page_config(
    page_title="HireLens | Resume Analyzer",
    layout="wide",
)

pages = {
    "Workspace": [
        st.Page("pages/0_Dashboard.py", title="Dashboard", default=True),
        st.Page("pages/1_New_Analysis.py", title="New Analysis"),
        st.Page("pages/2_Candidates.py", title="Candidates"),
        st.Page("pages/3_Candidate_Details.py", title="Candidate Details"),
    ]
}

navigation = st.navigation(pages, position="sidebar")
navigation.run()
