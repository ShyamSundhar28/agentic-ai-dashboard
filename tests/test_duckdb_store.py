import pytest
import pandas as pd
from tools.duckdb_store import DuckDBStore

def test_duckdb_store_persistence():
    store = DuckDBStore(":memory:")
    data = {"col1": [1, 2], "col2": ["A", "B"]}
    df = pd.DataFrame(data)
    
    table_name = "test_table"
    store.create_table_from_df(df, table_name)
    
    stats = store.get_table_stats(table_name)
    assert stats["row_count"] == 2
    assert stats["col_count"] == 2
    
    query_df = store.query(f"SELECT * FROM {table_name}")
    assert len(query_df) == 2
    assert list(query_df.columns) == ["col1", "col2"]
    
    store.close()
