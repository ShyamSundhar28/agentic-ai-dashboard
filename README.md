# Agentic AI Dashboard

Enterprise monorepo scaffold for an Agentic AI Dashboard platform. This initial PR focuses on project structure, shared Python tooling, and CI automation.

## Repository structure

```text
apps/
  api-gateway/
  ui-streamlit/
  worker/
packages/
  common/
  agents/
  tools/
  policy/
  evals/
infra/
  docker/
docs/
  adr/
.github/
  workflows/
```

## Local development quickstart

1. Create and activate a Python 3.11+ virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the project with development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

## Common commands

- Lint and formatting checks:

  ```bash
  make lint
  ```

- Type checking:

  ```bash
  make typecheck
  ```

- Run tests with coverage:

  ```bash
  make test
  ```
