from core.models import RCAResult, QueryIntent
import pandas as pd
import numpy as np
from typing import Optional

class RCAAgent:
    def execute(self, df: pd.DataFrame, intent: QueryIntent) -> RCAResult:
        metric = intent.metric or (df.select_dtypes(include=[np.number]).columns[0] if not df.select_dtypes(include=[np.number]).empty else None)
        dimension = intent.dimension or (df.select_dtypes(include=['object', 'category']).columns[0] if not df.select_dtypes(include=['object', 'category']).empty else None)
        date_col = intent.date_column
        
        if not metric or not dimension:
            return RCAResult(
                primary_driver="Insufficient Data",
                details="RCA requires at least one numeric metric and one categorical dimension.",
                confidence=0.0
            )

        # Split data into current vs previous (dummy split if no date_col)
        if date_col and date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col)
            mid_point = len(df) // 2
            prev_df = df.iloc[:mid_point]
            curr_df = df.iloc[mid_point:]
        else:
            mid_point = len(df) // 2
            prev_df = df.iloc[:mid_point]
            curr_df = df.iloc[mid_point:]

        # Calculate Totals
        prev_total = prev_df[metric].sum()
        curr_total = curr_df[metric].sum()
        abs_change = curr_total - prev_total
        pct_change = (abs_change / prev_total * 100) if prev_total != 0 else 0

        # Calculate Share of Change by Dimension
        prev_grouped = prev_df.groupby(dimension)[metric].sum()
        curr_grouped = curr_df.groupby(dimension)[metric].sum()
        
        # Merge to find deltas per subgroup
        delta_df = pd.DataFrame({
            'previous': prev_grouped,
            'current': curr_grouped
        }).fillna(0)
        
        delta_df['abs_delta'] = delta_df['current'] - delta_df['previous']
        delta_df['pct_contribution'] = (delta_df['abs_delta'] / abs_change * 100) if abs_change != 0 else 0
        delta_df = delta_df.sort_values('abs_delta', ascending=False)

        primary_driver = delta_df.index[0]
        driver_impact = delta_df.iloc[0]['pct_contribution']

        details = f"The {metric} changed by {abs_change:,.2f} ({pct_change:+.2f}%). "
        details += f"The primary driver was '{primary_driver}', accounting for {driver_impact:.1f}% of the total change."

        return RCAResult(
            primary_driver=str(primary_driver),
            details=details,
            confidence=0.9,
            absolute_change=float(abs_change),
            percent_change=float(pct_change),
            contribution_table=delta_df.reset_index().to_dict('records')
        )
