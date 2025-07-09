"""
Module de stockage vectoriel pour la base de données de vecteurs
"""
import logging
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np

# Imports pour ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Imports pour FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from models import Chunk, SearchResult, SearchQuery, ChunkType
from config import VectorStoreConfig

logger = logging.getLogger(__name__)

class BaseVectorStore(ABC):
    """Interface abstraite pour les bases de données vectorielles"""
    
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.store_path = Path(config.store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """Ajoute des chunks à la base vectorielle"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Recherche dans la base vectorielle"""
        pass
    
    @abstractmethod
    def delete_chunk(self, chunk_id: str) -> bool:
        """Supprime un chunk de la base"""
        pass
    
    @abstractmethod
    def get_chunk_count(self) -> int:
        """Retourne le nombre de chunks stockés"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Vide la base de données"""
        pass

class ChromaVectorStore(BaseVectorStore):
    """Implémentation avec ChromaDB"""
    
    def __init__(self, config: VectorStoreConfig):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB n'est pas installé. Installer avec: pip install chromadb")
        
        super().__init__(config)
        self.collection_name = config.collection_name
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client ChromaDB"""
        try:
            # Configuration pour le client persistant
            self.client = chromadb.PersistentClient(
                path=str(self.store_path)
            )
            
            # Création ou récupération de la collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Collection pour RAG multimodal",
                    "created_by": "multimodal_rag_pipeline"
                }
            )
            
            logger.info(f"ChromaDB initialisé: {self.collection.count()} documents existants")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de ChromaDB: {e}")
            raise
    
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """Ajoute des chunks à ChromaDB"""
        if not chunks:
            return True
        
        try:
            documents = []
            embeddings = []
            metadata = []
            ids = []
            
            for chunk in chunks:
                if chunk.embedding is not None and len(chunk.embedding) > 0:
                    documents.append(chunk.content)
                    embeddings.append(chunk.embedding.tolist())
                    
                    # Préparation des métadonnées (ChromaDB n'accepte que certains types)
                    chunk_metadata = {
                        "chunk_type": chunk.chunk_type.value,
                        "page_number": chunk.page_number,
                        "created_at": chunk.created_at.isoformat(),
                        "processing_status": chunk.processing_status.value
                    }
                    
                    # Ajouter les questions hypothétiques comme string
                    if chunk.hypothetical_questions:
                        chunk_metadata["questions"] = " | ".join(chunk.hypothetical_questions)
                    
                    # Ajouter les métadonnées additionnelles (en tant que strings)
                    for key, value in chunk.metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            chunk_metadata[f"meta_{key}"] = value
                        else:
                            chunk_metadata[f"meta_{key}"] = str(value)
                    
                    metadata.append(chunk_metadata)
                    ids.append(chunk.id)
            
            if documents:
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadata,
                    ids=ids
                )
                
                logger.info(f"Ajouté {len(documents)} chunks à ChromaDB")
                return True
            else:
                logger.warning("Aucun chunk avec embedding valide à ajouter")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à ChromaDB: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Recherche dans ChromaDB"""
        try:
            # Construction des filtres ChromaDB
            where_clause = None
            if filters:
                where_clause = self._build_where_clause(filters)
            
            # Recherche
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k,
                where=where_clause
            )
            
            # Conversion en SearchResult
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
        """Construit la clause WHERE pour ChromaDB"""
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
        """Supprime un chunk de ChromaDB"""
        try:
            self.collection.delete(ids=[chunk_id])
            logger.info(f"Chunk {chunk_id} supprimé de ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du chunk {chunk_id}: {e}")
            return False
    
    def get_chunk_count(self) -> int:
        """Retourne le nombre de chunks dans ChromaDB"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Erreur lors du comptage ChromaDB: {e}")
            return 0
    
    def clear(self) -> bool:
        """Vide la collection ChromaDB"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Collection pour RAG multimodal",
                    "created_by": "multimodal_rag_pipeline"
                }
            )
            logger.info("Collection ChromaDB vidée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du vidage ChromaDB: {e}")
            return False

