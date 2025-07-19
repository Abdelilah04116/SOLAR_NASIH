import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store interface using Qdrant."""
    
    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None):
        try:
            self.client = QdrantClient(url=url, api_key=api_key)
            self.collections = {}
            logger.info(f"Connected to Qdrant at {url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise
    
    def create_collection(self, 
                         collection_name: str, 
                         vector_size: int, 
                         distance: Distance = Distance.COSINE) -> bool:
        """Create a new collection."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            existing_names = [col.name for col in collections]
            
            if collection_name in existing_names:
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
            
            self.collections[collection_name] = {
                'vector_size': vector_size,
                'distance': distance
            }
            
            logger.info(f"Created collection '{collection_name}' with size {vector_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    def add_vectors(self, 
                   collection_name: str,
                   vectors: List[np.ndarray],
                   payloads: List[Dict[str, Any]],
                   ids: Optional[List[Union[int, str]]] = None) -> bool:
        """Add vectors to collection."""
        try:
            if not ids:
                ids = list(range(len(vectors)))
            
            points = []
            for i, (vector, payload) in enumerate(zip(vectors, payloads)):
                point = PointStruct(
                    id=ids[i],
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                    payload=payload
                )
                points.append(point)
            
            # Upload points in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
            
            logger.info(f"Added {len(vectors)} vectors to '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors: {str(e)}")
            return False
    
    def search(self, 
              collection_name: str,
              query_vector: np.ndarray,
              top_k: int = 5,
              filter_conditions: Optional[Dict[str, Any]] = None,
              score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                search_filter = Filter(must=conditions)
            
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
                limit=top_k,
                query_filter=search_filter,
                score_threshold=score_threshold
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False