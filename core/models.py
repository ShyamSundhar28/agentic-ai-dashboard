from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentTask(BaseModel):
    id: str
    description: str
    status: str = "pending"
    result: Optional[Any] = None

class Plan(BaseModel):
    steps: List[AgentTask]

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

class Recommendation(BaseModel):
    action: str
    rationale: str

class SupervisorResponse(BaseModel):
    run_id: str
    plan: Plan
    results: Dict[str, Any]
    final_output: str
