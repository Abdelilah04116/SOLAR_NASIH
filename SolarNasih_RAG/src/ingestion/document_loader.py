import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging
from dataclasses import dataclass

from .extractors.text_extractor import TextExtractor
from .extractors.image_extractor import ImageExtractor
from .extractors.audio_extractor import AudioExtractor
from .extractors.video_extractor import VideoExtractor

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document representation."""
    content: str
    metadata: Dict[str, Any]
    doc_type: str
    source: str
    chunks: Optional[List[Dict[str, Any]]] = None

class DocumentLoader:
    """Main document loader for all file types."""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.audio_extractor = AudioExtractor()
        self.video_extractor = VideoExtractor()
        
        # MIME type mapping
        self.mime_type_mapping = {
            'text': ['text/plain', 'text/markdown', 'text/html'],
            'pdf': ['application/pdf'],
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'],
            'video': ['video/mp4', 'video/avi', 'video/mov', 'video/wmv']
        }
    
    def load_document(self, file_path: Union[str, Path]) -> Document:
        """Load a document from file path."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        doc_type = self._get_document_type(mime_type, file_path.suffix)
        
        logger.info(f"Loading document: {file_path}, type: {doc_type}")
        
        try:
            if doc_type == 'text' or doc_type == 'pdf':
                content, metadata = self.text_extractor.extract(file_path)
            elif doc_type == 'image':
                content, metadata = self.image_extractor.extract(file_path)
            elif doc_type == 'audio':
                content, metadata = self.audio_extractor.extract(file_path)
            elif doc_type == 'video':
                content, metadata = self.video_extractor.extract(file_path)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            # Add common metadata
            metadata.update({
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'mime_type': mime_type,
                'doc_type': doc_type
            })
            
            return Document(
                content=content,
                metadata=metadata,
                doc_type=doc_type,
                source=str(file_path)
            )
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def load_documents(self, directory: Union[str, Path]) -> List[Document]:
        """Load all documents from a directory."""
        directory = Path(directory)
        documents = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    document = self.load_document(file_path)
                    documents.append(document)
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {str(e)}")
                    continue
        
        return documents
    
    def _get_document_type(self, mime_type: Optional[str], file_suffix: str) -> str:
        """Determine document type from MIME type and file extension."""
        if mime_type:
            for doc_type, mime_types in self.mime_type_mapping.items():
                if mime_type in mime_types:
                    return doc_type
        
        # Fallback to file extension
        extension_mapping = {
            '.txt': 'text',
            '.md': 'text',
            '.html': 'text',
            '.pdf': 'pdf',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.ogg': 'audio',
            '.mp4': 'video',
            '.avi': 'video',
            '.mov': 'video'
        }
        
        return extension_mapping.get(file_suffix.lower(), 'text')

