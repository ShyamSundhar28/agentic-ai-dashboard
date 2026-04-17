import duckdb
import pandas as pd
from typing import Optional

class DuckDBStore:
    """
    Manages DuckDB persistence and querying.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)

    def create_table_from_df(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Creates (or replaces) a table from a pandas DataFrame.
        """
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")

    def get_table_stats(self, table_name: str) -> dict:
        """
        Returns row and column counts for a given table.
        """
        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        col_names = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
        return {
            "row_count": row_count,
            "col_count": len(col_names)
        }

    def query(self, sql: str) -> pd.DataFrame:
        """
        Executes a SQL query and returns result as DataFrame.
        """
        return self.conn.execute(sql).df()

    def close(self):
        self.conn.close()
