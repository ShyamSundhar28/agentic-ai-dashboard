# Agent Roles and Responsibilities

This document defines the specialized roles within the agentic swarm.

| Agent | Responsibility | Key Output |
| :--- | :--- | :--- |
| **Planner** | Deconstructs user queries into a logical execution plan. | `execution_plan.json` |
| **Analyst** | Performs statistical analysis and data transformations. | `data_summary.json` / Dataframes |
| **Visualization** | Selects optimal chart types and generates Plotly/Altair code. | Interactive Charts |
| **Root Cause** | Identifies the primary drivers behind metric fluctuations. | `rca_report.md` |
| **Recommender** | Suggests business actions based on data insights. | `action_plan.md` |
| **Supervisor** | Manages agent coordination, error handling, and final synthesis. | Final User Response |

## Interaction Pattern
1.  **User** sends a query.
2.  **Supervisor** passes it to the **Planner**.
3.  **Planner** returns steps to the **Supervisor**.
4.  **Supervisor** executes steps by calling **Analyst**, **Viz**, or **Root Cause** in sequence.
5.  **Recommender** synthesizes the final business value.
6.  **Supervisor** reviews and delivers.
