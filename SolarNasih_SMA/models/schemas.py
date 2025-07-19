from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentType(str, Enum):
    TASK_DIVIDER = "task_divider"
    DOCUMENT_INDEXER = "document_indexer"
    VOICE_PROCESSOR = "voice_processor"
    MULTILINGUAL_DETECTOR = "multilingual_detector"
    TECHNICAL_ADVISOR = "technical_advisor"
    ENERGY_SIMULATOR = "energy_simulator"
    REGULATORY_ASSISTANT = "regulatory_assistant"
    EDUCATIONAL_AGENT = "educational_agent"
    COMMERCIAL_ASSISTANT = "commercial_assistant"
    CERTIFICATION_ASSISTANT = "certification_assistant"
    DOCUMENT_GENERATOR = "document_generator"
    RAG_SYSTEM = "rag_system"

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message de l'utilisateur")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexte de la conversation")
    language: Optional[str] = Field(default="fr", description="Langue détectée")

class ChatResponse(BaseModel):
    message: str = Field(..., description="Réponse du système")
    agent_used: AgentType = Field(..., description="Agent utilisé pour la réponse")
    confidence: float = Field(..., description="Niveau de confiance")
    sources: List[str] = Field(default=[], description="Sources utilisées")

class EnergySimulationRequest(BaseModel):
    surface_toit: float = Field(..., description="Surface du toit en m²")
    orientation: str = Field(..., description="Orientation du toit")
    inclinaison: float = Field(..., description="Inclinaison en degrés")
    localisation: str = Field(..., description="Localisation géographique")
    consommation_annuelle: float = Field(..., description="Consommation annuelle en kWh")
    budget_max: Optional[float] = Field(None, description="Budget maximum")

class DocumentGenerationRequest(BaseModel):
    document_type: str = Field(..., description="Type de document à générer")
    client_info: Dict[str, Any] = Field(..., description="Informations client")
    project_details: Dict[str, Any] = Field(..., description="Détails du projet")
    template_id: Optional[str] = Field(None, description="ID du template")

class AgentState(BaseModel):
    """État partagé entre les agents"""
    current_message: str = ""
    detected_language: str = "fr"
    user_intent: str = ""
    agent_route: AgentType = AgentType.TASK_DIVIDER
    context: Dict[str, Any] = {}
    response: str = ""
    confidence: float = 0.0
    sources: List[str] = []
    processing_history: List[Dict[str, Any]] = []

class VoiceProcessingResult(BaseModel):
    transcribed_text: str
    detected_language: str
    audio_response_url: Optional[str] = None
    confidence: float

class SimulationResult(BaseModel):
    puissance_recommandee: float
    production_annuelle: float
    economies_annuelles: float
    temps_amortissement: float
    co2_evite: float
    cout_installation: float
    
class DocumentGenerationResult(BaseModel):
    document_url: str
    document_type: str
    generated_at: str
    document_id: str

class Language(str, Enum):
    FRENCH = "fr"
    ENGLISH = "en"
    SPANISH = "es"
    # Ajoutez d'autres langues si besoin