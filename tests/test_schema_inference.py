import pytest
import pandas as pd
from tools.schema_inference import clean_column_name, infer_column_types, profile_data

def test_clean_column_name():
    assert clean_column_name("User ID") == "user_id"
    assert clean_column_name("  Metric-Value (%) ") == "metric_value"
    assert clean_column_name("Signup Date") == "signup_date"

def test_infer_column_types():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "spend": [10.5, 20.0, 15.0],
        "active": [True, False, True]
    })
    types = infer_column_types(df)
    assert types["id"] == "numeric"
    assert types["name"] == "categorical" # because unique < 20 or ratio small
    assert types["date"] == "datetime"
    assert types["spend"] == "numeric"
    assert types["active"] == "boolean"

def test_profile_data():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "val": [10, 20, 30]
    })
    profile = profile_data(df)
    assert profile["num_rows"] == 3
    assert "inferred_types" in profile
    assert "missing_values" in profile
