import pytest
import pandas as pd
from agents.root_cause import RCAAgent
from core.models import QueryIntent

def test_rca_agent():
    # Setup dummy data showing an obvious drop
    data = {
        "date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "region": ["North", "North", "North", "North"],
        "sales": [100, 110, 50, 40]
    }
    df = pd.DataFrame(data)
    
    agent = RCAAgent()
    intent = QueryIntent(
        metric="sales",
        dimension="region",
        date_column="date"
    )
    
    res = agent.execute(df, intent)
    
    # Assert primary driver is North
    assert res.primary_driver == "North"
    
    # Assert change calculation
    # Prev (100+110=210) to Curr (50+40=90). Abs change = -120
    assert float(res.absolute_change) == -120.0
    assert float(res.percent_change) < 0

def test_rca_insufficient_data():
    df = pd.DataFrame({"dummy": ["a", "b"]})
    agent = RCAAgent()
    intent = QueryIntent()
    res = agent.execute(df, intent)
    
    assert res.primary_driver == "Insufficient Data"
