import logging
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

class KeywordRetriever:
    """Keyword-based retrieval using BM25 algorithm."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1  # Term frequency saturation parameter
        self.b = b    # Length normalization parameter
        self.documents = []
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.idf_scores = {}
        self.term_frequencies = []
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index documents for keyword search."""
        try:
            self.documents = documents
            self.term_frequencies = []
            self.doc_lengths = []
            
            # Process each document
            all_terms = set()
            for doc in documents:
                content = doc.get('content', '')
                terms = self._tokenize(content)
                
                # Calculate term frequencies
                tf = Counter(terms)
                self.term_frequencies.append(tf)
                self.doc_lengths.append(len(terms))
                all_terms.update(terms)
            
            # Calculate average document length
            self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
            
            # Calculate IDF scores
            self.idf_scores = {}
            num_docs = len(documents)
            
            for term in all_terms:
                # Count documents containing the term
                doc_freq = sum(1 for tf in self.term_frequencies if term in tf)
                # Calculate IDF
                idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5))
                self.idf_scores[term] = max(idf, 0)  # Ensure non-negative
            
            logger.info(f"Indexed {len(documents)} documents for keyword search")
            
        except Exception as e:
            logger.error(f"Document indexing failed: {str(e)}")
            raise
    
    def retrieve(self, 
                query: str,
                top_k: int = 5,
                doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve documents using BM25 scoring."""
        try:
            if not self.documents:
                logger.warning("No documents indexed for keyword search")
                return []
            
            query_terms = self._tokenize(query)
            scores = []
            
            # Calculate BM25 score for each document
            for i, doc in enumerate(self.documents):
                # Apply document type filter
                if doc_type and doc.get('metadata', {}).get('doc_type') != doc_type:
                    scores.append(0)
                    continue
                
                score = self._calculate_bm25_score(query_terms, i)
                scores.append(score)
            
            # Get top-k results
            doc_scores = list(zip(self.documents, scores, range(len(scores))))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for doc, score, idx in doc_scores[:top_k]:
                if score > 0:  # Only include documents with positive scores
                    results.append({
                        'content': doc.get('content', ''),
                        'metadata': doc.get('metadata', {}),
                        'score': score,
                        'retrieval_method': 'keyword',
                        'doc_id': idx,
                        'source': doc.get('metadata', {}).get('file_path', '')
                    })
            
            logger.info(f"Keyword retrieval found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Keyword retrieval failed: {str(e)}")
            return []
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Convert to lowercase and split on non-alphanumeric characters
        text = text.lower()
        terms = re.findall(r'\b\w+\b', text)
        
        # Filter out very short terms
        terms = [term for term in terms if len(term) > 2]
        
        return terms
    
    def _calculate_bm25_score(self, query_terms: List[str], doc_index: int) -> float:
        """Calculate BM25 score for a document."""
        score = 0
        tf_doc = self.term_frequencies[doc_index]
        doc_length = self.doc_lengths[doc_index]
        
        for term in query_terms:
            if term in tf_doc and term in self.idf_scores:
                tf = tf_doc[term]
                idf = self.idf_scores[term]
                
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                
                score += idf * (numerator / denominator)
        
        return score