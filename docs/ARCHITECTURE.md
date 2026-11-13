# Architecture and engineering decisions

> **Scope:** a local reference implementation using invented/synthetic inputs. No production deployment or service-level claims are implied.

## Bounded tool-using assistant

```mermaid
flowchart LR
  A["Question"]
  B["Offline or LLM planner"]
  C["Tool allowlist"]
  D["Pydantic validation"]
  E["Synthetic read-only data"]
  F["Trace and audit DB"]
  A --> B
  B --> C
  C --> D
  D --> E
  E --> F
```

**Actual processing path:** Question --> Planner (offline or optional OpenAI) --> Tool allowlist --> Pydantic argument validation --> Synthetic read-only fixtures --> Evidence trace and SQLite audit.

## Key files

- `switchboard/agent.py`: enforces the step budget and retains observations.
- `switchboard/tools.py`: validates and executes the approved read-only tools.
- `switchboard/openai_planner.py`: optional model-side function-calling adapter.
- `switchboard/api.py`: exposes the local FastAPI service.

## Failure modes / trust boundaries

The model is untrusted. The tool registry is the authoritative boundary. An audited tool call does not prove final prose is correct. No API authentication, multi-tenant isolation, or prompt-injection evaluation is provided.

## What I would build next

Evidence-coverage tests, prompt-injection harness, request budgets, principal-level authorization.

## Reviewer checklist

1. Read the source and confirm the processing path above.
2. Follow `docs/DEMO.md` and run the tests locally.
3. Inspect CI and document any divergence between local and GitHub results.
4. Treat all benchmarks as synthetic demonstrations unless proven otherwise.
