import pandas as pd
from typing import List, Dict, Any, Optional

class ChartSelector:
    """
    Selects optimal chart types based on data schema.
    """
    @staticmethod
    def recommend_charts(df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        charts = []
        
        # 1. Histogram for first numeric column
        numeric_cols = [col for col, dtype in schema.items() if dtype == "numeric"]
        if numeric_cols:
            charts.append({
                "type": "histogram",
                "column": numeric_cols[0],
                "title": f"Distribution of {numeric_cols[0]}"
            })
            
        # 2. Bar chart for first categorical column
        categorical_cols = [col for col, dtype in schema.items() if dtype == "categorical"]
        if categorical_cols:
            charts.append({
                "type": "bar",
                "column": categorical_cols[0],
                "title": f"Counts of {categorical_cols[0]}"
            })
            
        # 3. Line chart if datetime + numeric
        datetime_cols = [col for col, dtype in schema.items() if dtype == "datetime"]
        if datetime_cols and numeric_cols:
            charts.append({
                "type": "line",
                "x": datetime_cols[0],
                "y": numeric_cols[0],
                "title": f"{numeric_cols[0]} over Time"
            })
            
        return charts
