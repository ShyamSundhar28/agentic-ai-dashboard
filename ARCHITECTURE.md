# Project Architecture

This document outlines the technical design of the Agentic AI Dashboard.

## 1. Ingestion Layer
- **Modules**: `tools/data_loader.py`
- **Capabilities**: Supports CSV, Parquet, and JSON. Loads data into an in-memory or persistent DuckDB instance.

## 2. Schema Inference
- **Modules**: `tools/schema_inference.py`
- **Mechanism**: Automatically detects column types, identifies primary/foreign keys, and generates Pydantic models for type-safe data manipulation.

## 3. Query Engine
- **Modules**: `tools/query_engine.py`
- **Strategy**: Translates natural language intent into SQL/Python code. Executes within an isolated environment and validates outputs against the inferred schema.

## 4. Agent Pipeline
- **Orchestration**: A **Supervisor-First** model where a master agent delegates tasks to specialized sub-agents.
- **Handoffs**: Structured message passing between agents using Pydantic-defined state objects.

## 5. Root Cause Analysis (RCA) Layer
- **Modules**: `agents/root_cause.py`
- **Logic**: Triggered when anomalous metrics are detected. Performs statistical decomposition and correlational analysis to isolate drivers of change.

## 6. Artifact Tracking
- **Storage**: `artifacts/runs/`
- **Tracking**: Every analysis session generates a `run_id`. All generated code, charts, and data extracts are versioned and linked to the session metadata.

## 7. Deployment Plan
- **Containerization**: `Dockerfile` for multi-stage builds.
- **Platform**: Targeted for **Google Cloud Run** for serverless scaling.
- **CI/CD**: Automated testing via Pytest and deployment via Cloud Build.
