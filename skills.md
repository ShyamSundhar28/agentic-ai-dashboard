# Skills-Based Workflows

Standardized procedures for developing and maintaining the Agentic Dashboard.

## 1. Create Module
- **Trigger**: Adding a new tool or agent.
- **Workflow**:
    1. Create `.py` file in `agents/` or `tools/`.
    2. Define a Pydantic `Configuration` class.
    3. Implement the core logic.
    4. Register the module in `core/config.py`.

## 2. Add Tests
- **Trigger**: New feature or bug fix.
- **Workflow**:
    1. Create a corresponding file in `tests/`.
    2. Use `pytest` for unit testing logic.
    3. Use mock data for LLM interaction tests.

## 3. Add Artifact Output
- **Trigger**: Agent generating a new piece of data.
- **Workflow**:
    1. Utilize `tools/artifact_writer.py`.
    2. Save as JSON/CSV/PDF in `artifacts/runs/{run_id}/`.
    3. Update the `run_context.py` manifest.

## 4. Refactor Large Function
- **Trigger**: Functions exceeding 50 lines.
- **Workflow**:
    1. Decompose into smaller utility functions in `core/utils.py`.
    2. Ensure unit tests pass for the refactored logic.

## 5. Add Cloud Run Config
- **Trigger**: Preparing for production.
- **Workflow**:
    1. Update `Dockerfile`.
    2. Configure `cloud-build.yaml`.
    3. Set up environment variables in GCP Console.
