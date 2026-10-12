from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#172b3a; --muted:#71818a; --teal:#14836e; --line:#e5eceb; --canvas:#f5f8f7; }
        .stApp { background:var(--canvas); color:var(--ink); }
        .block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:#102a3a; }
        [data-testid="stSidebar"] * { color:#e9f2f3; }
        [data-testid="stSidebar"] hr { border-color:#294452; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a { border-radius:9px; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background:#1b3b4b; }
        .brand { font-size:1.55rem; font-weight:750; letter-spacing:-.04em; color:#fff; }
        .brand span { color:#5bd0ad; }
        .eyebrow { color:var(--teal); font-size:.75rem; font-weight:750; letter-spacing:.13em; text-transform:uppercase; }
        .hero { background:linear-gradient(120deg,#fff,#f2faf7); border:1px solid var(--line); border-radius:20px; padding:1.6rem 1.8rem; margin-bottom:1.3rem; }
        .hero p { color:var(--muted); margin-bottom:0; }
        div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:15px; padding:1rem 1.2rem; box-shadow:0 5px 18px #203b3b08; }
        div[data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-color:var(--line); border-radius:16px; }
        .stButton > button[kind="primary"] { background:var(--teal); border-color:var(--teal); border-radius:10px; font-weight:650; min-height:2.8rem; }
        .stButton > button[kind="primary"]:hover { background:#0f6d5b; border-color:#0f6d5b; }
        div[data-testid="stFileUploader"] { background:#fbfdfc; border:1px dashed #a5c4ba; border-radius:12px; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
        @media(max-width:700px) { .block-container { padding:1rem .85rem 2rem; } .hero { padding:1.2rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="brand">Hire<span>Lens</span></div>', unsafe_allow_html=True)
        st.caption("AI recruiting workspace")
        st.divider()
        st.caption("Resume matching, made clearer.")


def page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f'<section class="hero"><div class="eyebrow">{kicker}</div>'
        f'<h1>{title}</h1><p>{description}</p></section>',
        unsafe_allow_html=True,
    )


def candidates() -> list[dict]:
    values = st.session_state.get("results", [])
    return values if isinstance(values, list) else []


def candidate_label(candidate: dict) -> str:
    try:
        score = float(candidate.get("score", 0))
    except (TypeError, ValueError):
        score = 0.0
    return f"{candidate.get('name') or candidate.get('filename') or 'Unnamed candidate'} · {score:.1f}%"


def selected_candidate() -> dict | None:
    values = candidates()
    if not values:
        return None
    identity = st.session_state.get("selected_candidate_id")
    for item in values:
        if identity == (item.get("filename"), item.get("name")):
            return item
    return values[0]


def choose_candidate(values: list[dict], key: str = "candidate_choice") -> dict:
    identity = st.session_state.get("selected_candidate_id")
    default_index = next(
        (i for i, item in enumerate(values)
         if identity == (item.get("filename"), item.get("name"))),
        0,
    )
    index = st.selectbox(
        "Select a candidate", range(len(values)), index=default_index,
        format_func=lambda i: candidate_label(values[i]), key=key,
    )
    result = values[index]
    st.session_state["selected_candidate_id"] = (result.get("filename"), result.get("name"))
    return result


def detail_value(details: dict, *labels: str):
    normalized = {str(key).strip().lower().replace("_", " "): value for key, value in details.items()}
    for label in labels:
        key = label.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]
    return None


def show_value_list(value) -> None:
    if isinstance(value, (list, tuple, set)):
        values = [str(item).strip() for item in value if str(item).strip()]
        if values:
            st.write(" · ".join(values))
        else:
            st.caption("No items returned.")
    elif value is not None and str(value).strip():
        st.write(value)
    else:
        st.caption("Not provided in this analysis.")
