import duckdb
import pandas as pd
from typing import Optional, Dict, Any

from core.config import settings

class DuckDBStore:
    """
    Manages DuckDB persistence and querying.
    """
    def __init__(self, db_path: Optional[str] = None):
        """
        Initializes the DuckDB connection.
        """
        self.db_path = db_path or settings.duckdb_path
        self.conn = duckdb.connect(self.db_path)

    def create_table_from_df(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Creates (or replaces) a table from a pandas DataFrame.
        """
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Returns row and column counts for a given table.
        """
        try:
            row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            col_names = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            return {
                "row_count": row_count,
                "col_count": len(col_names)
            }
        except Exception:
            return {"row_count": 0, "col_count": 0}

    def query(self, sql: str) -> pd.DataFrame:
        """
        Executes a SQL query and returns result as DataFrame.
        """
        return self.conn.execute(sql).df()

    def close(self) -> None:
        """
        Closes the DuckDB connection.
        """
        self.conn.close()
