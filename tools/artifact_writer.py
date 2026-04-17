import json
import os
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class ArtifactWriter:
    """
    Handles saving artifacts (JSON, images, results) to specific run folders,
    and optionally to Google Cloud Storage.
    """
    def __init__(self, base_path: str = "artifacts/runs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.gcs_bucket = os.getenv("GCP_BUCKET_NAME", None)
        
        if self.gcs_bucket:
            try:
                from google.cloud import storage
                self.storage_client = storage.Client()
                self.bucket = self.storage_client.bucket(self.gcs_bucket)
                logger.info(f"Initialized Cloud Storage with bucket: {self.gcs_bucket}")
            except ImportError:
                logger.warning("google-cloud-storage is not installed. Falling back to local storage only.")
                self.gcs_bucket = None
            except Exception as e:
                logger.error(f"Failed to initialize Cloud Storage: {e}")
                self.gcs_bucket = None

    def get_run_dir(self, run_id: str) -> Path:
        run_dir = self.base_path / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _upload_to_gcs(self, local_path: str, run_id: str, filename: str):
        if hasattr(self, 'bucket') and self.bucket:
            try:
                blob_path = f"runs/{run_id}/{filename}"
                blob = self.bucket.blob(blob_path)
                blob.upload_from_filename(local_path)
                logger.info(f"Uploaded {filename} to gs://{self.gcs_bucket}/{blob_path}")
            except Exception as e:
                logger.error(f"Error uploading to GCS: {e}")

    def save_json(self, run_id: str, filename: str, data: Dict[str, Any]) -> str:
        run_dir = self.get_run_dir(run_id)
        file_path = run_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        if self.gcs_bucket:
            self._upload_to_gcs(str(file_path), run_id, filename)
            
        return str(file_path)

    def save_text(self, run_id: str, filename: str, content: str) -> str:
        run_dir = self.get_run_dir(run_id)
        file_path = run_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
            
        if self.gcs_bucket:
            self._upload_to_gcs(str(file_path), run_id, filename)
            
        return str(file_path)

