"""
Module de stockage vectoriel pour la base de données de vecteurs (ChromaDB uniquement, mode client HTTP)
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

# Imports pour ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from models import Chunk, SearchResult, SearchQuery, ChunkType
from config import VectorStoreConfig

logger = logging.getLogger(__name__)

class BaseVectorStore:
    """Interface de base pour la base de données vectorielle"""
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.store_path = Path(config.store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

    def add_chunks(self, chunks: List[Chunk]) -> bool:
        raise NotImplementedError

    def search(self, query_embedding: np.ndarray, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        raise NotImplementedError

    def delete_chunk(self, chunk_id: str) -> bool:
        raise NotImplementedError

    def get_chunk_count(self) -> int:
        raise NotImplementedError

    def clear(self) -> bool:
        raise NotImplementedError

class ChromaVectorStore(BaseVectorStore):
    """Implémentation avec ChromaDB (client HTTP)"""
    def __init__(self, config: VectorStoreConfig):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB n'est pas installé. Installer avec: pip install chromadb")
        super().__init__(config)
        self.collection_name = config.collection_name
        self._initialize_client()

    def _initialize_client(self):
        """Initialise le client ChromaDB en mode HTTP (serveur)"""
        try:
            # Connexion à un serveur ChromaDB (par défaut localhost:8000)
            self.client = chromadb.HttpClient(host=self.config.chromadb_host or "localhost", port=self.config.chromadb_port or 8000)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Collection pour RAG multimodal",
                    "created_by": "multimodal_rag_pipeline"
                }
            )
            logger.info(f"ChromaDB (serveur) initialisé: {self.collection.count()} documents existants")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de ChromaDB: {e}")
            raise

    def add_chunks(self, chunks: List[Chunk]) -> bool:
        if not chunks:
            return True
        try:
            dim_to_collection = {}
            # Prépare une collection par dimension
            for chunk in chunks:
                if chunk.embedding is not None and len(chunk.embedding) > 0:
                    dim = len(chunk.embedding)
                    if dim not in dim_to_collection:
                        # Crée une collection spécifique pour chaque dimension
                        collection_name = f"{self.collection_name}_{dim}"
                        collection = self.client.get_or_create_collection(
                            name=collection_name,
                            metadata={
                                "description": f"Collection pour RAG multimodal (dim={dim})",
                                "created_by": "multimodal_rag_pipeline"
                            }
                        )
                        dim_to_collection[dim] = collection
            # Ajoute les chunks dans la bonne collection
            for dim, collection in dim_to_collection.items():
                group = [c for c in chunks if c.embedding is not None and len(c.embedding) == dim]
                documents = [c.content for c in group]
                embeddings = [c.embedding.tolist() for c in group]
                metadata = []
                ids = []
                for chunk in group:
                    chunk_metadata = {
                        "chunk_type": chunk.chunk_type.value,
                        "page_number": chunk.page_number,
                        "created_at": chunk.created_at.isoformat(),
                        "processing_status": chunk.processing_status.value
                    }
                    if chunk.hypothetical_questions:
                        chunk_metadata["questions"] = " | ".join(chunk.hypothetical_questions)
                    for key, value in chunk.metadata.items():
                        if key == "image_path":
                            chunk_metadata["image_path"] = value  # pas de préfixe
                        elif isinstance(value, (str, int, float, bool)):
                            chunk_metadata[f"meta_{key}"] = value
                        else:
                            chunk_metadata[f"meta_{key}"] = str(value)
                    metadata.append(chunk_metadata)
                    ids.append(chunk.id)
                if documents:
                    try:
                        collection.add(
                            documents=documents,
                            embeddings=embeddings,
                            metadatas=metadata,
                            ids=ids
                        )
                        logger.info(f"Ajouté {len(documents)} chunks (embedding dim={dim}) à la collection {collection.name}")
                    except Exception as e:
                        logger.error(f"Erreur lors de l'ajout à la collection {collection.name}: {e}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à ChromaDB: {e}")
            return False

    def search(self, query_embedding: np.ndarray, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        try:
            where_clause = None
            if filters:
                where_clause = self._build_where_clause(filters)
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k,
                where=where_clause
            )
            search_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    search_result = SearchResult(
                        chunk_id=results['ids'][0][i],
                        content=results['documents'][0][i],
                        chunk_type=ChunkType(metadata.get('chunk_type', 'text')),
                        page_number=metadata.get('page_number', 0),
                        score=1.0 - results['distances'][0][i] if 'distances' in results else 1.0,
                        distance=results['distances'][0][i] if 'distances' in results else 0.0,
                        metadata=metadata
                    )
                    search_results.append(search_result)
            return search_results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche ChromaDB: {e}")
            return []

    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        where_clause = {}
        for key, value in filters.items():
            if key == "chunk_type":
                where_clause["chunk_type"] = {"$eq": value}
            elif key == "page_number":
                where_clause["page_number"] = {"$eq": value}
            elif key in ["min_page", "max_page"]:
                if "page_number" not in where_clause:
                    where_clause["page_number"] = {}
                if key == "min_page":
                    where_clause["page_number"]["$gte"] = value
                else:
                    where_clause["page_number"]["$lte"] = value
        return where_clause

    def delete_chunk(self, chunk_id: str) -> bool:
        try:
            self.collection.delete(ids=[chunk_id])
            logger.info(f"Chunk {chunk_id} supprimé de ChromaDB (serveur)")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du chunk {chunk_id}: {e}")
            return False

    def get_chunk_count(self) -> int:
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Erreur lors du comptage ChromaDB: {e}")
            return 0

    def clear(self) -> bool:
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Collection pour RAG multimodal",
                    "created_by": "multimodal_rag_pipeline"
                }
            )
            logger.info("Collection ChromaDB (serveur) vidée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du vidage ChromaDB: {e}")
            return False

class VectorStoreFactory:
    """Factory pour créer un store vectoriel ChromaDB uniquement"""
    @staticmethod
    def create_store(config: VectorStoreConfig) -> BaseVectorStore:
        return ChromaVectorStore(config)

def create_vector_store(config: VectorStoreConfig) -> BaseVectorStore:
    return VectorStoreFactory.create_store(config)