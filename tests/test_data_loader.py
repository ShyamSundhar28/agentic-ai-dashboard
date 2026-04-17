import pytest
import pandas as pd
import os
from tools.data_loader import load_csv_to_duckdb, get_table_preview
import duckdb

def test_data_loader_workflow():
    # Create dummy csv
    csv_path = "tests/dummy.csv"
    os.makedirs("tests", exist_ok=True)
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df.to_csv(csv_path, index=False)
    
    conn = duckdb.connect(":memory:")
    load_csv_to_duckdb(csv_path, "dummy_table", conn)
    
    preview = get_table_preview(conn, "dummy_table")
    assert len(preview) == 2
    assert "a" in preview.columns
    
    # Cleanup
    conn.close()
    if os.path.exists(csv_path):
        os.remove(csv_path)
