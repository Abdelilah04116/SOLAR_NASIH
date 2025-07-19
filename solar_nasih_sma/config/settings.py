import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "your_tavily_api_key_here")
    
    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # Utilisation de Gemini 2.0 Flash
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 1024
    
    # Tavily Configuration
    TAVILY_MAX_RESULTS: int = 5
    
    # RAG Configuration
    RAG_ENDPOINT: str = "http://localhost:8001"  # Endpoint du RAG existant
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    
    # Voice Processing
    VOICE_LANGUAGE: str = "fr-FR"
    
    # Solar Nasih Specific
    SOLAR_EXPERTISE_DOMAINS: list = [
        "installation_photovoltaique",
        "reglementation_solaire",
        "simulation_energetique",
        "certification_rge",
        "aide_financiere",
        "maintenance_panneau",
        "autoconsommation",
        "revente_electricite"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()