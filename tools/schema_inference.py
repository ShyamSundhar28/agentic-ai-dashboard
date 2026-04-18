import pandas as pd
import re
from typing import Dict, Any, List

def clean_column_name(name: str) -> str:
    """
    Cleans a column name: lowercase, trim, snakes_case, remove special chars.
    """
    # Lowercase and trim
    name = name.strip().lower()
    # Replace spaces and hyphens with underscores
    name = re.sub(r'[\s\-]+', '_', name)
    # Remove special characters (keep alphanumeric and underscores)
    name = re.sub(r'[^\w_]', '', name)
    # Remove leading/trailing underscores and multiple underscores
    name = re.sub(r'_+', '_', name).strip('_')
    return name

def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infers types for each column in a DataFrame: numeric, categorical, datetime, boolean, text.
    Handles duplicate column names robustly.
    """
    inferred_types = {}
    
    # We iterate by index to handle duplicate column names safely
    for i, col_name in enumerate(df.columns):
        series = df.iloc[:, i]
        
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            inferred_types[f"{col_name}_{i}"] = "datetime"
        # Check if numeric
        elif pd.api.types.is_numeric_dtype(series):
            # If only 0 and 1, could be boolean
            if series.nunique() <= 2 and set(series.dropna().unique()).issubset({0, 1, True, False}):
                inferred_types[f"{col_name}_{i}"] = "boolean"
            else:
                inferred_types[f"{col_name}_{i}"] = "numeric"
        # Check if boolean explicitly
        elif pd.api.types.is_bool_dtype(series):
            inferred_types[f"{col_name}_{i}"] = "boolean"
        # Check if categorical
        elif series.nunique() < 20 or (len(df) > 0 and series.nunique() / len(df) < 0.05):
            inferred_types[f"{col_name}_{i}"] = "categorical"
        else:
            inferred_types[f"{col_name}_{i}"] = "text"
            
    # Map back to names (if names are unique, this is identity, otherwise it suffix-protects)
    # Actually, for the dashboard, let's just return a dict keyed by the actual column headers
    # assuming we handle duplicates upstream. But let's be safe here.
    final_types = {}
    for i, col_name in enumerate(df.columns):
        # We use iloc again to ensure we get a Series even with duplicate names
        series = df.iloc[:, i]
        dtype = "text"
        if pd.api.types.is_datetime64_any_dtype(series): dtype = "datetime"
        elif pd.api.types.is_numeric_dtype(series):
            if series.nunique() <= 2 and set(series.dropna().unique()).issubset({0, 1, True, False}): dtype = "boolean"
            else: dtype = "numeric"
        elif pd.api.types.is_bool_dtype(series): dtype = "boolean"
        elif series.nunique() < 20 or (len(df) > 0 and series.nunique() / len(df) < 0.05): dtype = "categorical"
        
        # If there's a duplicate name, the last one wins in the dict, which is fine
        # but the logic inside doesn't crash anymore.
        final_types[col_name] = dtype
            
    return final_types

def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Returns a detailed data profile. Safer against duplicates.
    """
    schema = infer_column_types(df)
    
    numeric_summary = {}
    categorical_summary = {}
    
    for i, col in enumerate(df.columns):
        series = df.iloc[:, i]
        dtype = schema.get(col)
        
        if dtype == "numeric":
            numeric_summary[col] = series.describe().to_dict()
        elif dtype == "categorical":
            categorical_summary[col] = series.value_counts().head(5).to_dict()

    return {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "inferred_types": schema,
        "missing_values": {col: int(df.iloc[:, i].isnull().sum()) for i, col in enumerate(df.columns)},
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary
    }

