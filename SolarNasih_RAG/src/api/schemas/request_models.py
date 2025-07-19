"""
Modèles de requête Pydantic pour l'API RAG multimodal.
Définit les schémas de validation pour les requêtes entrantes.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class SearchType(str, Enum):
    """Types de recherche disponibles."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    MULTIMODAL = "multimodal"

class DocumentType(str, Enum):
    """Types de documents supportés."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"
    DOCX = "docx"

class SearchRequest(BaseModel):
    """Modèle de requête pour la recherche de documents."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Requête de recherche")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type de recherche")
    top_k: int = Field(default=5, ge=1, le=50, description="Nombre de résultats à retourner")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Seuil de pertinence")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filtres de recherche")
    include_metadata: bool = Field(default=True, description="Inclure les métadonnées dans la réponse")
    
    @validator('query')
    def validate_query(cls, v):
        """Valide que la requête n'est pas vide après nettoyage."""
        if not v.strip():
            raise ValueError("La requête ne peut pas être vide")
        return v.strip()

class UploadRequest(BaseModel):
    """Modèle de requête pour l'upload de documents."""
    
    file_path: str = Field(..., description="Chemin vers le fichier à uploader")
    document_type: Optional[DocumentType] = Field(default=None, description="Type de document")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées du document")
    chunk_size: int = Field(default=1000, ge=100, le=10000, description="Taille des chunks")
    chunk_overlap: int = Field(default=200, ge=0, le=5000, description="Chevauchement des chunks")
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Valide que le fichier existe."""
        from pathlib import Path
        if not Path(v).exists():
            raise ValueError(f"Le fichier {v} n'existe pas")
        return v

class GenerateRequest(BaseModel):
    """Modèle de requête pour la génération de réponse."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Question à traiter")
    context_docs: Optional[List[Dict[str, Any]]] = Field(default=None, description="Documents de contexte")
    max_tokens: int = Field(default=1000, ge=50, le=4000, description="Nombre maximum de tokens")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Température de génération")
    template_type: str = Field(default="general_rag", description="Type de template à utiliser")
    
    @validator('query')
    def validate_query(cls, v):
        """Valide que la requête n'est pas vide après nettoyage."""
        if not v.strip():
            raise ValueError("La requête ne peut pas être vide")
        return v.strip()

class MultimodalSearchRequest(BaseModel):
    """Modèle de requête pour la recherche multimodale."""
    
    text_query: Optional[str] = Field(default=None, description="Requête textuelle")
    image_path: Optional[str] = Field(default=None, description="Chemin vers l'image")
    audio_path: Optional[str] = Field(default=None, description="Chemin vers l'audio")
    video_path: Optional[str] = Field(default=None, description="Chemin vers la vidéo")
    top_k: int = Field(default=5, ge=1, le=50, description="Nombre de résultats")
    fusion_strategy: str = Field(default="weighted", description="Stratégie de fusion des résultats")
    
    @validator('text_query', 'image_path', 'audio_path', 'video_path')
    def validate_at_least_one_input(cls, v, values):
        """Valide qu'au moins une entrée est fournie."""
        if not any([values.get('text_query'), values.get('image_path'), 
                   values.get('audio_path'), values.get('video_path')]):
            raise ValueError("Au moins une entrée (texte, image, audio ou vidéo) doit être fournie")
        return v

class IndexRequest(BaseModel):
    """Modèle de requête pour l'indexation de documents."""
    
    directory: str = Field(..., description="Dossier contenant les documents à indexer")
    document_types: Optional[List[DocumentType]] = Field(default=None, description="Types de documents à traiter")
    recursive: bool = Field(default=True, description="Parcourir les sous-dossiers")
    dry_run: bool = Field(default=False, description="Simulation sans indexation réelle")
    force_reindex: bool = Field(default=False, description="Forcer la réindexation")
    
    @validator('directory')
    def validate_directory(cls, v):
        """Valide que le dossier existe."""
        from pathlib import Path
        if not Path(v).exists():
            raise ValueError(f"Le dossier {v} n'existe pas")
        return v

class HealthCheckRequest(BaseModel):
    """Modèle de requête pour le health check."""
    
    detailed: bool = Field(default=False, description="Inclure des détails dans la réponse")
    check_dependencies: bool = Field(default=True, description="Vérifier les dépendances")
    check_vector_store: bool = Field(default=True, description="Vérifier la base vectorielle")

class BatchSearchRequest(BaseModel):
    """Modèle de requête pour la recherche par lot."""
    
    queries: List[str] = Field(..., min_items=1, max_items=100, description="Liste de requêtes")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type de recherche")
    top_k: int = Field(default=5, ge=1, le=50, description="Nombre de résultats par requête")
    
    @validator('queries')
    def validate_queries(cls, v):
        """Valide que toutes les requêtes sont valides."""
        for i, query in enumerate(v):
            if not query.strip():
                raise ValueError(f"La requête {i+1} ne peut pas être vide")
        return [q.strip() for q in v]

class FilterRequest(BaseModel):
    """Modèle de requête pour les filtres de recherche."""
    
    document_types: Optional[List[DocumentType]] = Field(default=None, description="Types de documents")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Plage de dates")
    source_filter: Optional[List[str]] = Field(default=None, description="Filtres par source")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="Filtres par métadonnées")
    
    @validator('date_range')
    def validate_date_range(cls, v):
        """Valide le format de la plage de dates."""
        if v is not None:
            required_keys = ['start', 'end']
            if not all(key in v for key in required_keys):
                raise ValueError("La plage de dates doit contenir 'start' et 'end'")
        return v
