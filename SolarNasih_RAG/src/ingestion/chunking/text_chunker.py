import logging
from typing import List, Dict, Any
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class TextChunker:
    """Intelligent text chunking with semantic awareness."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into semantic chunks."""
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **metadata,
                    'chunk_id': i,
                    'chunk_type': 'text',
                    'chunk_size': len(chunk),
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                
                chunk_objects.append({
                    'content': chunk,
                    'metadata': chunk_metadata
                })
            
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()