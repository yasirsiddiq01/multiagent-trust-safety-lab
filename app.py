from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import AGENTS, GUARD_MODES, SCENARIOS
from src.generator import generate_trace, normalize_uploaded_trace
from src.reporting import generate_markdown_report
from src.safety import decision_paragraph, score_trace, summarize_decision
from src.ui import badge, configure_page, metric_card, status_panel


def run_analysis(
    scenario_type: str,
    affected_agent: str,
    time_steps: int,
    random_seed: int,
    guard_mode: str,
    uploaded_file,
) -> None:
    if uploaded_file is not None:
        uploaded = pd.read_csv(uploaded_file)
        trace = normalize_uploaded_trace(uploaded)
        scenario_label = "Uploaded CSV scenario"
    else:
        trace = generate_trace(
            scenario_type=scenario_type,
            time_steps=time_steps,
            random_seed=random_seed,
            affected_agent=affected_agent,
            guard_mode=guard_mode,
        )
        scenario_label = SCENARIOS[scenario_type]["label"]

    scored = score_trace(trace, guard_mode=guard_mode)
    summary = summarize_decision(scored, guard_mode=guard_mode)
    explanation = decision_paragraph(summary, scenario_label, guard_mode=guard_mode)
    report = generate_markdown_report(
        scenario_label=scenario_label,
        guard_mode_label=GUARD_MODES[guard_mode],
        scored=scored,
        summary=summary,
        explanation=explanation,
    )

    st.session_state["analysis"] = {
        "trace": trace,
        "scored": scored,
        "summary": summary,
        "explanation": explanation,
        "report": report,
        "scenario_label": scenario_label,
        "guard_mode_label": GUARD_MODES[guard_mode],
    }


def sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-title">Multi-Agent<br>Trust Safety Lab</div>
                <div class="sidebar-subtitle">Synthetic trust-aware safety testbed for agentic AI workflows</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="nav-note">NAVIGATION</div>', unsafe_allow_html=True)
        section = st.radio(
            "Choose section",
            ["Decision Dashboard", "Risk and Trace Analysis", "About and Help"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown('<div class="nav-note">SCENARIO SETUP</div>', unsafe_allow_html=True)

        with st.form("scenario_form"):
            scenario_label_to_key = {v["label"]: k for k, v in SCENARIOS.items()}
            scenario_label = st.selectbox("Scenario type", list(scenario_label_to_key.keys()), index=1)
            scenario_type = scenario_label_to_key[scenario_label]

            affected_agent = st.selectbox("Affected agent after midpoint", ["All agents"] + AGENTS)
            guard_label_to_key = {v: k for k, v in GUARD_MODES.items()}
            guard_label = st.selectbox("Evaluation mode", list(guard_label_to_key.keys()), index=1)
            guard_mode = guard_label_to_key[guard_label]

            time_steps = st.number_input("Workflow steps", min_value=8, max_value=120, value=40, step=1)
            random_seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
            uploaded_file = st.file_uploader("Optional CSV upload", type=["csv"])

            submitted = st.form_submit_button("Run safety analysis")
            if submitted:
                run_analysis(
                    scenario_type=scenario_type,
                    affected_agent=affected_agent,
                    time_steps=int(time_steps),
                    random_seed=int(random_seed),
                    guard_mode=guard_mode,
                    uploaded_file=uploaded_file,
                )

        st.markdown(
            '<p class="small-muted">Change values first, then press the button. Results do not recalculate automatically.</p>',
            unsafe_allow_html=True,
        )

    return section


def get_analysis():
    if "analysis" not in st.session_state:
        run_analysis(
            scenario_type="prompt_injection",
            affected_agent="All agents",
            time_steps=40,
            random_seed=42,
            guard_mode="trust_guard",
            uploaded_file=None,
        )
    return st.session_state["analysis"]


def decision_dashboard() -> None:
    analysis = get_analysis()
    summary = analysis["summary"]
    scored = analysis["scored"]

    st.title("Multi-Agent Trust Safety Lab")
    st.caption("Synthetic trust-aware safety demo for agentic AI and multi-agent collaboration research.")
    badge("This is a research-oriented synthetic safety demo. It does not claim to evaluate or secure a real deployed LLM agent system.")

    metrics = [
        ("Workflow decision", str(summary["workflow_decision"]), analysis["scenario_label"]),
        ("Mean trust score", f'{summary["mean_trust_score"]}/100', "Average across agent steps"),
        ("Contained events", str(summary["contained_events"]), "Blocked/quarantined/verified by guard"),
        ("Riskiest agent", str(summary["riskiest_agent"]), "Highest observed max risk"),
    ]
    st.markdown(
        '<div class="metric-row">' + "".join(metric_card(*m) for m in metrics) + "</div>",
        unsafe_allow_html=True,
    )

    status_panel(str(summary["workflow_decision"]))

    st.subheader("Safety decision explanation")
    st.write(analysis["explanation"])

    with st.expander("Warning and fail conditions", expanded=True):
        for warning in summary["warnings"]:
            st.write(f"- {warning}")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Markdown report",
            data=analysis["report"],
            file_name="multiagent_trust_safety_report.md",
            mime="text/markdown",
        )
    with col2:
        st.download_button(
            "Download scored CSV",
            data=scored.to_csv(index=False),
            file_name="multiagent_trust_safety_scored_trace.csv",
            mime="text/csv",
        )

    st.subheader("Latest step decision table")
    latest_cols = [
        "agent",
        "trust_score",
        "mean_risk",
        "max_risk",
        "status",
        "recommended_action",
        "message_summary",
    ]
    st.dataframe(summary["latest"][latest_cols].round(1), use_container_width=True, hide_index=True)


def risk_and_trace_analysis() -> None:
    analysis = get_analysis()
    scored = analysis["scored"]
    summary = analysis["summary"]

    st.title("Risk and Trace Analysis")
    st.caption("Detailed KPI-style analysis for trust, risk, containment, and propagation behaviour.")

    badge("Results reflect the most recent safety-analysis run. Use the sidebar to configure a scenario and press Run safety analysis.")

    st.subheader("Trust score over time")
    trust_pivot = scored.pivot_table(index="step", columns="agent", values="trust_score", aggfunc="mean")
    st.line_chart(trust_pivot)

    st.subheader("Risk score over time")
    risk_pivot = scored.pivot_table(index="step", columns="agent", values="mean_risk", aggfunc="mean")
    st.line_chart(risk_pivot)

    st.subheader("Agent-level summary")
    agent_summary = summary["trust_by_agent"].copy()
    st.dataframe(agent_summary.round(1), use_container_width=True, hide_index=True)

    st.subheader("Status distribution")
    status_counts = scored["status"].value_counts().rename_axis("status").reset_index(name="count")
    st.bar_chart(status_counts, x="status", y="count")

    st.subheader("Full scored trace")
    display_cols = [
        "step",
        "agent",
        "event_type",
        "evidence_score",
        "confidence",
        "hallucination_risk",
        "prompt_injection_risk",
        "tool_risk",
        "policy_risk",
        "contradiction_score",
        "value_conflict_score",
        "trust_score",
        "status",
        "recommended_action",
        "message_summary",
    ]
    st.dataframe(scored[display_cols].round(1), use_container_width=True, hide_index=True)


def about_and_help() -> None:
    st.title("About and Help")
    st.caption("Purpose, workflow, interpretation, CSV format, and limitations.")

    badge(
        "Multi-Agent Trust Safety Lab is a synthetic testbed for studying trust-aware safety decisions in agentic AI workflows. It is designed for research portfolio use, not real safety certification.",
        tone="blue",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="card">
            <h3>What this project does</h3>
            <p>The tool generates or accepts a multi-agent workflow trace and scores each agent step using transparent safety indicators.</p>
            <ul>
              <li>Models prompt injection, hallucinated evidence, unsafe tool use, value conflict, memory poisoning, and cascading error.</li>
              <li>Computes trust score, risk score, status, and recommended action.</li>
              <li>Shows whether the workflow should be allowed, monitored, verified, quarantined, or blocked.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="card">
            <h3>How to use the dashboard</h3>
            <ol>
              <li>Select a scenario from the sidebar.</li>
              <li>Select the affected agent and evaluation mode.</li>
              <li>Set workflow steps and random seed.</li>
              <li>Optionally upload a CSV trace.</li>
              <li>Press <b>Run safety analysis</b>.</li>
              <li>Review decision, warnings, graphs, trace table, and download reports.</li>
            </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            """
            <div class="card">
            <h3>How to read the score</h3>
            <p>The trust score ranges from 0 to 100. Higher values indicate stronger evidence, lower risk, and better suitability for propagation inside this synthetic workflow.</p>
            <p>Hard safety risks can still trigger <b>Block</b> or <b>Quarantine</b> even when some scores look acceptable.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
            <div class="card">
            <h3>Important limitations</h3>
            <ul>
              <li>No real LLM API is called.</li>
              <li>No real agent system is certified or secured.</li>
              <li>Scores are synthetic and rule-based.</li>
              <li>The demo is intended to support research discussion and portfolio evidence.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("CSV upload format")
    st.write("A CSV may include these columns. Missing numeric fields are filled with safe defaults.")
    st.code(
        "step,agent,event_type,evidence_score,confidence,hallucination_risk,prompt_injection_risk,tool_risk,policy_risk,contradiction_score,value_conflict_score,message_summary",
        language="text",
    )

    st.subheader("Research positioning")
    st.write(
        "This project is suitable for applications related to agentic AI safety, multi-agent collaboration, prompt injection, tool-use risk, value-aware negotiation, trust/reputation, and cascading-error containment."
    )


def main() -> None:
    configure_page()
    section = sidebar()

    if section == "Decision Dashboard":
        decision_dashboard()
    elif section == "Risk and Trace Analysis":
        risk_and_trace_analysis()
    else:
        about_and_help()


if __name__ == "__main__":
    main()
