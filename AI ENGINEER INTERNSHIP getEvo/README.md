# EvoAI Agent

A LangGraph-based agent for a mock Shopify store that handles product assistance and order management with strict cancellation policies.

## Project Structure

```
/src                  # agent graph + tools
  graph.py
  tools.py
/data
  products.json
  orders.json
/prompts
  system.md
/tests
  run_tests.py
README.md
```

## Setup

1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install langgraph
   ```

## Run Tests

Execute the test suite to verify the agent's functionality:

```bash
python tests/run_tests.py
```

This will run the 4 required test cases and output the JSON traces and final replies for each.

## Usage

The agent can be used programmatically:

```python
from src.graph import run_agent

trace = run_agent("Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?")
print(trace['final_message'])
```

## Features

- **Product Assist**: Search for products under budget, recommend sizes, provide ETAs
- **Order Help**: Secure order lookup and cancellation with 60-minute policy enforcement
- **Guardrails**: Refuses invalid requests and suggests legitimate alternatives
- **Traces**: Every response includes a structured JSON trace for debugging and evaluation

## Dependencies

- langgraph
- Python standard library (json, datetime, re, os, typing)