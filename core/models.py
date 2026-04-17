from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryIntent(BaseModel):
    metric: Optional[str] = None
    dimension: Optional[str] = None
    date_column: Optional[str] = None
    aggregation: Optional[str] = "sum"
    filters: List[Dict[str, Any]] = []
    intent_type: str = "general" # trend, top_k, comparison, summary, rca

class AgentTask(BaseModel):
    id: str
    description: str
    status: str = "pending"
    result: Optional[Any] = None

class Plan(BaseModel):
    steps: List[AgentTask]
    intent: Optional[QueryIntent] = None

class AnalysisResult(BaseModel):
    summary: str
    data: Optional[Dict[str, Any]] = None

class VisualizationSpec(BaseModel):
    chart_type: str
    title: str
    config: Dict[str, Any]

class RCAResult(BaseModel):
    primary_driver: str
    details: str
    confidence: float
    absolute_change: float = 0.0
    percent_change: float = 0.0
    contribution_table: Optional[List[Dict[str, Any]]] = None


class Recommendation(BaseModel):
    action: str
    rationale: str

class SupervisorResponse(BaseModel):
    run_id: str
    plan: Plan
    results: Dict[str, Any]
    final_output: str
