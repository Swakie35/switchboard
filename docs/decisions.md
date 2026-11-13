# Decisions and threat model

- **No write tools:** prevents the demo from modifying operational state even when a prompt requests it.
- **Typed parameters:** guards against arbitrary argument shapes and SQL strings masquerading as lookups.
- **Max tool steps:** protects from runaway tool usage. It is not a substitute for model token or spend quotas.
- **Explicit traces:** each response contains a tool-by-tool record and source strings; a final answer alone is not proof of correctness.
- **Optional model adapter:** keeps local CI deterministic, avoids network credentials, but leaves an end-to-end model path for real experimentation.
- **Trust boundary:** the LLM is untrusted for choosing tools and final prose; tool registry enforces scope. Retrieved content remains untrusted text.
