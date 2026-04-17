import pandas as pd
from tools.duckdb_store import DuckDBStore
from typing import Optional, List, Dict, Any

class QueryEngine:
    """
    Orchestrates data retrieval and transformation using DuckDB.
    """
    def __init__(self, store: DuckDBStore):
        self.store = store

    def execute_query(self, sql: str) -> pd.DataFrame:
        """
        Executes a raw SQL query.
        """
        try:
            return self.store.query(sql)
        except Exception as e:
            # In production, we'd log this and raise a custom error
            raise RuntimeError(f"SQL execution failed: {str(e)}")

    def get_summary_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Retrieves basic summary statistics for a table.
        """
        return self.store.get_table_stats(table_name)
