import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Build context for generation from retrieved documents."""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def build_context(self, 
                     retrieved_docs: List[Dict[str, Any]],
                     query: str,
                     prioritize_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Build context from retrieved documents."""
        try:
            if not retrieved_docs:
                return []
            
            # Group documents by type
            docs_by_type = defaultdict(list)
            for doc in retrieved_docs:
                doc_type = doc.get('metadata', {}).get('doc_type', 'text')
                docs_by_type[doc_type].append(doc)
            
            # Prioritize document types if specified
            if prioritize_types:
                ordered_docs = []
                for doc_type in prioritize_types:
                    ordered_docs.extend(docs_by_type.get(doc_type, []))
                
                # Add remaining documents
                for doc_type, docs in docs_by_type.items():
                    if doc_type not in prioritize_types:
                        ordered_docs.extend(docs)
                
                retrieved_docs = ordered_docs
            
            # Filter and truncate context
            context_docs = self._filter_and_truncate(retrieved_docs)
            
            # Enhance context with metadata
            enhanced_context = self._enhance_context(context_docs)
            
            logger.info(f"Built context with {len(enhanced_context)} documents")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Context building failed: {str(e)}")
            return []
    
    def _filter_and_truncate(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and truncate documents to fit context length."""
        filtered_docs = []
        current_length = 0
        
        for doc in docs:
            content = doc.get('content', '')
            content_length = len(content)
            
            if current_length + content_length <= self.max_context_length:
                filtered_docs.append(doc)
                current_length += content_length
            else:
                # Truncate the document to fit
                remaining_space = self.max_context_length - current_length
                if remaining_space > 200:  # Only include if significant space remains
                    truncated_doc = doc.copy()
                    truncated_doc['content'] = content[:remaining_space] + "..."
                    truncated_doc['truncated'] = True
                    filtered_docs.append(truncated_doc)
                break
        
        return filtered_docs
    
    def _enhance_context(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance context with additional metadata."""
        enhanced_docs = []
        
        for i, doc in enumerate(docs):
            enhanced_doc = doc.copy()
            metadata = enhanced_doc.get('metadata', {})
            
            # Add context-specific metadata
            enhanced_doc['context_rank'] = i + 1
            enhanced_doc['relevance_score'] = doc.get('score', 0.0)
            
            # Add source information
            source = doc.get('source', metadata.get('file_path', 'Unknown'))
            enhanced_doc['source_info'] = {
                'file': source,
                'type': metadata.get('doc_type', 'text'),
                'chunk_id': metadata.get('chunk_id', 0)
            }
            
            enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs

