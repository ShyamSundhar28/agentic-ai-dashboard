from core.models import Recommendation
from typing import List

class RecommenderAgent:
    def execute(self) -> List[Recommendation]:
        return [
            Recommendation(
                action="Regularize data ingestion",
                rationale="Ensuring consistent data schema across uploads will minimize inference errors."
            ),
            Recommendation(
                action="Explore datetime trends",
                rationale="Time-series analysis can reveal seasonal patterns in your metrics."
            )
        ]
