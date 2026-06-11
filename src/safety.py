"""Trust-aware safety scoring and decision logic for synthetic agent traces."""

from __future__ import annotations

import pandas as pd
import numpy as np

from src.config import RISK_COLUMNS, SCORE_WEIGHTS, THRESHOLDS


def _bounded(series: pd.Series) -> pd.Series:
    return series.astype(float).clip(0, 100)


def score_trace(df: pd.DataFrame, guard_mode: str = "trust_guard") -> pd.DataFrame:
    """Add trust, risk, status, and recommended action columns to a trace."""
    out = df.copy()

    for col in [
        "evidence_score",
        "confidence",
        "hallucination_risk",
        "prompt_injection_risk",
        "tool_risk",
        "policy_risk",
        "contradiction_score",
        "value_conflict_score",
    ]:
        out[col] = _bounded(out[col])

    out["mean_risk"] = out[RISK_COLUMNS].mean(axis=1)
    out["max_risk"] = out[RISK_COLUMNS].max(axis=1)

    risk_penalty = (
        SCORE_WEIGHTS["hallucination_risk"] * out["hallucination_risk"]
        + SCORE_WEIGHTS["prompt_injection_risk"] * out["prompt_injection_risk"]
        + SCORE_WEIGHTS["tool_risk"] * out["tool_risk"]
        + SCORE_WEIGHTS["policy_risk"] * out["policy_risk"]
        + SCORE_WEIGHTS["contradiction_score"] * out["contradiction_score"]
        + SCORE_WEIGHTS["value_conflict_score"] * out["value_conflict_score"]
    )
    positive = (
        SCORE_WEIGHTS["evidence_score"] * out["evidence_score"]
        + SCORE_WEIGHTS["confidence"] * out["confidence"]
    )
    # Scale to an intuitive 0-100 score. High evidence and confidence help, but
    # risk dominates because this demo is safety-oriented.
    out["trust_score"] = (78 + positive - risk_penalty).clip(0, 100)

    if guard_mode == "trust_guard":
        out["guard_adjusted_risk"] = (
            out["mean_risk"]
            - 0.22 * out["evidence_score"]
            + 0.10 * out["contradiction_score"]
        ).clip(0, 100)
    else:
        out["guard_adjusted_risk"] = out["mean_risk"]

    out["status"] = out.apply(_classify_status, axis=1)
    out["recommended_action"] = out.apply(_recommended_action, axis=1)
    out["allowed_to_propagate"] = out["recommended_action"].isin(
        ["Allow", "Allow with monitoring", "Verify before propagation"]
    )
    return out


def _classify_status(row: pd.Series) -> str:
    if row["tool_risk"] >= THRESHOLDS["high_tool_risk"] or row["policy_risk"] >= THRESHOLDS["high_policy_risk"]:
        return "Block"
    if row["prompt_injection_risk"] >= THRESHOLDS["high_prompt_injection"]:
        return "Quarantine"
    if row["hallucination_risk"] >= THRESHOLDS["high_hallucination"] and row["evidence_score"] < THRESHOLDS["low_evidence"]:
        return "Quarantine"
    if row["contradiction_score"] >= THRESHOLDS["high_contradiction"] or row["value_conflict_score"] >= THRESHOLDS["high_value_conflict"]:
        return "Verify"
    if row["trust_score"] < THRESHOLDS["minimum_trust"] or row["max_risk"] >= THRESHOLDS["monitor_risk"]:
        return "Monitor"
    return "Trusted"


def _recommended_action(row: pd.Series) -> str:
    if row["status"] == "Block":
        return "Block or require human approval"
    if row["status"] == "Quarantine":
        return "Quarantine output and request independent verification"
    if row["status"] == "Verify":
        return "Verify before propagation"
    if row["status"] == "Monitor":
        return "Allow with monitoring"
    return "Allow"


