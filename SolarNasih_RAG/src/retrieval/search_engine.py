import logging
from typing import List, Dict, Any, Optional
from .retrievers.vector_retriever import VectorRetriever
from .retrievers.keyword_retriever import KeywordRetriever
from .retrievers.hybrid_retriever import HybridRetriever
from .rankers.score_fusion import ScoreFusion
from .rankers.reranker import Reranker

logger = logging.getLogger(__name__)

class SearchEngine:
    """Main search engine orchestrating different retrieval methods."""
    
    def __init__(self,
                 vector_retriever: VectorRetriever,
                 keyword_retriever: Optional[KeywordRetriever] = None,
                 use_reranking: bool = True):
        
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        
        # Initialize hybrid retriever if keyword retriever is available
        if keyword_retriever:
            self.hybrid_retriever = HybridRetriever(vector_retriever, keyword_retriever)
        else:
            self.hybrid_retriever = None
        
        # Initialize reranker
        self.reranker = Reranker() if use_reranking else None
        
        logger.info("Search engine initialized")
    
    def search(self,
              query: str,
              method: str = "hybrid",
              top_k: int = 5,
              doc_type: Optional[str] = None,
              use_reranking: bool = True,
              score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Perform search using specified method."""
        try:
            results = []
            
            if method == "vector":
                results = self.vector_retriever.retrieve(
                    query=query,
                    top_k=top_k * 2 if use_reranking else top_k,  # Get more for reranking
                    doc_type=doc_type,
                    score_threshold=score_threshold
                )
                
            elif method == "keyword" and self.keyword_retriever:
                results = self.keyword_retriever.retrieve(
                    query=query,
                    top_k=top_k * 2 if use_reranking else top_k,
                    doc_type=doc_type
                )
                
            elif method == "hybrid" and self.hybrid_retriever:
                results = self.hybrid_retriever.retrieve(
                    query=query,
                    top_k=top_k * 2 if use_reranking else top_k,
                    doc_type=doc_type
                )
                
            else:
                # Fallback to vector search
                logger.warning(f"Method '{method}' not available, using vector search")
                results = self.vector_retriever.retrieve(
                    query=query,
                    top_k=top_k * 2 if use_reranking else top_k,
                    doc_type=doc_type,
                    score_threshold=score_threshold
                )
            
            # Apply reranking if enabled
            if use_reranking and self.reranker and results:
                results = self.reranker.rerank(query, results, top_k=top_k)
            else:
                results = results[:top_k]
            
            # Filter by score threshold if specified
            if score_threshold:
                results = [r for r in results if r['score'] >= score_threshold]
            
            logger.info(f"Search completed: {len(results)} results returned")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def multimodal_search(self,
                         text_query: Optional[str] = None,
                         image_query: Optional[str] = None,
                         top_k: int = 5,
                         use_reranking: bool = True) -> List[Dict[str, Any]]:
        """Perform multimodal search."""
        try:
            all_results = []
            
            # Text-based search
            if text_query:
                text_results = self.vector_retriever.retrieve(
                    query=text_query,
                    top_k=top_k
                )
                all_results.append(text_results)
            
            # Image-based search
            if image_query:
                image_results = self.vector_retriever.retrieve_multimodal(
                    query="",
                    image_query=image_query,
                    top_k=top_k
                )
                all_results.append(image_results)
            
            if not all_results:
                return []
            
            # Combine results using RRF
            if len(all_results) > 1:
                combined_results = ScoreFusion.reciprocal_rank_fusion(all_results)
            else:
                combined_results = all_results[0]
            
            # Apply reranking
            if use_reranking and self.reranker and text_query:
                combined_results = self.reranker.rerank(text_query, combined_results, top_k=top_k)
            else:
                combined_results = combined_results[:top_k]
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Multimodal search failed: {str(e)}")
            return []
    
    def index_documents_for_keyword_search(self, documents: List[Dict[str, Any]]):
        """Index documents for keyword search."""
        if self.keyword_retriever:
            self.keyword_retriever.index_documents(documents)
            logger.info("Documents indexed for keyword search")

