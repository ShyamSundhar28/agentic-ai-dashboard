from core.models import Recommendation, RCAResult
from typing import List, Dict, Optional
import pandas as pd

class RecommenderAgent:
    def execute(self, df: pd.DataFrame, schema: Dict[str, str], rca_result: Optional[RCAResult] = None) -> List[Recommendation]:
        recommendations = []
        
        # 1. RCA-based recommendations
        if rca_result and rca_result.primary_driver != "Insufficient Data":
            recommendations.append(
                Recommendation(
                    action=f"Deep dive into '{rca_result.primary_driver}'",
                    rationale=f"This segment is the largest driver of the {rca_result.percent_change:+.1f}% change. Try filtering to just this group."
                )
            )
            
        # 2. Schema/Data Quality recommendations
        null_counts = df.isnull().sum()
        total_rows = len(df)
        for col, nulls in null_counts.items():
            if nulls > 0:
                pct_null = (nulls / total_rows) * 100
                if pct_null > 10:
                    recommendations.append(
                        Recommendation(
                            action=f"Investigate missing values in '{col}'",
                            rationale=f"{pct_null:.1f}% of values are missing, which may reduce confidence in analysis involving this column."
                        )
                    )
                    
        # 3. Exploratory recommendations
        cat_cols = [c for c, t in schema.items() if t == 'string']
        num_cols = [c for c, t in schema.items() if t in ['integer', 'float']]
        
        if len(num_cols) >= 2:
            recommendations.append(
                Recommendation(
                    action=f"Compare {num_cols[0]} vs {num_cols[1]}",
                    rationale="A scatter plot or correlation analysis could reveal interesting relationships between these metrics."
                )
            )
            
        if len(cat_cols) > 0 and len(num_cols) > 0:
            recommendations.append(
                Recommendation(
                    action=f"Analyze '{num_cols[0]}' across '{cat_cols[0]}'",
                    rationale="Grouping by this dimension can highlight the highest and lowest performing segments."
                )
            )

        # Fallback if we don't have enough specific ones
        if len(recommendations) < 2:
             recommendations.append(
                 Recommendation(
                     action="Explore datetime trends",
                     rationale="If you have a date column, time-series analysis can reveal seasonal patterns."
                 )
             )
             
        # Return at most Top 3 recommendations
        return recommendations[:3]

