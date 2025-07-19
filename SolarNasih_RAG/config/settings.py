from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    gemini_api_key: str | None = None
    
    # Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    redis_url: str = "redis://localhost:6379"
    
    # Storage
    data_path: str = "./data"
    models_path: str = "./models"
    cache_path: str = "./data/cache"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Model Configuration
    default_text_model: str = "all-MiniLM-L6-v2"
    default_image_model: str = "ViT-B/32"
    default_llm_model: str = "gpt-3.5-turbo"
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Vector Store
    vector_collection_name: str = "multimodal_documents"
    vector_size: int = 384
    
    # Retrieval
    top_k: int = 5
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()