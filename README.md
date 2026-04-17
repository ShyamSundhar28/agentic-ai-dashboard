# Agentic AI Dashboard

An autonomous, multi-agent business intelligence platform that transforms raw data into actionable insights through automated analysis, visualization, and root-cause investigation.

## 🚀 Overview

The Agentic AI Dashboard uses a swarm of specialized AI agents to handle the entire data lifecycle—from initial ingestion and schema inference to complex multi-step reasoning and interactive visualization.

## 🛠️ Tech Stack

- **Frontend**: React + Vite (Custom Dashboard), Streamlit (Rapid Prototyping UI)
- **Data Engine**: Python 3.12, DuckDB (OLAP), Pandas
- **Visualization**: Plotly, Altair
- **Intelligence**: Pydantic (Strong Typing), LangChain/OpenAI/Anthropic
- **Testing & DevOps**: Pytest, Docker, GitHub Actions

## 📖 Architecture Summary

The system follows a modular, agent-driven architecture:
1.  **Ingestion & Tools**: Specialized modules for data loading and schema inference.
2.  **Agent Swarm**: A coordinated group of agents (Planner, Analyst, etc.) managed by a Supervisor.
3.  **Run Context**: A persistent state tracker that manages artifacts and logs for every analysis session.

## 🏃 How to Run Locally

### 1. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
streamlit run app/dashboard.py
```

### 3. (Optional) Run React Frontend
```bash
npm install
npm run dev
```
