import logging
from typing import List, Dict, Any, Optional
import numpy as np
from src.vectorization.vector_store import VectorStore
from src.vectorization.embeddings.multimodal_embeddings import MultimodalEmbeddings

logger = logging.getLogger(__name__)

class VectorRetriever:
    """Vector-based retrieval using embeddings."""
    
    def __init__(self, 
                 vector_store: VectorStore,
                 embeddings: MultimodalEmbeddings,
                 collection_name: str = "multimodal_documents"):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.collection_name = collection_name
    
    def retrieve(self, 
                query: str,
                top_k: int = 5,
                doc_type: Optional[str] = None,
                score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Retrieve similar documents using vector search."""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.text_embedder.embed_text(query)
            
            # Prepare filters
            filter_conditions = {}
            if doc_type:
                filter_conditions['doc_type'] = doc_type
            
            # Search vector store
            results = self.vector_store.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.flatten(),
                top_k=top_k,
                filter_conditions=filter_conditions,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result['payload'].get('content', ''),
                    'metadata': result['payload'].get('metadata', {}),
                    'score': result['score'],
                    'retrieval_method': 'vector',
                    'doc_id': result['id'],
                    'source': result['payload'].get('source', '')
                })
            
            logger.info(f"Vector retrieval found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector retrieval failed: {str(e)}")
            return []
    
    def retrieve_multimodal(self,
                           query: str,
                           image_query: Optional[str] = None,
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve using multimodal queries."""
        try:
            results = []
            
            # Text-based retrieval
            if query:
                text_results = self.retrieve(query, top_k=top_k)
                results.extend(text_results)
            
            # Image-based retrieval (if image query provided)
            if image_query:
                image_embedding = self.embeddings.image_embedder.embed_text_for_image_search(image_query)
                
                image_results = self.vector_store.search(
                    collection_name=self.collection_name,
                    query_vector=image_embedding.flatten(),
                    top_k=top_k,
                    filter_conditions={'doc_type': 'image'}
                )
                
                for result in image_results:
                    results.append({
                        'content': result['payload'].get('content', ''),
                        'metadata': result['payload'].get('metadata', {}),
                        'score': result['score'],
                        'retrieval_method': 'image_vector',
                        'doc_id': result['id'],
                        'source': result['payload'].get('source', '')
                    })
            
            # Remove duplicates and sort by score
            unique_results = {}
            for result in results:
                doc_id = result['doc_id']
                if doc_id not in unique_results or result['score'] > unique_results[doc_id]['score']:
                    unique_results[doc_id] = result
            
            final_results = list(unique_results.values())
            final_results.sort(key=lambda x: x['score'], reverse=True)
            
            return final_results[:top_k]
            
        except Exception as e:
            logger.error(f"Multimodal retrieval failed: {str(e)}")
            return []
