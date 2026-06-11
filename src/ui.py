"""Shared Streamlit UI helpers."""

from __future__ import annotations

import streamlit as st


def configure_page() -> None:
    st.set_page_config(
        page_title="Multi-Agent Trust Safety Lab",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str, tone: str = "blue") -> None:
    st.markdown(f'<div class="info-banner {tone}">{text}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, caption: str = "") -> str:
    # Keep the HTML unindented. Streamlit parses markdown before rendering HTML;
    # leading four-space indentation can be interpreted as a code block.
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-caption">{caption}</div>'
        f'</div>'
    )


def status_panel(decision: str) -> None:
    decision = decision.upper()
    if decision == "ALLOW":
        klass = "status-allow"
        msg = "Workflow is currently acceptable under the synthetic safety checks."
    elif decision == "MONITOR":
        klass = "status-monitor"
        msg = "Workflow is usable but should be monitored for degradation."
    elif decision == "VERIFY":
        klass = "status-verify"
        msg = "Workflow requires independent verification before propagation."
    elif decision == "QUARANTINE":
        klass = "status-quarantine"
        msg = "At least one agent output should be quarantined and independently checked."
    else:
        klass = "status-block"
        msg = "At least one agent action should be blocked or require human approval."

    st.markdown(
        f"""
        <div class="status-panel {klass}">
            <div class="status-title">Trust-aware safety decision</div>
            <div class="status-message">{msg}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}

h1 {
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #0b2346;
}

h2, h3 {
    color: #0b2346;
}

section[data-testid="stSidebar"] {
    background: #f7faff;
    border-right: 1px solid #d7e2f2;
}

.sidebar-brand {
    background: linear-gradient(135deg, #06234d 0%, #0b4faa 100%);
    color: white;
    padding: 1.1rem 1rem;
    border-radius: 14px;
    margin-bottom: 1.1rem;
    box-shadow: 0 10px 24px rgba(7, 40, 91, 0.18);
}

.sidebar-title {
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.12;
}

.sidebar-subtitle {
    font-size: 0.8rem;
    opacity: 0.86;
    margin-top: 0.45rem;
}

.nav-note {
    color: #53647d;
    font-size: 0.78rem;
    font-weight: 700;
    margin: 0.7rem 0 0.35rem 0;
    letter-spacing: 0.04em;
}

div[data-testid="stRadio"] > label {
    font-weight: 700;
    color: #0b2346;
}

div[data-testid="stSelectbox"], div[data-testid="stNumberInput"], div[data-testid="stFileUploader"] {
    border: 1px solid #d6e0ef;
    border-radius: 12px;
    padding: 0.45rem 0.55rem;
    background: white;
    margin-bottom: 0.75rem;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    background: #0b5ed7;
    color: white;
    border: none;
    font-weight: 700;
    padding: 0.68rem 1rem;
}

.stButton > button:hover {
    background: #084eb6;
    color: white;
}

.info-banner {
    border-radius: 12px;
    padding: 0.95rem 1.05rem;
    margin: 1.1rem 0;
    border: 1px solid #b7d4fb;
    background: #eaf3ff;
    color: #06478f;
    font-weight: 600;
}

.info-banner.yellow {
    background: #fff7df;
    border-color: #f4d27b;
    color: #7a5200;
}

.info-banner.green {
    background: #e8f8ef;
    border-color: #99dfb7;
    color: #066132;
}

.info-banner.red {
    background: #ffebed;
    border-color: #ffb1bc;
    color: #8a1020;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.2rem 0 1.4rem 0;
}

.metric-card {
    background: white;
    border: 1px solid #d8e3f2;
    border-radius: 16px;
    padding: 1.05rem 1.1rem;
    box-shadow: 0 8px 24px rgba(13, 45, 88, 0.07);
    min-height: 112px;
}

.metric-label {
    color: #50617c;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.metric-value {
    color: #0b5ed7;
    font-weight: 800;
    font-size: 1.85rem;
    margin-top: 0.35rem;
}

.metric-caption {
    color: #67768e;
    font-size: 0.86rem;
    margin-top: 0.25rem;
}

.status-panel {
    border-radius: 16px;
    padding: 1.25rem 1.35rem;
    margin: 1rem 0 1.15rem 0;
    border-left: 6px solid;
}

.status-title {
    font-weight: 800;
    color: #0b2346;
    margin-bottom: 0.35rem;
}

.status-message {
    font-size: 1.15rem;
    font-weight: 800;
}

.status-allow {
    background: #e9f9f0;
    border-color: #0fa15c;
    color: #087440;
}

.status-monitor {
    background: #fff8df;
    border-color: #d59a00;
    color: #8b6100;
}

.status-verify {
    background: #eef4ff;
    border-color: #2d6cdf;
    color: #174ea6;
}

.status-quarantine {
    background: #fff1e8;
    border-color: #ff7a1a;
    color: #a64600;
}

.status-block {
    background: #ffecef;
    border-color: #dc2430;
    color: #9d1722;
}

.card {
    background: white;
    border: 1px solid #d8e3f2;
    border-radius: 16px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 8px 24px rgba(13, 45, 88, 0.06);
    margin-bottom: 1rem;
}

.small-muted {
    color: #66758f;
    font-size: 0.92rem;
}

@media (max-width: 900px) {
    .metric-row {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
"""
