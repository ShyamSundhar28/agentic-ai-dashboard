import pytest
import pandas as pd
from tools.schema_inference import clean_column_name, infer_column_types

def test_clean_column_name():
    assert clean_column_name("  User ID  ") == "user_id"
    assert clean_column_name("Total Sales ($)") == "total_sales_"
    assert clean_column_name("First-Name") == "first_name"
    assert clean_column_name("Column!@#123") == "column123"

def test_infer_column_types():
    data = {
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "is_active": [True, False, True],
        "created_at": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
        "score": [95.5, 80.0, 88.2],
        "category": ["A", "A", "B"]
    }
    df = pd.DataFrame(data)
    types = infer_column_types(df)
    
    assert types["id"] == "numeric"
    assert types["name"] == "categorical" # small df, 3 unique < 20 threshold
    assert types["is_active"] == "boolean"
    assert types["created_at"] == "datetime"
    assert types["score"] == "numeric"
    assert types["category"] == "categorical"
