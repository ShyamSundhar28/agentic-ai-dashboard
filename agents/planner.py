from core.models import Plan, AgentTask
from typing import Dict, Any

class PlannerAgent:
    def generate_plan(self, query: str) -> Plan:
        # Simple rule-based planning
        steps = []
        if "analyze" in query.lower() or "summary" in query.lower():
            steps.append(AgentTask(id="analyst", description="Summarize the dataset statistics"))
        
        if "chart" in query.lower() or "viz" in query.lower() or "plot" in query.lower():
            steps.append(AgentTask(id="viz", description="Generate relevant visualizations"))
            
        if "why" in query.lower() or "cause" in query.lower() or "root" in query.lower():
            steps.append(AgentTask(id="rca", description="Perform root cause analysis on anomalies"))
            
        if "recommend" in query.lower() or "suggest" in query.lower():
            steps.append(AgentTask(id="recommender", description="Generate business recommendations"))
            
        return Plan(steps=steps)
