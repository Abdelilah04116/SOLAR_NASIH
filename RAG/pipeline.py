"""
Pipeline principale pour l'ingestion et l'indexation RAG multimodal
"""
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from models import (
    Document, Chunk, SearchResult, SearchQuery, 
    ProcessingResult, PipelineState, ProcessingStatus
)
from config import RAGPipelineConfig
from parsers import ParserFactory
from chunker import create_chunker
from question_generator import create_question_generator
from embedder import create_embedder
from vector_store import create_vector_store

# Configuration du logging
def setup_logging(config: RAGPipelineConfig):
    """Configure le système de logging"""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    # Création du répertoire de logs
    log_dir = Path(config.logs_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'pipeline.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

def is_image_query(query: str) -> bool:
    mots_cles = ["image", "photo", "montre", "affiche", "voir", "illustration"]
    return any(mot in query.lower() for mot in mots_cles)

class MultimodalRAGPipeline:
    """Pipeline principale pour l'ingestion et l'indexation RAG multimodal"""
    
    def __init__(self, config: Optional[RAGPipelineConfig] = None):
        self.config = config or RAGPipelineConfig()
        
        # Configuration du logging
        setup_logging(self.config)
        
        # Initialisation des composants
        self._initialize_components()
        
        # État de la pipeline
        self.state = PipelineState()
        
        logger.info("Pipeline RAG multimodal initialisée")
        logger.info(f"Configuration: {self._get_config_summary()}")
    
    def _initialize_components(self):
        """Initialise tous les composants de la pipeline"""
        try:
            # Parser factory
            self.parser_factory = ParserFactory(self.config.parsing)
            
            # Chunker
            self.chunker = create_chunker(self.config.chunking)
            
            # Générateur de questions
            self.question_generator = create_question_generator(self.config.question_generation)
            
            # Embedder
            self.embedder = create_embedder(self.config.embedding)
            
            # Vector store
            self.vector_store = create_vector_store(self.config.vector_store)
            
            logger.info("Tous les composants initialisés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des composants: {e}")
            raise
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la configuration"""
        return {
            "text_model": self.config.embedding.text_model_name,
            "image_model": self.config.embedding.image_model_name,
            "vector_store": self.config.vector_store.store_type,
            "chunk_size": self.config.chunking.text_chunk_size,
            "max_questions": self.config.question_generation.max_questions_per_chunk
        }
    
    def ingest_document(self, file_path: str) -> ProcessingResult:
        """Ingestion complète d'un document"""
        start_time = time.time()
        
        logger.info(f"Début de l'ingestion: {file_path}")
        
        try:
            # Vérification de l'existence du fichier
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
            
            # Étape 1: Parsing du document
            logger.info("Étape 1/5: Parsing du document")
            document = self._parse_document(file_path)
            
            # Étape 2: Chunking
            logger.info("Étape 2/5: Chunking du contenu")
            document = self._chunk_document(document)
            
            # Étape 3: Génération de questions hypothétiques
            logger.info("Étape 3/5: Génération de questions hypothétiques")
            document = self._generate_questions(document)
            
            # Étape 4: Génération d'embeddings
            logger.info("Étape 4/5: Génération d'embeddings")
            document = self._generate_embeddings(document)
            
            # Étape 5: Stockage vectoriel
            logger.info("Étape 5/5: Stockage vectoriel")
            success = self._store_chunks(document.chunks)
            
            if not success:
                raise Exception("Échec du stockage vectoriel")
            
            # Mise à jour de l'état
            document.update_status(ProcessingStatus.COMPLETED)
            self.state.update_stats(document)
            
            # Calcul des statistiques
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                success=True,
                document=document,
                processing_time=processing_time,
                chunks_created=len(document.chunks),
                embeddings_generated=len([c for c in document.chunks if c.embedding is not None])
            )
            
            logger.info(f"Ingestion terminée avec succès en {processing_time:.2f}s")
            logger.info(f"Statistiques: {document.get_statistics()}")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Erreur lors de l'ingestion: {e}"
            logger.error(error_msg)
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _parse_document(self, file_path: str) -> Document:
        """Parse un document"""
        try:
            parser = self.parser_factory.create_parser(file_path)
            document = parser.parse(file_path)
            
            logger.info(f"Parsing terminé: {len(document.parsed_content)} éléments extraits")
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing: {e}")
            raise
    
    def _chunk_document(self, document: Document) -> Document:
        """Découpe le document en chunks"""
        try:
            document = self.chunker.chunk_document(document)
            
            logger.info(f"Chunking terminé: {len(document.chunks)} chunks créés")
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors du chunking: {e}")
            raise
    
    def _generate_questions(self, document: Document) -> Document:
        """Génère des questions hypothétiques"""
        try:
            document.chunks = self.question_generator.generate_questions(document.chunks)
            
            total_questions = sum(len(c.hypothetical_questions or []) for c in document.chunks)
            logger.info(f"Questions générées: {total_questions} questions pour {len(document.chunks)} chunks")
            
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de questions: {e}")
            raise
    
    def _generate_embeddings(self, document: Document) -> Document:
        """Génère les embeddings"""
        try:
            document.chunks = self.embedder.embed_chunks(document.chunks)
            
            embedded_count = len([c for c in document.chunks if c.embedding is not None])
            logger.info(f"Embeddings générés: {embedded_count}/{len(document.chunks)} chunks")
            
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings: {e}")
            raise
    
    def _store_chunks(self, chunks: List[Chunk]) -> bool:
        """Stocke les chunks dans la base vectorielle"""
        try:
            success = self.vector_store.add_chunks(chunks)
            
            if success:
                logger.info(f"Stockage terminé: {len(chunks)} chunks ajoutés")
            else:
                logger.error("Échec du stockage vectoriel")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors du stockage: {e}")
            return False
    
    def ingest_multiple_documents(self, file_paths: List[str]) -> List[ProcessingResult]:
        """Ingestion multiple de documents"""
        logger.info(f"Début de l'ingestion multiple: {len(file_paths)} documents")
        
        results = []
        successful = 0
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Document {i}/{len(file_paths)}: {file_path}")
            
            result = self.ingest_document(file_path)
            results.append(result)
            
            if result.success:
                successful += 1
            else:
                logger.warning(f"Échec de l'ingestion: {file_path} - {result.error_message}")
        
        logger.info(f"Ingestion multiple terminée: {successful}/{len(file_paths)} documents traités avec succès")
        
        return results
    
    def search(self, query: str, k: int = 5, 
               filters: Optional[Dict[str, Any]] = None,
               query_type: str = "text") -> List[SearchResult]:
        logger.info(f"Recherche: '{query[:50]}...' (k={k})")
        try:
            # Détection automatique du type de requête
            if query_type == "text" and is_image_query(query):
                query_type = "image"
            # Génération de l'embedding de la requête
            query_embedding = self.embedder.embed_query(query, query_type)
            if len(query_embedding) == 0:
                logger.warning("Embedding de requête vide")
                return []
            # Recherche dans la base vectorielle
            if query_type == "image":
                from config import VectorStoreConfig
                from vector_store import ChromaVectorStore
                image_store_config = VectorStoreConfig(
                    collection_name=f"{self.config.vector_store.collection_name}_512",
                    chromadb_host=self.config.vector_store.chromadb_host,
                    chromadb_port=self.config.vector_store.chromadb_port,
                    store_path=self.config.vector_store.store_path
                )
                image_store = ChromaVectorStore(image_store_config)
                results = image_store.search(query_embedding, k, filters)
            else:
                results = self.vector_store.search(query_embedding, k, filters)
            logger.info(f"Recherche terminée: {len(results)} résultats trouvés")
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def search_with_query(self, search_query: SearchQuery) -> List[SearchResult]:
        """Recherche avec un objet SearchQuery"""
        return self.search(
            query=search_query.query_text,
            k=search_query.k,
            filters=search_query.filters,
            query_type=search_query.query_type
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la pipeline"""
        store_count = self.vector_store.get_chunk_count()
        
        stats = {
            "pipeline_state": self.state.to_dict(),
            "vector_store_count": store_count,
            "embedding_dimensions": self.embedder.get_embedding_dimensions(),
            "supported_formats": self.parser_factory.get_supported_formats(),
            "config_summary": self._get_config_summary()
        }
        
        return stats
    
    def clear_vector_store(self) -> bool:
        """Vide la base de données vectorielle"""
        logger.info("Vidage de la base vectorielle")
        
        try:
            success = self.vector_store.clear()
            
            if success:
                # Réinitialiser l'état
                self.state = PipelineState()
                logger.info("Base vectorielle vidée avec succès")
            else:
                logger.error("Échec du vidage de la base vectorielle")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage: {e}")
            return False
    
    def delete_document_chunks(self, file_path: str) -> bool:
        """Supprime les chunks d'un document spécifique"""
        logger.info(f"Suppression des chunks du document: {file_path}")
        
        # Cette fonctionnalité nécessiterait de stocker les associations document->chunks
        # Pour l'instant, nous retournons False car non implémenté
        logger.warning("Suppression de documents spécifiques non implémentée")
        return False
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un chunk par son ID (si supporté par le vector store)"""
        # Cette fonctionnalité dépend du type de vector store
        logger.warning("Récupération de chunk par ID non implémentée")
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de santé de la pipeline"""
        health = {
            "status": "healthy",
            "components": {},
            "errors": []
        }
        
        try:
            # Test du vector store
            count = self.vector_store.get_chunk_count()
            health["components"]["vector_store"] = {
                "status": "ok",
                "chunk_count": count
            }
        except Exception as e:
            health["components"]["vector_store"] = {
                "status": "error",
                "error": str(e)
            }
            health["errors"].append(f"Vector store: {e}")
        
        try:
            # Test de l'embedder
            test_embedding = self.embedder.embed_query("test")
            health["components"]["embedder"] = {
                "status": "ok",
                "embedding_dim": len(test_embedding)
            }
        except Exception as e:
            health["components"]["embedder"] = {
                "status": "error",
                "error": str(e)
            }
            health["errors"].append(f"Embedder: {e}")
        
        # Statut global
        if health["errors"]:
            health["status"] = "degraded" if len(health["errors"]) < 2 else "unhealthy"
        
        return health

def create_pipeline(config: Optional[RAGPipelineConfig] = None) -> MultimodalRAGPipeline:
    """Factory function pour créer une pipeline"""
    return MultimodalRAGPipeline(config)

# Fonctions utilitaires
def ingest_document_simple(file_path: str, 
                          vector_store_type: str = "chroma",
                          vector_store_path: str = "./vector_store") -> ProcessingResult:
    """Fonction utilitaire pour ingérer un document avec une configuration simple"""
    config = RAGPipelineConfig()
    config.vector_store.store_type = vector_store_type
    config.vector_store.store_path = vector_store_path
    
    pipeline = create_pipeline(config)
    return pipeline.ingest_document(file_path)

def search_simple(query: str, 
                 k: int = 5,
                 vector_store_type: str = "chroma",
                 vector_store_path: str = "./vector_store") -> List[SearchResult]:
    """Fonction utilitaire pour rechercher avec une configuration simple"""
    config = RAGPipelineConfig()
    config.vector_store.store_type = vector_store_type
    config.vector_store.store_path = vector_store_path
    
    pipeline = create_pipeline(config)
    return pipeline.search(query, k)