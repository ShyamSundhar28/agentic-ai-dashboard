import pytest
import pandas as pd
from tools.duckdb_store import DuckDBStore
from tools.query_engine import QueryEngine

def test_query_engine():
    store = DuckDBStore(":memory:")
    df = pd.DataFrame({"x": [10, 20], "y": [30, 40]})
    store.create_table_from_df(df, "data")
    
    engine = QueryEngine(store)
    result = engine.execute_query("SELECT SUM(x) as total FROM data")
    assert result.iloc[0]["total"] == 30
    
    stats = engine.get_summary_stats("data")
    assert stats["row_count"] == 2
    
    store.close()
