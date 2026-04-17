from core.models import RCAResult
import pandas as pd

class RCAAgent:
    def execute(self, df: pd.DataFrame) -> RCAResult:
        # Dummy logic: find column with most nulls
        null_counts = df.isnull().sum()
        max_null_col = null_counts.idxmax()
        if null_counts[max_null_col] > 0:
            return RCAResult(
                primary_driver=max_null_col,
                details=f"Column '{max_null_col}' has {null_counts[max_null_col]} missing values, potentially impacting downstream analysis.",
                confidence=0.85
            )
        return RCAResult(
            primary_driver="None",
            details="No obvious data quality issues or anomalies detected in the primary dimensions.",
            confidence=0.9
        )
