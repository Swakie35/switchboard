# Reproducible local walkthrough

This walkthrough does not require production data or cloud deployment. Run the commands at this repository root.

## Prerequisites

Python 3.11+; make a virtual environment and install the project test extra.

## Setup and test

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
```

## Demonstrate the main path

```bash
python -m switchboard --question 'Which items need restocking?'
```

## What to look for

- Observe the console or generated report; **do not substitute copied/synthetic screenshots for actual runtime output**.
- For algorithms, inspect tests around boundary conditions and compare behavior with the README.
- For Java demos, the test runner exercises the HTTP service or core worker behavior; the README includes manual server commands.
- Open `docs/ARCHITECTURE.md` to explain design trade-offs and limits.

## Interpretation

The model is untrusted. The tool registry is the authoritative boundary. An audited tool call does not prove final prose is correct. No API authentication, multi-tenant isolation, or prompt-injection evaluation is provided.

If a command fails, capture the exact error and runtime version rather than claiming the repository is verified.
