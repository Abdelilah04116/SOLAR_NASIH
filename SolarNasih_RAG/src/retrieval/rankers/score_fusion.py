import logging
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class ScoreFusion:
    """Advanced score fusion techniques for combining retrieval results."""
    
    @staticmethod
    def reciprocal_rank_fusion(results_list: List[List[Dict[str, Any]]], 
                              k: int = 60) -> List[Dict[str, Any]]:
        """Combine results using Reciprocal Rank Fusion (RRF)."""
        try:
            # Collect all unique documents
            all_docs = {}
            
            for results in results_list:
                for rank, result in enumerate(results):
                    doc_key = ScoreFusion._get_doc_key(result)
                    
                    if doc_key not in all_docs:
                        all_docs[doc_key] = {
                            'result': result,
                            'rrf_score': 0.0,
                            'rank_sum': 0,
                            'appearances': 0
                        }
                    
                    # Add RRF score: 1 / (k + rank)
                    all_docs[doc_key]['rrf_score'] += 1.0 / (k + rank + 1)
                    all_docs[doc_key]['rank_sum'] += rank + 1
                    all_docs[doc_key]['appearances'] += 1
            
            # Create final ranked list
            final_results = []
            for doc_info in all_docs.values():
                result = doc_info['result'].copy()
                result['score'] = doc_info['rrf_score']
                result['fusion_method'] = 'rrf'
                result['appearances'] = doc_info['appearances']
                final_results.append(result)
            
            # Sort by RRF score
            final_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"RRF fusion combined {len(final_results)} unique documents")
            return final_results
            
        except Exception as e:
            logger.error(f"RRF fusion failed: {str(e)}")
            return []
    
    @staticmethod
    def weighted_score_fusion(results_list: List[List[Dict[str, Any]]], 
                             weights: List[float]) -> List[Dict[str, Any]]:
        """Combine results using weighted score fusion."""
        try:
            if len(results_list) != len(weights):
                raise ValueError("Number of result lists must match number of weights")
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Collect all unique documents
            all_docs = {}
            
            for i, results in enumerate(results_list):
                # Normalize scores within this result set
                if results:
                    scores = [r['score'] for r in results]
                    max_score = max(scores)
                    min_score = min(scores)
                    score_range = max_score - min_score if max_score != min_score else 1.0
                    
                    for result in results:
                        doc_key = ScoreFusion._get_doc_key(result)
                        normalized_score = (result['score'] - min_score) / score_range
                        weighted_score = normalized_score * weights[i]
                        
                        if doc_key not in all_docs:
                            all_docs[doc_key] = {
                                'result': result,
                                'weighted_score': 0.0,
                                'component_scores': []
                            }
                        
                        all_docs[doc_key]['weighted_score'] += weighted_score
                        all_docs[doc_key]['component_scores'].append(weighted_score)
            
            # Create final ranked list
            final_results = []
            for doc_info in all_docs.values():
                result = doc_info['result'].copy()
                result['score'] = doc_info['weighted_score']
                result['fusion_method'] = 'weighted'
                final_results.append(result)
            
            # Sort by weighted score
            final_results.sort(key=lambda x: x['score'], reverse=True)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Weighted fusion failed: {str(e)}")
            return []
    
    @staticmethod
    def _get_doc_key(result: Dict[str, Any]) -> str:
        """Generate a unique key for a document."""
        content = result.get('content', '')
        source = result.get('source', '')
        chunk_id = result.get('metadata', {}).get('chunk_id', 0)
        return f"{source}_{chunk_id}_{hash(content[:100])}"

