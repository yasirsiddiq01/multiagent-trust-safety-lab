from src.generator import generate_trace
from src.reporting import generate_markdown_report
from src.safety import decision_paragraph, score_trace, summarize_decision


def test_report_contains_main_sections():
    df = generate_trace("hallucinated_evidence", time_steps=10, random_seed=8)
    scored = score_trace(df)
    summary = summarize_decision(scored)
    explanation = decision_paragraph(summary, "Hallucinated evidence")
    report = generate_markdown_report("Hallucinated evidence", "Trust-aware safety guard", scored, summary, explanation)
    assert "# Multi-Agent Trust Safety Lab Report" in report
    assert "Workflow decision" in report
    assert "Important limitation" in report
