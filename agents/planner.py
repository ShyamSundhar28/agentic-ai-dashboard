from core.models import Plan, AgentTask, QueryIntent
from typing import Dict, Any, List
import re

class PlannerAgent:
    def __init__(self, schema: Dict[str, str]):
        self.schema = schema
        self.numeric_cols = [c for c, t in schema.items() if t == "numeric"]
        self.categorical_cols = [c for c, t in schema.items() if t == "categorical"]
        self.datetime_cols = [c for c, t in schema.items() if t == "datetime"]

    def parse_intent(self, query: str) -> QueryIntent:
        query_lower = query.lower()
        intent = QueryIntent()
        
        # 1. Detect Intent Type
        if any(w in query_lower for w in ["trend", "over time", "history", "timeline"]):
            intent.intent_type = "trend"
        elif any(w in query_lower for w in ["top", "highest", "best", "most"]):
            intent.intent_type = "top_k"
        elif any(w in query_lower for w in ["compare", "vs", "versus"]):
            intent.intent_type = "comparison"
        elif any(w in query_lower for w in ["why", "cause", "reason", "driver"]):
            intent.intent_type = "rca"
        else:
            intent.intent_type = "summary"

        # 2. Extract Metric (Match with numeric columns)
        for col in self.numeric_cols:
            if col in query_lower or col.replace('_', ' ') in query_lower:
                intent.metric = col
                break
        if not intent.metric and self.numeric_cols:
            intent.metric = self.numeric_cols[0]

        # 3. Extract Dimension (Match with categorical columns)
        for col in self.categorical_cols:
            if col in query_lower or col.replace('_', ' ') in query_lower:
                intent.dimension = col
                break
        if not intent.dimension and self.categorical_cols:
            intent.dimension = self.categorical_cols[0]

        # 4. Extract Date Column
        if self.datetime_cols:
            intent.date_column = self.datetime_cols[0]

        # 5. Extraction Aggregation
        if "average" in query_lower or "mean" in query_lower:
            intent.aggregation = "avg"
        elif "count" in query_lower:
            intent.aggregation = "count"
        else:
            intent.aggregation = "sum"

        return intent

    def generate_plan(self, query: str) -> Plan:
        intent = self.parse_intent(query)
        steps = []
        
        # Basic logical steps based on intent
        steps.append(AgentTask(id="analyst", description=f"Calculate {intent.aggregation} of {intent.metric} by {intent.dimension}"))
        
        if intent.intent_type in ["trend", "top_k", "comparison"]:
            steps.append(AgentTask(id="viz", description=f"Generate {intent.intent_type} chart for {intent.metric}"))
            
        if intent.intent_type == "rca":
            steps.append(AgentTask(id="rca", description=f"Analyze drivers of {intent.metric} fluctuations"))
            
        steps.append(AgentTask(id="recommender", description="Suggest improvements based on findings"))
            
        return Plan(steps=steps, intent=intent)
