# Returns Assistant Demo Agent

A minimal Python AI agent instrumented with Datadog LLM Observability (`ao-simulations-returns-demo`) for testing **Datadog Agent Observability Simulations**.

- Entrypoint: `agent.py:handle_message`
- Tool: `lookupOrder` (`@tool`)
- `main`: baseline agent (looks up the first order ID mentioned; mishandles ambiguous receipts and explicit corrections)
- PR #1 (`fix/clarify-all-mentions`): naive patch that clarifies whenever 2+ order ID mentions appear (introduces a regression on repeated mentions like `rd-1006` + `RD-1006`)
- PR #2 (`fix/distinct-orders-and-corrections`): deduplicates order IDs case-insensitively and honors explicit `Correction:` instructions
