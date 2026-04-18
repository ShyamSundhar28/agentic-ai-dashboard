from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

class RunContext(BaseModel):
    """
    Context for a single analysis run.
    """
    run_id: str
    table_name: str = "uploaded_data"
    schema_info: Dict[str, str] = {}
    suggested_column_renames: Dict[str, str] = {}
    is_schema_finalized: bool = False
    metadata: Dict[str, Any] = {}

    @classmethod
    def create(cls, table_name: str = "uploaded_data") -> "RunContext":
        return cls(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            table_name=table_name
        )
