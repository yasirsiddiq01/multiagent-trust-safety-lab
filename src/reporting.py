"""Report generation utilities."""

from __future__ import annotations

import pandas as pd


def generate_markdown_report(
    scenario_label: str,
    guard_mode_label: str,
    scored: pd.DataFrame,
    summary: dict[str, object],
    explanation: str,
) -> str:
    latest = summary["latest"].copy()
    latest_small = latest[
        [
            "agent",
            "trust_score",
            "mean_risk",
            "max_risk",
            "status",
            "recommended_action",
        ]
    ].round(1)

    by_agent = summary["trust_by_agent"].copy().round(1)

    warnings = "\n".join([f"- {w}" for w in summary["warnings"]])

    return f"""# Multi-Agent Trust Safety Lab Report

## Scenario

- Scenario: {scenario_label}
- Guard mode: {guard_mode_label}
- Workflow decision: {summary["workflow_decision"]}
- Mean trust score: {summary["mean_trust_score"]}/100
- Mean risk score: {summary["mean_risk"]}/100
- Highest-trust agent: {summary["highest_trust_agent"]}
- Riskiest agent: {summary["riskiest_agent"]}
- Block-level events: {summary["blocked_count"]}
- Quarantine-level events: {summary["quarantined_count"]}
- Verification-level events: {summary["verify_count"]}
- Contained events: {summary["contained_events"]}
- Safe completion rate: {summary["safe_completion_rate"]}%

## Decision explanation

{explanation}

## Warning and fail conditions

{warnings}

## Latest step agent decisions

{latest_small.to_markdown(index=False)}

## Agent-level aggregate summary

{by_agent.to_markdown(index=False)}

## Important limitation

This is a research-oriented synthetic safety demo for multi-agent workflows. It does not call real LLMs, does not evaluate a deployed agent system, and should not be used as a real security or safety certification tool.
"""
