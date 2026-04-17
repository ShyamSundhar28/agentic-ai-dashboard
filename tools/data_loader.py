import duckdb
import pandas as pd
from typing import Optional

def load_csv_to_duckdb(file_path: str, table_name: str, conn: Optional[duckdb.DuckDBPyConnection] = None) -> duckdb.DuckDBPyConnection:
    """
    Loads a CSV file into a DuckDB table.
    """
    if conn is None:
        conn = duckdb.connect(':memory:')
    
    # Use DuckDB's native CSV reader for performance
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
    return conn

def get_table_preview(conn: duckdb.DuckDBPyConnection, table_name: str, limit: int = 20) -> pd.DataFrame:
    """
    Returns a pandas DataFrame preview of a table.
    """
    return conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}").df()
