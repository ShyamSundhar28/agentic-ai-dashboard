import pandas as pd
from core.models import AnalysisResult

class AnalystAgent:
    def execute(self, df: pd.DataFrame) -> AnalysisResult:
        summary = f"Dataset contains {len(df)} rows and {len(df.columns)} columns."
        stats = df.describe().to_dict()
        return AnalysisResult(summary=summary, data=stats)
