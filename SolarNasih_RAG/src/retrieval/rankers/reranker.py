import logging
from typing import List, Dict, Any, Optional
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class Reranker:
    """Re-rank retrieved documents using cross-encoder models."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Reranker model '{model_name}' loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load reranker model: {str(e)}")
            self.model = None
            self.tokenizer = None
    
    def rerank(self, 
              query: str, 
              results: List[Dict[str, Any]], 
              top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Re-rank results using cross-encoder."""
        try:
            if not self.model:
                logger.warning("Reranker model not available, returning original ranking")
                return results[:top_k] if top_k else results
            
            if not results:
                return results
            
            # Prepare query-document pairs
            pairs = []
            for result in results:
                content = result.get('content', '')
                # Truncate content to avoid token limits
                content = self._truncate_text(content, max_length=400)
                pairs.append([query, content])
            
            # Tokenize pairs
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Get relevance scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.nn.functional.softmax(outputs.logits, dim=-1)[:, 1]  # Relevance score
                scores = scores.cpu().numpy()
            
            # Update results with reranking scores
            reranked_results = []
            for i, result in enumerate(results):
                result_copy = result.copy()
                result_copy['rerank_score'] = float(scores[i])
                result_copy['original_score'] = result.get('score', 0.0)
                result_copy['score'] = float(scores[i])  # Use rerank score as main score
                reranked_results.append(result_copy)
            
            # Sort by rerank score
            reranked_results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Return top-k results
            final_results = reranked_results[:top_k] if top_k else reranked_results
            
            logger.info(f"Reranked {len(results)} results, returning top {len(final_results)}")
            return final_results
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            return results[:top_k] if top_k else results
    
    def _truncate_text(self, text: str, max_length: int = 400) -> str:
        """Truncate text to maximum length while preserving word boundaries."""
        if len(text) <= max_length:
            return text
        
        # Find the last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we don't lose too much
            return truncated[:last_space]
        else:
            return truncated

