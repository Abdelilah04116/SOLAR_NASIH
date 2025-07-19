import logging
from typing import List, Dict, Any, Optional
import uuid
from .embeddings.multimodal_embeddings import MultimodalEmbeddings
from .vector_store import VectorStore
from config.settings import settings

logger = logging.getLogger(__name__)

class Indexer:
    """Index documents into vector store."""
    
    def __init__(self, 
                 vector_store: Optional[VectorStore] = None,
                 embeddings: Optional[MultimodalEmbeddings] = None):
        
        self.vector_store = vector_store or VectorStore(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        
        self.embeddings = embeddings or MultimodalEmbeddings(
            text_model=settings.default_text_model,
            image_model=settings.default_image_model
        )
        
        self.collection_name = settings.vector_collection_name
        
        # Create collection if it doesn't exist
        self.vector_store.create_collection(
            self.collection_name,
            settings.vector_size
        )
    
    def index_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Index a list of document chunks."""
        try:
            vectors = []
            payloads = []
            ids = []
            
            for chunk in chunks:
                try:
                    # Generate embeddings
                    chunk_embeddings = self.embeddings.embed_chunk(chunk)
                    
                    # Get primary embedding for storage
                    doc_type = chunk.get('metadata', {}).get('doc_type', 'text')
                    primary_embedding = self.embeddings.get_primary_embedding(
                        chunk_embeddings, doc_type
                    )
                    
                    if primary_embedding.size == 0:
                        logger.warning(f"No embedding generated for chunk: {chunk.get('metadata', {}).get('chunk_id', 'unknown')}")
                        continue
                    
                    # Prepare data for storage
                    chunk_id = str(uuid.uuid4())
                    
                    payload = {
                        'content': chunk.get('content', ''),
                        'metadata': chunk.get('metadata', {}),
                        'doc_type': doc_type,
                        'chunk_id': chunk.get('metadata', {}).get('chunk_id', 0),
                        'source': chunk.get('metadata', {}).get('file_path', ''),
                        'embeddings_available': list(chunk_embeddings.keys())
                    }
                    
                    vectors.append(primary_embedding.flatten())
                    payloads.append(payload)
                    ids.append(chunk_id)
                    
                except Exception as e:
                    logger.warning(f"Failed to process chunk: {str(e)}")
                    continue
            
            if not vectors:
                logger.warning("No vectors to index")
                return False
            
            # Add to vector store
            success = self.vector_store.add_vectors(
                self.collection_name,
                vectors,
                payloads,
                ids
            )
            
            if success:
                logger.info(f"Successfully indexed {len(vectors)} chunks")
            
            return success
            
        except Exception as e:
            logger.error(f"Indexing failed: {str(e)}")
            return False
    
    def index_single_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Index a single chunk."""
        return self.index_chunks([chunk])
    
    def search_similar(self, 
                      query: str,
                      doc_type: Optional[str] = None,
                      top_k: int = 5,
                      score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.text_embedder.embed_text(query)
            
            # Prepare filter conditions
            filter_conditions = {}
            if doc_type:
                filter_conditions['doc_type'] = doc_type
            
            # Search
            results = self.vector_store.search(
                self.collection_name,
                query_embedding.flatten(),
                top_k=top_k,
                filter_conditions=filter_conditions,
                score_threshold=score_threshold
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []