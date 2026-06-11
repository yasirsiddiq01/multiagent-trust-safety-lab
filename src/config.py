"""Configuration for the Multi-Agent Trust Safety Lab.

This project is a synthetic research demo. It does not call external LLM APIs and
does not claim to evaluate real deployed AI agents. The values below are
transparent parameters used to generate and score agentic workflow traces.
"""

from __future__ import annotations

AGENTS = [
    "UserProxy",
    "Planner",
    "Retriever",
    "ToolExecutor",
    "CriticVerifier",
    "SafetyMonitor",
]

SCENARIOS = {
    "normal_collaboration": {
        "label": "Normal collaboration",
        "description": "Agents coordinate on a benign task with adequate evidence and low risk.",
    },
    "prompt_injection": {
        "label": "Indirect prompt injection",
        "description": "A retrieved document contains hidden instructions that try to override the user goal.",
    },
    "hallucinated_evidence": {
        "label": "Hallucinated evidence",
        "description": "One agent forwards a confident claim without adequate source support.",
    },
    "unsafe_tool_request": {
        "label": "Unsafe tool request",
        "description": "An agent attempts a risky tool action that should require approval or blocking.",
    },
    "conflicting_values": {
        "label": "Conflicting values",
        "description": "Agents disagree across utility, fairness, privacy, safety, and task success.",
    },
    "memory_poisoning": {
        "label": "Memory poisoning",
        "description": "A previous memory entry introduces misleading context into a later decision.",
    },
    "cascading_error": {
        "label": "Cascading error propagation",
        "description": "An early unreliable output is accepted by downstream agents and spreads through the workflow.",
    },
}

GUARD_MODES = {
    "baseline": "Baseline agent flow",
    "trust_guard": "Trust-aware safety guard",
}

REQUIRED_COLUMNS = [
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
    "message_summary",
]

RISK_COLUMNS = [
    "hallucination_risk",
    "prompt_injection_risk",
    "tool_risk",
    "policy_risk",
    "contradiction_score",
    "value_conflict_score",
]

SCORE_WEIGHTS = {
    "evidence_score": 0.22,
    "confidence": 0.12,
    "hallucination_risk": 0.18,
    "prompt_injection_risk": 0.17,
    "tool_risk": 0.15,
    "policy_risk": 0.16,
    "contradiction_score": 0.10,
    "value_conflict_score": 0.10,
}

THRESHOLDS = {
    "hard_fail_risk": 82.0,
    "monitor_risk": 55.0,
    "minimum_trust": 58.0,
    "high_prompt_injection": 70.0,
    "high_hallucination": 68.0,
    "high_tool_risk": 72.0,
    "high_policy_risk": 70.0,
    "high_contradiction": 65.0,
    "high_value_conflict": 65.0,
    "low_evidence": 45.0,
}

STATUS_ORDER = ["Trusted", "Monitor", "Verify", "Quarantine", "Block", "Human approval"]
