import logging
from typing import List, Dict, Any, Union
from .text_chunker import TextChunker
from .image_chunker import ImageChunker

logger = logging.getLogger(__name__)

class MultimodalChunker:
    """Coordinated chunking for multimodal documents."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.text_chunker = TextChunker(chunk_size, chunk_overlap)
        self.image_chunker = ImageChunker()
    
    def chunk_document(self, content: str, metadata: Dict[str, Any], doc_type: str) -> List[Dict[str, Any]]:
        """Chunk document based on its type."""
        try:
            if doc_type in ['text', 'pdf']:
                return self.text_chunker.chunk_text(content, metadata)
            elif doc_type == 'image':
                # For images, we primarily use the description but can also chunk the image
                text_chunks = self.text_chunker.chunk_text(content, metadata)
                return text_chunks
            elif doc_type in ['audio', 'video']:
                # For audio/video, chunk the transcription
                return self.text_chunker.chunk_text(content, metadata)
            else:
                raise ValueError(f"Unsupported document type for chunking: {doc_type}")
                
        except Exception as e:
            logger.error(f"Multimodal chunking failed: {str(e)}")
            raise
    
    def chunk_mixed_content(self, content_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk mixed content with temporal/spatial awareness."""
        all_chunks = []
        
        for i, item in enumerate(content_items):
            try:
                content = item.get('content', '')
                metadata = item.get('metadata', {})
                doc_type = metadata.get('doc_type', 'text')
                
                # Add sequence information
                metadata['sequence_index'] = i
                metadata['total_items'] = len(content_items)
                
                chunks = self.chunk_document(content, metadata, doc_type)
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.warning(f"Failed to chunk item {i}: {str(e)}")
                continue
        
        return all_chunks