def summarize_decision(scored: pd.DataFrame, guard_mode: str = "trust_guard") -> dict[str, object]:
    """Summarize the workflow-level safety decision."""
    latest_step = int(scored["step"].max())
    latest = scored[scored["step"] == latest_step].copy()

    blocked = scored[scored["status"] == "Block"]
    quarantined = scored[scored["status"] == "Quarantine"]
    verify = scored[scored["status"] == "Verify"]

    baseline_attack_events = int(
        (
            (scored["prompt_injection_risk"] >= THRESHOLDS["high_prompt_injection"])
            | (scored["tool_risk"] >= THRESHOLDS["high_tool_risk"])
            | (scored["policy_risk"] >= THRESHOLDS["high_policy_risk"])
        ).sum()
    )

    contained_events = int((~scored["allowed_to_propagate"]).sum()) if guard_mode == "trust_guard" else 0
    safe_completion_rate = float((scored["allowed_to_propagate"].mean()) * 100)

    trust_by_agent = (
        scored.groupby("agent", as_index=False)
        .agg(
            mean_trust_score=("trust_score", "mean"),
            mean_risk=("mean_risk", "mean"),
            max_risk=("max_risk", "max"),
            blocked_or_quarantined=("status", lambda x: int(x.isin(["Block", "Quarantine"]).sum())),
        )
        .sort_values(["mean_trust_score", "mean_risk"], ascending=[False, True])
    )

    highest_trust_agent = str(trust_by_agent.iloc[0]["agent"])
    riskiest_agent = str(trust_by_agent.sort_values("max_risk", ascending=False).iloc[0]["agent"])
    latest_decision = _workflow_decision(latest)

    warnings = build_warnings(scored)

    return {
        "latest_step": latest_step,
        "workflow_decision": latest_decision,
        "highest_trust_agent": highest_trust_agent,
        "riskiest_agent": riskiest_agent,
        "blocked_count": int(len(blocked)),
        "quarantined_count": int(len(quarantined)),
        "verify_count": int(len(verify)),
        "contained_events": contained_events,
        "attack_like_events": baseline_attack_events,
        "safe_completion_rate": round(safe_completion_rate, 1),
        "mean_trust_score": round(float(scored["trust_score"].mean()), 1),
        "mean_risk": round(float(scored["mean_risk"].mean()), 1),
        "warnings": warnings,
        "trust_by_agent": trust_by_agent,
        "latest": latest,
    }


def _workflow_decision(latest: pd.DataFrame) -> str:
    statuses = set(latest["status"].tolist())
    if "Block" in statuses:
        return "BLOCK"
    if "Quarantine" in statuses:
        return "QUARANTINE"
    if "Verify" in statuses:
        return "VERIFY"
    if "Monitor" in statuses:
        return "MONITOR"
    return "ALLOW"


def build_warnings(scored: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    if (scored["prompt_injection_risk"] >= THRESHOLDS["high_prompt_injection"]).any():
        warnings.append("Prompt-injection risk crossed the quarantine threshold in at least one agent step.")
    if (scored["hallucination_risk"] >= THRESHOLDS["high_hallucination"]).any():
        warnings.append("Hallucination risk crossed the high-risk threshold in at least one agent step.")
    if (scored["tool_risk"] >= THRESHOLDS["high_tool_risk"]).any():
        warnings.append("Tool-use risk crossed the blocking threshold in at least one agent step.")
    if (scored["policy_risk"] >= THRESHOLDS["high_policy_risk"]).any():
        warnings.append("Policy risk crossed the blocking threshold in at least one agent step.")
    if (scored["contradiction_score"] >= THRESHOLDS["high_contradiction"]).any():
        warnings.append("Contradiction score crossed the verification threshold in at least one agent step.")
    if not warnings:
        warnings.append("No high-risk threshold was crossed in this synthetic run.")
    return warnings


def decision_paragraph(summary: dict[str, object], scenario_label: str, guard_mode: str = "trust_guard") -> str:
    """Create an engineer-style explanation for the main dashboard."""
    decision = str(summary["workflow_decision"])
    mean_trust = summary["mean_trust_score"]
    mean_risk = summary["mean_risk"]
    riskiest = summary["riskiest_agent"]
    highest = summary["highest_trust_agent"]
    blocked = summary["blocked_count"]
    quarantined = summary["quarantined_count"]
    verify = summary["verify_count"]
    contained = summary["contained_events"]
    mode = "trust-aware safety guard" if guard_mode == "trust_guard" else "baseline flow"

    return (
        f"The workflow decision is {decision}. This result was produced under the {scenario_label} scenario using the {mode}. "
        f"The average trust score across agent steps is {mean_trust}/100 and the average risk score is {mean_risk}/100. "
        f"The strongest average contributor is {highest}, while the riskiest agent in this run is {riskiest}. "
        f"The safety layer identified {blocked} block-level events, {quarantined} quarantine-level events, and {verify} verification-level events. "
        f"Contained events: {contained}. The score should be read as a synthetic agent-safety signal, not as proof that a real deployed LLM agent is safe."
    )
