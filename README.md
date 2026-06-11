---
title: Multi-Agent Trust Safety Lab
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.37.0
app_file: app.py
pinned: false
license: mit
---

# Multi-Agent Trust Safety Lab

A research-oriented synthetic safety demo for agentic AI and multi-agent collaboration.

This project explores how trust-aware safety checks can help detect, contain, or escalate unreliable outputs in a multi-agent workflow. It is designed as a portfolio artifact for PhD/research applications in AI safety, cooperative AI, multi-agent systems, prompt injection, tool-use risk, and reliable agentic workflows.

## Important limitation

This is **not** a real deployed LLM-agent safety system. It does not call OpenAI, Anthropic, Ollama, Qwen, or any other model. It is a transparent synthetic testbed for demonstrating research thinking, scoring logic, scenario design, and engineering-style safety explanations.

## Core idea

Modern agentic AI systems may include several agents that plan, retrieve context, call tools, verify outputs, and monitor safety. A failure in one step can propagate downstream if unreliable information is accepted too early.

This project simulates those risks using synthetic traces and transparent scoring rules.

## Scenarios

- Normal collaboration
- Indirect prompt injection
- Hallucinated evidence
- Unsafe tool request
- Conflicting values
- Memory poisoning
- Cascading error propagation

## Agents

- UserProxy
- Planner
- Retriever
- ToolExecutor
- CriticVerifier
- SafetyMonitor

## Metrics

The dashboard evaluates:

- Evidence score
- Confidence
- Hallucination risk
- Prompt-injection risk
- Tool-use risk
- Policy risk
- Contradiction score
- Value-conflict score
- Mean risk
- Trust score
- Status and recommended action

## Decisions

The synthetic safety layer may recommend:

- Allow
- Allow with monitoring
- Verify before propagation
- Quarantine output and request independent verification
- Block or require human approval

## Features

- Streamlit dashboard
- Synthetic multi-agent trace generator
- CSV upload
- Trust-aware scoring
- Baseline vs trust-aware guard mode
- Decision explanation in engineer-readable language
- Graphs and trace-level analysis
- Downloadable Markdown report
- Downloadable scored CSV
- pytest unit tests
- Docker support
- Hugging Face Spaces-ready metadata

## Project structure

```text
multiagent-trust-safety-lab/
├── app.py
├── README.md
├── requirements.txt
├── Dockerfile
├── pytest.ini
├── data/
│   └── sample_agent_scenario.csv
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── generator.py
│   ├── reporting.py
│   ├── safety.py
│   └── ui.py
└── tests/
    ├── test_generator.py
    ├── test_reporting.py
    └── test_safety.py
```

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

For macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## CSV upload format

The app accepts a CSV with these columns:

```text
step,agent,event_type,evidence_score,confidence,hallucination_risk,prompt_injection_risk,tool_risk,policy_risk,contradiction_score,value_conflict_score,message_summary
```

Missing numeric fields are filled with defaults so the user can test simpler files.

## Research positioning

This project supports research discussion around:

- agentic AI safety
- multi-agent collaboration
- prompt injection
- tool misuse
- hallucination containment
- trust and reputation
- value-aware negotiation
- cascading-error prevention
- human approval gates
- verification before propagation

## Portfolio note

This is a compact synthetic research artifact. It should be described as a demo/testbed, not as a deployed AI-security solution.
