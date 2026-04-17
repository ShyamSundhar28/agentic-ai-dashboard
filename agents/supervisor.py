from core.models import SupervisorResponse, Plan
from agents.planner import PlannerAgent
from agents.analyst import AnalystAgent
from agents.viz import VizAgent
from agents.root_cause import RCAAgent
from agents.recommender import RecommenderAgent
import pandas as pd
from typing import Dict

class SupervisorAgent:
    def __init__(self):
        self.analyst = AnalystAgent()
        self.viz = VizAgent()
        self.rca = RCAAgent()
        self.recommender = RecommenderAgent()

    def run_pipeline(self, query: str, df: pd.DataFrame, schema: Dict[str, str], run_id: str) -> SupervisorResponse:
        # 1. Plan
        self.planner = PlannerAgent(schema)
        plan = self.planner.generate_plan(query)
        results = {}
        
        # 2. Execute steps
        for step in plan.steps:
            if step.id == "analyst":
                results["analysis"] = self.analyst.execute(df)
            elif step.id == "viz":
                results["visualizations"] = self.viz.execute(df, schema)
            elif step.id == "rca":
                results["root_cause"] = self.rca.execute(df, plan.intent)
            elif step.id == "recommender":
                results["recommendations"] = self.recommender.execute()
                
        return SupervisorResponse(
            run_id=run_id,
            plan=plan,
            results=results,
            final_output=f"Analysis for '{query}' completed successfully."
        )
