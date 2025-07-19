"""
Modèles de réponse Pydantic pour l'API RAG multimodal.
Définit les schémas de validation pour les réponses sortantes.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    """Statuts de réponse possibles."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

class SearchResult(BaseModel):
    """Modèle pour un résultat de recherche individuel."""
    
    content: str = Field(..., description="Contenu du document")
    source: str = Field(..., description="Source du document")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de pertinence")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées du document")
    doc_type: str = Field(default="text", description="Type de document")
    chunk_id: Optional[str] = Field(default=None, description="Identifiant du chunk")

class SearchResponse(BaseModel):
    """Modèle de réponse pour la recherche de documents."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    query: str = Field(..., description="Requête originale")
    results: List[SearchResult] = Field(..., description="Résultats de recherche")
    total_results: int = Field(..., description="Nombre total de résultats")
    search_time: float = Field(..., description="Temps de recherche en secondes")
    search_type: str = Field(..., description="Type de recherche utilisé")
    message: Optional[str] = Field(default=None, description="Message informatif")

class GenerateResponse(BaseModel):
    """Modèle de réponse pour la génération de réponse."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    query: str = Field(..., description="Question originale")
    response: str = Field(..., description="Réponse générée")
    sources: List[SearchResult] = Field(..., description="Sources utilisées")
    generation_time: float = Field(..., description="Temps de génération en secondes")
    model_used: str = Field(..., description="Modèle LLM utilisé")
    tokens_used: Optional[int] = Field(default=None, description="Nombre de tokens utilisés")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Score de confiance")

class UploadResponse(BaseModel):
    """Modèle de réponse pour l'upload de documents."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    file_path: str = Field(..., description="Chemin du fichier uploadé")
    document_id: str = Field(..., description="Identifiant du document")
    chunks_created: int = Field(..., description="Nombre de chunks créés")
    processing_time: float = Field(..., description="Temps de traitement en secondes")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées extraites")
    message: Optional[str] = Field(default=None, description="Message informatif")

class IndexResponse(BaseModel):
    """Modèle de réponse pour l'indexation de documents."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    directory: str = Field(..., description="Dossier traité")
    documents_processed: int = Field(..., description="Nombre de documents traités")
    chunks_created: int = Field(..., description="Nombre total de chunks créés")
    processing_time: float = Field(..., description="Temps de traitement en secondes")
    errors: List[str] = Field(default=[], description="Erreurs rencontrées")
    document_types: List[str] = Field(..., description="Types de documents traités")

class HealthCheckResponse(BaseModel):
    """Modèle de réponse pour le health check."""
    
    status: ResponseStatus = Field(..., description="Statut général du système")
    timestamp: datetime = Field(..., description="Timestamp de la vérification")
    version: str = Field(..., description="Version du système")
    uptime: float = Field(..., description="Temps de fonctionnement en secondes")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Statut des composants")
    dependencies: Dict[str, bool] = Field(..., description="Statut des dépendances")
    vector_store_status: Optional[Dict[str, Any]] = Field(default=None, description="Statut de la base vectorielle")

class BatchSearchResponse(BaseModel):
    """Modèle de réponse pour la recherche par lot."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    total_queries: int = Field(..., description="Nombre total de requêtes")
    successful_queries: int = Field(..., description="Nombre de requêtes réussies")
    failed_queries: int = Field(..., description="Nombre de requêtes échouées")
    results: List[SearchResponse] = Field(..., description="Résultats par requête")
    total_processing_time: float = Field(..., description="Temps total de traitement")
    average_response_time: float = Field(..., description="Temps de réponse moyen")

class ErrorResponse(BaseModel):
    """Modèle de réponse pour les erreurs."""
    
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Statut de la réponse")
    error_code: str = Field(..., description="Code d'erreur")
    error_message: str = Field(..., description="Message d'erreur")
    timestamp: datetime = Field(..., description="Timestamp de l'erreur")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Détails de l'erreur")
    request_id: Optional[str] = Field(default=None, description="Identifiant de la requête")

class MultimodalSearchResponse(BaseModel):
    """Modèle de réponse pour la recherche multimodale."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    text_results: Optional[List[SearchResult]] = Field(default=None, description="Résultats textuels")
    image_results: Optional[List[SearchResult]] = Field(default=None, description="Résultats d'images")
    audio_results: Optional[List[SearchResult]] = Field(default=None, description="Résultats audio")
    video_results: Optional[List[SearchResult]] = Field(default=None, description="Résultats vidéo")
    fused_results: List[SearchResult] = Field(..., description="Résultats fusionnés")
    fusion_strategy: str = Field(..., description="Stratégie de fusion utilisée")
    processing_time: float = Field(..., description="Temps de traitement")

class StatisticsResponse(BaseModel):
    """Modèle de réponse pour les statistiques du système."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    total_documents: int = Field(..., description="Nombre total de documents")
    total_chunks: int = Field(..., description="Nombre total de chunks")
    document_types: Dict[str, int] = Field(..., description="Répartition par type de document")
    vector_store_size: Optional[int] = Field(default=None, description="Taille de la base vectorielle")
    last_indexing: Optional[datetime] = Field(default=None, description="Dernière indexation")
    system_metrics: Dict[str, Any] = Field(..., description="Métriques système")

class FilterResponse(BaseModel):
    """Modèle de réponse pour les filtres de recherche."""
    
    status: ResponseStatus = Field(..., description="Statut de la réponse")
    available_filters: Dict[str, List[str]] = Field(..., description="Filtres disponibles")
    applied_filters: Dict[str, Any] = Field(..., description="Filtres appliqués")
    filtered_results_count: int = Field(..., description="Nombre de résultats après filtrage")

class APIInfoResponse(BaseModel):
    """Modèle de réponse pour les informations de l'API."""
    
    name: str = Field(..., description="Nom de l'API")
    version: str = Field(..., description="Version de l'API")
    description: str = Field(..., description="Description de l'API")
    endpoints: List[Dict[str, Any]] = Field(..., description="Endpoints disponibles")
    models_supported: List[str] = Field(..., description="Modèles supportés")
    document_types_supported: List[str] = Field(..., description="Types de documents supportés")
    max_file_size: Optional[int] = Field(default=None, description="Taille maximale de fichier")
    rate_limit: Optional[Dict[str, Any]] = Field(default=None, description="Limites de taux")
