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
    # Remove leading numbers/underscores if they make the name invalid for SQL (optional but good)
    return name

def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infers types for each column in a DataFrame: numeric, categorical, datetime, boolean, text.
    """
    inferred_types = {}
    
    for col in df.columns:
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            inferred_types[col] = "datetime"
        # Check if numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            # If only 0 and 1, could be boolean, but let's stick to numeric for now unless bool-like
            if df[col].nunique() <= 2 and set(df[col].dropna().unique()).issubset({0, 1, True, False}):
                inferred_types[col] = "boolean"
            else:
                inferred_types[col] = "numeric"
        # Check if boolean explicitly
        elif pd.api.types.is_bool_dtype(df[col]):
            inferred_types[col] = "boolean"
        # Check if categorical (few unique values relative to size)
        elif df[col].nunique() < 20 or (df[col].nunique() / len(df) < 0.05):
            inferred_types[col] = "categorical"
        # Fallback to text
        else:
            inferred_types[col] = "text"
            
    return inferred_types

def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Returns a detailed data profile.
    """
    schema = infer_column_types(df)
    
    numeric_summary = {}
    for col, dtype in schema.items():
        if dtype == "numeric":
            numeric_summary[col] = df[col].describe().to_dict()
            
    categorical_summary = {}
    for col, dtype in schema.items():
        if dtype == "categorical":
            categorical_summary[col] = df[col].value_counts().head(5).to_dict()

    return {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "inferred_types": schema,
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary
    }

