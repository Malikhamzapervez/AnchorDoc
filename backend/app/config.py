# config.py — Settings for Document Butler.
# Reads from .env automatically via pydantic-settings.

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b"

    # Local embeddings: Hugging Face model (free, 384-dim)
    embedding_provider: str = "huggingface"

    # Qdrant
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_path: str = "qdrant_storage"
    qdrant_collection: str = "document_butler"

    # File storage
    upload_dir: str = "uploads_tmp"       # Temp folder during processing (files deleted after)
    uploads_dir: str = "uploads"          # Permanent storage for original uploaded files
    markdown_dir: str = "markdown_files"  # Generated markdown file per uploaded document
    max_upload_size_mb: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def use_cloud_qdrant(self) -> bool:
        placeholders = {
            "qdrant url here",
            "your qdrant url here",
            "qdrant api key here",
            "your qdrant api key here",
        }
        return bool(
            self.qdrant_url
            and self.qdrant_api_key
            and self.qdrant_url.strip().lower() not in placeholders
            and self.qdrant_api_key.strip().lower() not in placeholders
        )


settings = Settings()
