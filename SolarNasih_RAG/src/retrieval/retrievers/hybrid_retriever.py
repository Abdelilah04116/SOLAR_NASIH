import logging
from typing import List, Dict, Any, Optional
from .vector_retriever import VectorRetriever
from .keyword_retriever import KeywordRetriever

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Hybrid retrieval combining vector and keyword search."""
    
    def __init__(self, 
                 vector_retriever: VectorRetriever,
                 keyword_retriever: KeywordRetriever,
                 vector_weight: float = 0.7,
                 keyword_weight: float = 0.3):
        
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    def retrieve(self, 
                query: str,
                top_k: int = 5,
                doc_type: Optional[str] = None,
                vector_top_k: Optional[int] = None,
                keyword_top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve documents using hybrid approach."""
        try:
            # Set retrieval limits
            vector_k = vector_top_k or min(top_k * 2, 20)
            keyword_k = keyword_top_k or min(top_k * 2, 20)
            
            # Get results from both retrievers
            vector_results = self.vector_retriever.retrieve(
                query, top_k=vector_k, doc_type=doc_type
            )
            
            keyword_results = self.keyword_retriever.retrieve(
                query, top_k=keyword_k, doc_type=doc_type
            )
            
            # Combine and re-rank results
            combined_results = self._combine_results(vector_results, keyword_results)
            
            # Sort by combined score and return top-k
            combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Clean up results
            final_results = []
            for result in combined_results[:top_k]:
                result['score'] = result['combined_score']
                result['retrieval_method'] = 'hybrid'
                del result['combined_score']
                final_results.append(result)
            
            logger.info(f"Hybrid retrieval found {len(final_results)} results")
            return final_results
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {str(e)}")
            return []
    
    def _combine_results(self, 
                        vector_results: List[Dict[str, Any]], 
                        keyword_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine and re-rank results from different retrievers."""
        try:
            # Normalize scores
            vector_results = self._normalize_scores(vector_results)
            keyword_results = self._normalize_scores(keyword_results)
            
            # Create combined results dictionary
            combined = {}
            
            # Add vector results
            for result in vector_results:
                doc_key = self._get_doc_key(result)
                combined[doc_key] = result.copy()
                combined[doc_key]['vector_score'] = result['score']
                combined[doc_key]['keyword_score'] = 0.0
            
            # Add keyword results
            for result in keyword_results:
                doc_key = self._get_doc_key(result)
                if doc_key in combined:
                    combined[doc_key]['keyword_score'] = result['score']
                else:
                    combined[doc_key] = result.copy()
                    combined[doc_key]['vector_score'] = 0.0
                    combined[doc_key]['keyword_score'] = result['score']
            
            # Calculate combined scores
            for doc_key, result in combined.items():
                vector_score = result['vector_score']
                keyword_score = result['keyword_score']
                
                # Weighted combination
                combined_score = (self.vector_weight * vector_score + 
                                self.keyword_weight * keyword_score)
                
                result['combined_score'] = combined_score
            
            return list(combined.values())
            
        except Exception as e:
            logger.error(f"Result combination failed: {str(e)}")
            return []
    
    def _normalize_scores(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize scores to 0-1 range."""
        if not results:
            return results
        
        scores = [result['score'] for result in results]
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0
        
        # Avoid division by zero
        score_range = max_score - min_score
        if score_range == 0:
            for result in results:
                result['score'] = 1.0
            return results
        
        # Normalize scores
        for result in results:
            normalized_score = (result['score'] - min_score) / score_range
            result['score'] = normalized_score
        
        return results
    
    def _get_doc_key(self, result: Dict[str, Any]) -> str:
        """Generate a unique key for a document."""
        content = result.get('content', '')
        source = result.get('source', '')
        chunk_id = result.get('metadata', {}).get('chunk_id', 0)
        
        return f"{source}_{chunk_id}_{hash(content[:100])}"

        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        
        return sanitized or 'unnamed_file'
    
    @staticmethod
    def validate_json(data: Any) -> bool:
        """Validate if data is valid JSON serializable."""
        try:
            import json
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_search_params(params: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate search parameters and return errors."""
        errors = {}
        
        # Validate query
        query = params.get('query', '')
        if not Validators.validate_query(query):
            errors['query'] = ['Query must be between 1 and 1000 characters']
        
        # Validate top_k
        top_k = params.get('top_k', 5)
        if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
            errors['top_k'] = ['top_k must be an integer between 1 and 100']
        
        # Validate score_threshold
        score_threshold = params.get('score_threshold')
        if score_threshold is not None:
            if not isinstance(score_threshold, (int, float)) or score_threshold < 0 or score_threshold > 1:
                errors['score_threshold'] = ['score_threshold must be a number between 0 and 1']
        
        # Validate method
        method = params.get('method', 'hybrid')
        valid_methods = ['vector', 'keyword', 'hybrid']
        if method not in valid_methods:
            errors['method'] = [f'method must be one of: {", ".join(valid_methods)}']
        
        return errors