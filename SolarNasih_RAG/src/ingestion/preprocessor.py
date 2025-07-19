import logging
from typing import List, Dict, Any
from pathlib import Path

from .document_loader import Document, DocumentLoader
from .chunking.multimodal_chunker import MultimodalChunker

logger = logging.getLogger(__name__)

class Preprocessor:
    """Main preprocessing pipeline for documents."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.document_loader = DocumentLoader()
        self.chunker = MultimodalChunker(chunk_size, chunk_overlap)
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single document through the complete pipeline."""
        try:
            # Load document
            document = self.document_loader.load_document(file_path)
            
            # Chunk document
            chunks = self.chunker.chunk_document(
                document.content, 
                document.metadata, 
                document.doc_type
            )
            
            logger.info(f"Processed {file_path}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Document processing failed for {file_path}: {str(e)}")
            raise
    
    def process_documents(self, directory: Path) -> List[Dict[str, Any]]:
        """Process all documents in a directory."""
        all_chunks = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    chunks = self.process_document(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Processed {len(all_chunks)} total chunks from {directory}")
        return all_chunks

