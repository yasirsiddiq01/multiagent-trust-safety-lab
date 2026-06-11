"""Synthetic multi-agent workflow generator.

The generator produces transparent, controlled traces for research portfolio
demonstration. It does not simulate real LLM internals. Each row represents an
agent action or message in a collaborative workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.config import AGENTS, REQUIRED_COLUMNS, SCENARIOS


@dataclass(frozen=True)
class ScenarioConfig:
    scenario_type: str = "normal_collaboration"
    time_steps: int = 40
    random_seed: int = 42
    affected_agent: str = "All agents"
    guard_mode: str = "trust_guard"


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return float(np.clip(value, low, high))


def _event_type_for_agent(agent: str, step: int, scenario_type: str) -> str:
    if agent == "UserProxy":
        return "user_goal"
    if agent == "Planner":
        return "task_decomposition"
    if agent == "Retriever":
        return "context_retrieval"
    if agent == "ToolExecutor":
        return "tool_call"
    if agent == "CriticVerifier":
        return "verification"
    if agent == "SafetyMonitor":
        return "safety_review"
    return "agent_message"


def _scenario_shock(agent: str, scenario_type: str, step: int, midpoint: int, affected_agent: str) -> dict[str, float]:
    active = step >= midpoint and (affected_agent == "All agents" or affected_agent == agent)
    shock = {
        "evidence_delta": 0.0,
        "confidence_delta": 0.0,
        "hallucination_delta": 0.0,
        "prompt_delta": 0.0,
        "tool_delta": 0.0,
        "policy_delta": 0.0,
        "contradiction_delta": 0.0,
        "value_delta": 0.0,
    }
    if not active:
        return shock

    if scenario_type == "prompt_injection" and agent in {"Retriever", "Planner", "ToolExecutor"}:
        shock.update({"prompt_delta": 48.0, "policy_delta": 15.0, "contradiction_delta": 16.0, "evidence_delta": -12.0})
    elif scenario_type == "hallucinated_evidence" and agent in {"Planner", "Retriever"}:
        shock.update({"hallucination_delta": 42.0, "confidence_delta": 12.0, "evidence_delta": -32.0, "contradiction_delta": 18.0})
    elif scenario_type == "unsafe_tool_request" and agent == "ToolExecutor":
        shock.update({"tool_delta": 55.0, "policy_delta": 38.0, "prompt_delta": 12.0})
    elif scenario_type == "conflicting_values" and agent in {"Planner", "CriticVerifier", "SafetyMonitor"}:
        shock.update({"value_delta": 45.0, "contradiction_delta": 22.0, "policy_delta": 18.0, "evidence_delta": -5.0})
    elif scenario_type == "memory_poisoning" and agent in {"Planner", "Retriever"}:
        shock.update({"hallucination_delta": 30.0, "prompt_delta": 18.0, "evidence_delta": -22.0, "contradiction_delta": 20.0})
    elif scenario_type == "cascading_error":
        # Early unreliable output is accepted by later agents; risk grows with step.
        cascade_factor = min(1.0, (step - midpoint + 1) / max(1, midpoint))
        if agent in {"Planner", "Retriever", "ToolExecutor", "CriticVerifier"}:
            shock.update({
                "hallucination_delta": 28.0 + 18.0 * cascade_factor,
                "contradiction_delta": 20.0 + 20.0 * cascade_factor,
                "policy_delta": 10.0 + 16.0 * cascade_factor,
                "evidence_delta": -20.0,
            })
    return shock


def _message_summary(agent: str, scenario_type: str, step: int, midpoint: int) -> str:
    after = step >= midpoint
    if not after or scenario_type == "normal_collaboration":
        templates = {
            "UserProxy": "User goal is represented as the primary instruction.",
            "Planner": "Planner decomposes the task into verifiable subtasks.",
            "Retriever": "Retriever provides context with sufficient source support.",
            "ToolExecutor": "ToolExecutor proposes an action within normal boundaries.",
            "CriticVerifier": "CriticVerifier checks evidence and consistency.",
            "SafetyMonitor": "SafetyMonitor reviews policy, risk, and approval needs.",
        }
        return templates.get(agent, "Agent contributes to the workflow.")

    if scenario_type == "prompt_injection" and agent == "Retriever":
        return "Retrieved content includes an instruction that conflicts with the user goal."
    if scenario_type == "hallucinated_evidence" and agent == "Planner":
        return "Planner forwards an unsupported claim with high confidence."
    if scenario_type == "unsafe_tool_request" and agent == "ToolExecutor":
        return "ToolExecutor attempts an action that should require blocking or approval."
    if scenario_type == "conflicting_values":
        return "Agent output reflects tension between utility, safety, privacy, and fairness."
    if scenario_type == "memory_poisoning" and agent == "Retriever":
        return "Retrieved memory contains misleading context from an earlier interaction."
    if scenario_type == "cascading_error":
        return "Unreliable upstream information is repeated by downstream agents."
    return "Agent output should be reviewed because the scenario contains degraded conditions."


def generate_trace(
    scenario_type: str = "normal_collaboration",
    time_steps: int = 40,
    random_seed: int = 42,
    affected_agent: str = "All agents",
    guard_mode: str = "trust_guard",
) -> pd.DataFrame:
    """Generate a synthetic multi-agent workflow trace."""

    if scenario_type not in SCENARIOS:
        raise ValueError(f"Unsupported scenario_type: {scenario_type}")

    if time_steps < 5:
        raise ValueError("time_steps must be at least 5")

    rng = np.random.default_rng(random_seed)
    rows: list[dict[str, object]] = []
    midpoint = time_steps // 2

    base_by_agent = {
        "UserProxy": (90, 86, 4, 2, 1, 3, 4, 6),
        "Planner": (82, 78, 12, 8, 7, 10, 14, 18),
        "Retriever": (76, 72, 15, 14, 5, 8, 16, 12),
        "ToolExecutor": (78, 70, 10, 7, 18, 16, 10, 8),
        "CriticVerifier": (84, 76, 8, 5, 3, 9, 8, 12),
        "SafetyMonitor": (88, 74, 6, 4, 5, 12, 6, 10),
    }

    for step in range(time_steps):
        drift = np.sin(step / max(3, time_steps / 8)) * 3.0
        for agent in AGENTS:
            evidence, conf, hall, prompt, tool, policy, contrad, value = base_by_agent[agent]
            noise = rng.normal(0, 3, 8)
            shock = _scenario_shock(agent, scenario_type, step, midpoint, affected_agent)

            row = {
                "step": int(step),
                "agent": agent,
                "event_type": _event_type_for_agent(agent, step, scenario_type),
                "evidence_score": _clip(evidence + drift + noise[0] + shock["evidence_delta"]),
                "confidence": _clip(conf + noise[1] + shock["confidence_delta"]),
                "hallucination_risk": _clip(hall + noise[2] + shock["hallucination_delta"]),
                "prompt_injection_risk": _clip(prompt + noise[3] + shock["prompt_delta"]),
                "tool_risk": _clip(tool + noise[4] + shock["tool_delta"]),
                "policy_risk": _clip(policy + noise[5] + shock["policy_delta"]),
                "contradiction_score": _clip(contrad + noise[6] + shock["contradiction_delta"]),
                "value_conflict_score": _clip(value + noise[7] + shock["value_delta"]),
                "message_summary": _message_summary(agent, scenario_type, step, midpoint),
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    return df[REQUIRED_COLUMNS]


def normalize_uploaded_trace(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize an uploaded CSV trace.

    Missing numeric risk fields are filled with safe defaults so users can test
    simple CSVs without preparing every column manually.
    """
    out = df.copy()

    if "step" not in out.columns:
        out["step"] = np.arange(len(out))
    if "agent" not in out.columns:
        out["agent"] = "UploadedAgent"
    if "event_type" not in out.columns:
        out["event_type"] = "uploaded_event"
    if "message_summary" not in out.columns:
        out["message_summary"] = "Uploaded scenario row."

    defaults = {
        "evidence_score": 70.0,
        "confidence": 70.0,
        "hallucination_risk": 20.0,
        "prompt_injection_risk": 15.0,
        "tool_risk": 15.0,
        "policy_risk": 15.0,
        "contradiction_score": 15.0,
        "value_conflict_score": 15.0,
    }
    for col, default in defaults.items():
        if col not in out.columns:
            out[col] = default
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(default).clip(0, 100)

    out["step"] = pd.to_numeric(out["step"], errors="coerce").fillna(0).astype(int)
    out["agent"] = out["agent"].astype(str)
    out["event_type"] = out["event_type"].astype(str)
    out["message_summary"] = out["message_summary"].astype(str)

    return out[REQUIRED_COLUMNS]
