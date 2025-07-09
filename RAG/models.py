"""
Modèles de données pour la pipeline RAG multimodal
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import hashlib
import numpy as np
from enum import Enum

class ChunkType(Enum):
    """Types de chunks supportés"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    MIXED = "mixed"

class ProcessingStatus(Enum):
    """Statuts de traitement"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Chunk:
    """Représente un chunk de données multimodal"""
    id: str
    content: str
    chunk_type: ChunkType
    page_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Contenu enrichi
    hypothetical_questions: Optional[List[str]] = None
    embedding: Optional[np.ndarray] = None
    
    # Métadonnées de traitement
    created_at: datetime = field(default_factory=datetime.now)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    
    # Informations de position
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    def __post_init__(self):
        """Post-traitement après initialisation"""
        if isinstance(self.chunk_type, str):
            self.chunk_type = ChunkType(self.chunk_type)
        if isinstance(self.processing_status, str):
            self.processing_status = ProcessingStatus(self.processing_status)
    
    def generate_hash(self) -> str:
        """Génère un hash unique pour le chunk"""
        content_str = f"{self.content}{self.chunk_type.value}{self.page_number}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le chunk en dictionnaire"""
        return {
            "id": self.id,
            "content": self.content,
            "chunk_type": self.chunk_type.value,
            "page_number": self.page_number,
            "metadata": self.metadata,
            "hypothetical_questions": self.hypothetical_questions,
            "embedding": self.embedding.tolist() if self.embedding is not None else None,
            "created_at": self.created_at.isoformat(),
            "processing_status": self.processing_status.value,
            "start_char": self.start_char,
            "end_char": self.end_char
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chunk':
        """Crée un chunk à partir d'un dictionnaire"""
        chunk = cls(
            id=data["id"],
            content=data["content"],
            chunk_type=ChunkType(data["chunk_type"]),
            page_number=data["page_number"],
            metadata=data.get("metadata", {}),
            hypothetical_questions=data.get("hypothetical_questions"),
            start_char=data.get("start_char"),
            end_char=data.get("end_char")
        )
        
        # Reconstituer l'embedding
        if data.get("embedding"):
            chunk.embedding = np.array(data["embedding"])
        
        # Reconstituer les dates et statuts
        if "created_at" in data:
            chunk.created_at = datetime.fromisoformat(data["created_at"])
        if "processing_status" in data:
            chunk.processing_status = ProcessingStatus(data["processing_status"])
        
        return chunk

@dataclass
class ParsedContent:
    """Représente le contenu parsé d'un document"""
    content: str
    content_type: ChunkType
    page_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Informations de position
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "content": self.content,
            "content_type": self.content_type.value,
            "page_number": self.page_number,
            "metadata": self.metadata,
            "bbox": self.bbox
        }

@dataclass
class Document:
    """Représente un document traité"""
    file_path: str
    file_name: str
    file_hash: str
    
    # Contenu parsé
    parsed_content: List[ParsedContent] = field(default_factory=list)
    chunks: List[Chunk] = field(default_factory=list)
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Informations de traitement
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    
    # Statistiques
    total_pages: int = 0
    total_chunks: int = 0
    
    def __post_init__(self):
        """Post-traitement après initialisation"""
        if isinstance(self.processing_status, str):
            self.processing_status = ProcessingStatus(self.processing_status)
    
    def add_parsed_content(self, content: ParsedContent):
        """Ajoute du contenu parsé"""
        self.parsed_content.append(content)
        self.last_updated = datetime.now()
    
    def add_chunk(self, chunk: Chunk):
        """Ajoute un chunk"""
        self.chunks.append(chunk)
        self.total_chunks = len(self.chunks)
        self.last_updated = datetime.now()
    
    def update_status(self, status: ProcessingStatus):
        """Met à jour le statut de traitement"""
        self.processing_status = status
        self.last_updated = datetime.now()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du document"""
        chunk_types = {}
        for chunk in self.chunks:
            chunk_type = chunk.chunk_type.value
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        return {
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "chunk_types": chunk_types,
            "total_questions": sum(len(c.hypothetical_questions or []) for c in self.chunks),
            "processing_status": self.processing_status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_hash": self.file_hash,
            "parsed_content": [pc.to_dict() for pc in self.parsed_content],
            "chunks": [c.to_dict() for c in self.chunks],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "processing_status": self.processing_status.value,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks
        }

@dataclass
class SearchResult:
    """Résultat de recherche dans la base vectorielle"""
    chunk_id: str
    content: str
    chunk_type: ChunkType
    page_number: int
    score: float
    distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-traitement après initialisation"""
        if isinstance(self.chunk_type, str):
            self.chunk_type = ChunkType(self.chunk_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "chunk_type": self.chunk_type.value,
            "page_number": self.page_number,
            "score": self.score,
            "distance": self.distance,
            "metadata": self.metadata
        }

@dataclass
class SearchQuery:
    """Requête de recherche"""
    query_text: str
    query_type: str = "text"  # text, image, hybrid
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Paramètres de recherche
    k: int = 5
    score_threshold: float = 0.0
    
    # Métadonnées
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "query_text": self.query_text,
            "query_type": self.query_type,
            "filters": self.filters,
            "k": self.k,
            "score_threshold": self.score_threshold,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ProcessingResult:
    """Résultat de traitement d'un document"""
    success: bool
    document: Optional[Document] = None
    error_message: Optional[str] = None
    
    # Statistiques de traitement
    processing_time: float = 0.0
    chunks_created: int = 0
    embeddings_generated: int = 0
    
    # Détails des erreurs
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "success": self.success,
            "document": self.document.to_dict() if self.document else None,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "chunks_created": self.chunks_created,
            "embeddings_generated": self.embeddings_generated,
            "warnings": self.warnings
        }

@dataclass
class PipelineState:
    """État de la pipeline"""
    documents_processed: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    
    # Statistiques par type
    text_chunks: int = 0
    table_chunks: int = 0
    image_chunks: int = 0
    
    # Informations temporelles
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def update_stats(self, document: Document):
        """Met à jour les statistiques avec un nouveau document"""
        self.documents_processed += 1
        self.total_chunks += document.total_chunks
        
        for chunk in document.chunks:
            if chunk.chunk_type == ChunkType.TEXT:
                self.text_chunks += 1
            elif chunk.chunk_type == ChunkType.TABLE:
                self.table_chunks += 1
            elif chunk.chunk_type == ChunkType.IMAGE:
                self.image_chunks += 1
            
            if chunk.embedding is not None:
                self.total_embeddings += 1
        
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "documents_processed": self.documents_processed,
            "total_chunks": self.total_chunks,
            "total_embeddings": self.total_embeddings,
            "text_chunks": self.text_chunks,
            "table_chunks": self.table_chunks,
            "image_chunks": self.image_chunks,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }