from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          color-scheme: light;
          --hl-canvas:#f4f7fb; --hl-surface:#ffffff; --hl-surface-soft:#edf3fa;
          --hl-ink:#17263d; --hl-muted:#53657c; --hl-line:#d8e2ee;
          --hl-blue:#2563eb; --hl-blue-hover:#1d4ed8; --hl-accent:#60a5fa;
          --hl-shadow:0 8px 24px rgba(20,42,74,.06);
        }
        :root[data-theme="dark"], body[data-theme="dark"], [data-theme="dark"] {
          color-scheme:dark;
          --hl-canvas:#0b1220; --hl-surface:#121d2e; --hl-surface-soft:#19283c;
          --hl-ink:#edf4ff; --hl-muted:#bac9dd; --hl-line:#304158;
          --hl-blue:#3b82f6; --hl-blue-hover:#60a5fa; --hl-accent:#93c5fd;
          --hl-shadow:0 8px 24px rgba(0,0,0,.20);
        }
        .stApp { background:var(--hl-canvas); color:var(--hl-ink); }
        .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] { color:var(--hl-ink); }
        .block-container { max-width:1240px; padding-top:1.8rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:#101b2b; color:#e8f0fb; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#dce7f5; }
        [data-testid="stSidebar"] hr { border-color:#33445b; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] { padding-top:.35rem; }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
          color:#e8f0fb !important; background:transparent; border-radius:10px;
          margin:.12rem 0; transition:background-color .12s ease;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] * { color:inherit !important; }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
          color:#fff !important; background:#243b5d;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:focus-visible {
          outline:2px solid #7db5ff; outline-offset:2px; color:#fff !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
          color:#fff !important; background:#1d4ed8; font-weight:650;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] * { color:#fff !important; }
        [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] { color:#9fb2ca !important; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a { border-radius:10px; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background:#243b5d; }
        .brand { font-size:1.6rem; font-weight:760; letter-spacing:-.045em; color:#fff; }
        .brand span { color:#7db5ff; }
        .sidebar-tagline { color:#c3d2e7 !important; font-size:.82rem; line-height:1.5; margin-top:.25rem; }
        .eyebrow { color:var(--hl-blue); font-size:.74rem; font-weight:750; letter-spacing:.13em; text-transform:uppercase; }
        .hero { background:linear-gradient(120deg,var(--hl-surface),var(--hl-surface-soft)); border:1px solid var(--hl-line); border-radius:20px; padding:1.55rem 1.8rem; margin-bottom:1.3rem; box-shadow:var(--hl-shadow); }
        .hero h1 { color:var(--hl-ink); letter-spacing:-.035em; margin:.28rem 0 .4rem; }
        .hero p { color:var(--hl-muted); margin-bottom:0; line-height:1.55; }
        div[data-testid="stMetric"] { background:var(--hl-surface); border:1px solid var(--hl-line); border-radius:15px; padding:1rem 1.2rem; box-shadow:var(--hl-shadow); }
        div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] { color:var(--hl-muted); }
        div[data-testid="stVerticalBlockBorderWrapper"] { background:var(--hl-surface); border-color:var(--hl-line); border-radius:16px; box-shadow:var(--hl-shadow); }
        .stButton > button[kind="primary"] { background:var(--hl-blue); border-color:var(--hl-blue); border-radius:10px; font-weight:680; min-height:2.85rem; color:#fff; }
        .stButton > button[kind="primary"]:hover { background:var(--hl-blue-hover); border-color:var(--hl-blue-hover); color:#fff; }
        .stButton > button:disabled { opacity:.62; cursor:not-allowed; }
        [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] [role="combobox"], [data-testid="stMultiSelect"] [role="combobox"] {
          background:var(--hl-surface); color:var(--hl-ink); border-color:var(--hl-line); border-radius:10px;
        }
        [data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder { color:var(--hl-muted); opacity:1; }
        [data-testid="stFileUploader"] { background:var(--hl-surface-soft); border:1px dashed var(--hl-line); border-radius:12px; padding:.35rem; }
        [data-testid="stFileUploader"] button { border-radius:8px; }
        [data-testid="stDataFrame"] { border:1px solid var(--hl-line); border-radius:12px; overflow:hidden; }
        [data-testid="stCaptionContainer"], .stCaption { color:var(--hl-muted); }
        [role="listbox"], [role="option"] { background:var(--hl-surface); color:var(--hl-ink); }
        [data-testid="stProgress"] { accent-color:var(--hl-blue); }
        @media(max-width:700px) { .block-container { padding:1rem .85rem 2rem; } .hero { padding:1.2rem; border-radius:16px; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="brand">Hire<span>Lens</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">See the Match. Understand the Potential.</div>', unsafe_allow_html=True)
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
