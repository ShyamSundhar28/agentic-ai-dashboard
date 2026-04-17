import json
import os
from pathlib import Path
from typing import Any, Dict

class ArtifactWriter:
    """
    Handles saving artifacts (JSON, images, results) to specific run folders.
    """
    def __init__(self, base_path: str = "artifacts/runs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_run_dir(self, run_id: str) -> Path:
        run_dir = self.base_path / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def save_json(self, run_id: str, filename: str, data: Dict[str, Any]) -> str:
        run_dir = self.get_run_dir(run_id)
        file_path = run_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return str(file_path)

    def save_text(self, run_id: str, filename: str, content: str) -> str:
        run_dir = self.get_run_dir(run_id)
        file_path = run_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return str(file_path)
