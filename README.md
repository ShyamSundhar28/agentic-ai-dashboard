# Agentic AI Dashboard

A multi-agent dashboard for analyzing and visualizing data using LLM agents.

## Project Structure

- `app/`: Streamlit dashboard application.
- `agents/`: Core agent logic (Planner, Analyst, etc.).
- `core/`: Shared configurations and utilities.
- `tools/`: Data loaders and analytical tools.
- `prompts/`: LLM prompt templates.
- `artifacts/`: Run outputs and persistent data.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   streamlit run app/dashboard.py
   ```
