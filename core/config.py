import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings and environment configuration.
    """
    app_env: str = os.getenv("APP_ENV", "local")
    duckdb_path: str = os.getenv("DUCKDB_PATH", ":memory:")
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "artifacts/runs")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    google_cloud_region: str = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
