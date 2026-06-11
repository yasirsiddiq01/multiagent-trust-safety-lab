import pandas as pd

from src.generator import generate_trace
from src.safety import score_trace, summarize_decision, decision_paragraph


def test_score_trace_adds_decision_columns():
    df = generate_trace("unsafe_tool_request", time_steps=12, random_seed=2)
    scored = score_trace(df)
    for col in ["trust_score", "mean_risk", "status", "recommended_action", "allowed_to_propagate"]:
        assert col in scored.columns


def test_scores_are_bounded():
    df = generate_trace("cascading_error", time_steps=12, random_seed=2)
    scored = score_trace(df)
    assert scored["trust_score"].between(0, 100).all()
    assert scored["mean_risk"].between(0, 100).all()


def test_unsafe_tool_request_has_block_event():
    df = generate_trace("unsafe_tool_request", time_steps=20, random_seed=3, affected_agent="ToolExecutor")
    scored = score_trace(df)
    assert (scored["status"] == "Block").any()


def test_summary_contains_expected_keys():
    df = generate_trace("prompt_injection", time_steps=20, random_seed=4)
    scored = score_trace(df)
    summary = summarize_decision(scored)
    assert summary["workflow_decision"] in {"ALLOW", "MONITOR", "VERIFY", "QUARANTINE", "BLOCK"}
    assert "trust_by_agent" in summary


def test_decision_paragraph_mentions_synthetic_signal():
    df = generate_trace("prompt_injection", time_steps=20, random_seed=4)
    scored = score_trace(df)
    summary = summarize_decision(scored)
    paragraph = decision_paragraph(summary, "Indirect prompt injection")
    assert "synthetic agent-safety signal" in paragraph
