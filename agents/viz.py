from core.models import VisualizationSpec
from tools.chart_selector import ChartSelector
import pandas as pd
from typing import List, Dict

class VizAgent:
    def execute(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[VisualizationSpec]:
        charts = ChartSelector.recommend_charts(df, schema)
        specs = []
        for c in charts:
            specs.append(VisualizationSpec(
                chart_type=c['type'],
                title=c['title'],
                config=c
            ))
        return specs