class FAISSVectorStore(BaseVectorStore):
    """Implémentation avec FAISS"""
    
    def __init__(self, config: VectorStoreConfig):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS n'est pas installé. Installer avec: pip install faiss-cpu")
        
        super().__init__(config)
        self.index_file = self.store_path / "faiss_index.bin"
        self.metadata_file = self.store_path / "metadata.json"
        
        self.index = None
        self.chunk_metadata = {}
        self.id_to_index = {}
        self.index_to_id = {}
        self.dimension = None
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Charge l'index existant ou en crée un nouveau"""
        if self.index_file.exists() and self.metadata_file.exists():
            self._load_index()
        else:
            logger.info("Création d'un nouvel index FAISS")
    
    def _load_index(self):
        """Charge l'index FAISS existant"""
        try:
            self.index = faiss.read_index(str(self.index_file))
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunk_metadata = data.get('chunk_metadata', {})
                self.id_to_index = data.get('id_to_index', {})
                self.index_to_id = {v: k for k, v in self.id_to_index.items()}
                self.dimension = data.get('dimension')
            
            logger.info(f"Index FAISS chargé: {self.index.ntotal} vecteurs, dimension {self.dimension}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'index FAISS: {e}")
            self.index = None
            self.chunk_metadata = {}
            self.id_to_index = {}
            self.index_to_id = {}
    
    def _save_index(self):
        """Sauvegarde l'index FAISS"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))
                
                data = {
                    'chunk_metadata': self.chunk_metadata,
                    'id_to_index': self.id_to_index,
                    'dimension': self.dimension
                }
                
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.debug("Index FAISS sauvegardé")
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde FAISS: {e}")
    
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """Ajoute des chunks à FAISS"""
        if not chunks:
            return True
        
        try:
            embeddings = []
            valid_chunks = []
            
            for chunk in chunks:
                if chunk.embedding is not None and len(chunk.embedding) > 0:
                    embeddings.append(chunk.embedding)
                    valid_chunks.append(chunk)
            
            if not embeddings:
                logger.warning("Aucun chunk avec embedding valide à ajouter")
                return False
            
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Initialisation de l'index si nécessaire
            if self.index is None:
                self.dimension = embeddings_array.shape[1]
                
                if self.config.faiss_index_type == "flat":
                    if self.config.faiss_metric == "L2":
                        self.index = faiss.IndexFlatL2(self.dimension)
                    else:
                        self.index = faiss.IndexFlatIP(self.dimension)
                elif self.config.faiss_index_type == "ivf":
                    quantizer = faiss.IndexFlatL2(self.dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
                    # Entraînement nécessaire pour IVF
                    if len(embeddings_array) >= 100:
                        self.index.train(embeddings_array)
                else:
                    # Fallback sur flat L2
                    self.index = faiss.IndexFlatL2(self.dimension)
                
                logger.info(f"Index FAISS créé: {self.config.faiss_index_type}, dimension {self.dimension}")
            
            # Ajout des vecteurs
            start_index = self.index.ntotal
            self.index.add(embeddings_array)
            
            # Mise à jour des métadonnées
            for i, chunk in enumerate(valid_chunks):
                current_index = start_index + i
                self.id_to_index[chunk.id] = current_index
                self.index_to_id[current_index] = chunk.id
                
                self.chunk_metadata[chunk.id] = {
                    "content": chunk.content,
                    "chunk_type": chunk.chunk_type.value,
                    "page_number": chunk.page_number,
                    "created_at": chunk.created_at.isoformat(),
                    "processing_status": chunk.processing_status.value,
                    "hypothetical_questions": chunk.hypothetical_questions or [],
                    "metadata": chunk.metadata
                }
            
            # Sauvegarde
            self._save_index()
            
            logger.info(f"Ajouté {len(valid_chunks)} chunks à FAISS")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à FAISS: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Recherche dans FAISS"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        try:
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            
            # Recherche FAISS
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            search_results = []
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # Pas de résultat trouvé
                    continue
                
                chunk_id = self.index_to_id.get(idx)
                if chunk_id is None or chunk_id not in self.chunk_metadata:
                    continue
                
                metadata = self.chunk_metadata[chunk_id]
                
                # Application des filtres
                if filters and not self._apply_filters(metadata, filters):
                    continue
                
                # Calcul du score (inverse de la distance pour L2)
                score = 1.0 / (1.0 + distance) if self.config.faiss_metric == "L2" else distance
                
                search_result = SearchResult(
                    chunk_id=chunk_id,
                    content=metadata["content"],
                    chunk_type=ChunkType(metadata["chunk_type"]),
                    page_number=metadata["page_number"],
                    score=score,
                    distance=float(distance),
                    metadata=metadata["metadata"]
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche FAISS: {e}")
            return []
    
    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Applique les filtres aux métadonnées"""
        for key, value in filters.items():
            if key == "chunk_type":
                if metadata.get("chunk_type") != value:
                    return False
            elif key == "page_number":
                if metadata.get("page_number") != value:
                    return False
            elif key == "min_page":
                if metadata.get("page_number", 0) < value:
                    return False
            elif key == "max_page":
                if metadata.get("page_number", float('inf')) > value:
                    return False
        
        return True
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Supprime un chunk de FAISS (marque comme supprimé)"""
        try:
            if chunk_id in self.chunk_metadata:
                del self.chunk_metadata[chunk_id]
                
                if chunk_id in self.id_to_index:
                    idx = self.id_to_index[chunk_id]
                    del self.id_to_index[chunk_id]
                    if idx in self.index_to_id:
                        del self.index_to_id[idx]
                
                self._save_index()
                logger.info(f"Chunk {chunk_id} supprimé de FAISS")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du chunk {chunk_id}: {e}")
            return False
    
    def get_chunk_count(self) -> int:
        """Retourne le nombre de chunks dans FAISS"""
        return len(self.chunk_metadata)
    
    def clear(self) -> bool:
        """Vide l'index FAISS"""
        try:
            self.index = None
            self.chunk_metadata = {}
            self.id_to_index = {}
            self.index_to_id = {}
            self.dimension = None
            
            # Supprimer les fichiers
            if self.index_file.exists():
                self.index_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            logger.info("Index FAISS vidé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage FAISS: {e}")
            return False

class VectorStoreFactory:
    """Factory pour créer des stores vectoriels"""
    
    @staticmethod
    def create_store(config: VectorStoreConfig) -> BaseVectorStore:
        """Crée un store vectoriel selon la configuration"""
        if config.store_type.lower() == "chroma":
            return ChromaVectorStore(config)
        elif config.store_type.lower() == "faiss":
            return FAISSVectorStore(config)
        else:
            raise ValueError(f"Type de store non supporté: {config.store_type}")

def create_vector_store(config: VectorStoreConfig) -> BaseVectorStore:
    """Function utilitaire pour créer un store vectoriel"""
    return VectorStoreFactory.create_store(config)