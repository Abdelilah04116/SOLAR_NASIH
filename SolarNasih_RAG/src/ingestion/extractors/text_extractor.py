import logging
from pathlib import Path
from typing import Dict, Tuple, Any
import PyPDF2
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class TextExtractor:
    """Extract text from various text-based documents."""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.html', '.pdf']
    
    def extract(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract text content from file."""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.txt', '.md', '.html']:
            return self._extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported text format: {file_extension}")
    
    def _extract_from_text(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            metadata = {
                'extractor': 'text',
                'character_count': len(content),
                'line_count': content.count('\n') + 1,
                'word_count': len(content.split())
            }
            
            return content, metadata
            
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    
                    metadata = {
                        'extractor': 'text',
                        'encoding': encoding,
                        'character_count': len(content),
                        'line_count': content.count('\n') + 1,
                        'word_count': len(content.split())
                    }
                    
                    return content, metadata
                except UnicodeDecodeError:
                    continue
            
            raise UnicodeDecodeError("Unable to decode file with supported encodings")
    
    def _extract_from_pdf(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF files."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                        continue
                
                metadata = {
                    'extractor': 'pdf',
                    'page_count': len(pdf_reader.pages),
                    'character_count': len(content),
                    'word_count': len(content.split())
                }
                
                # Try OCR if no text was extracted
                if not content.strip():
                    logger.info("No text found in PDF, attempting OCR...")
                    content, ocr_metadata = self._extract_pdf_with_ocr(file_path)
                    metadata.update(ocr_metadata)
                
                return content, metadata
                
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    def _extract_pdf_with_ocr(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF using OCR."""
        try:
            # Convert PDF to images and apply OCR
            from pdf2image import convert_from_path
            
            images = convert_from_path(file_path)
            content = ""
            
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image)
                    content += page_text + "\n"
                except Exception as e:
                    logger.warning(f"OCR failed for page {i}: {str(e)}")
                    continue
            
            metadata = {
                'extractor': 'pdf_ocr',
                'ocr_pages': len(images),
                'character_count': len(content),
                'word_count': len(content.split())
            }
            
            return content, metadata
            
        except ImportError:
            logger.error("pdf2image not installed, cannot perform OCR on PDF")
            raise
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise