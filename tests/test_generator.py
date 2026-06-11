import pandas as pd

from src.config import REQUIRED_COLUMNS
from src.generator import generate_trace, normalize_uploaded_trace


def test_generate_trace_has_required_columns():
    df = generate_trace(time_steps=10, random_seed=1)
    assert list(df.columns) == REQUIRED_COLUMNS
    assert len(df) == 10 * 6


def test_prompt_injection_increases_prompt_risk():
    normal = generate_trace("normal_collaboration", time_steps=20, random_seed=5)
    injected = generate_trace("prompt_injection", time_steps=20, random_seed=5)
    assert injected["prompt_injection_risk"].mean() > normal["prompt_injection_risk"].mean()


def test_uploaded_trace_normalization_fills_missing_columns():
    raw = pd.DataFrame({"agent": ["Planner"], "evidence_score": [80]})
    out = normalize_uploaded_trace(raw)
    assert "prompt_injection_risk" in out.columns
    assert out.loc[0, "agent"] == "Planner"
    assert out.loc[0, "evidence_score"] == 80
