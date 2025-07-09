"""
Parsers pour différents types de documents
"""
import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pathlib import Path
import hashlib
import io
import base64

# Imports pour le parsing PDF
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image

from models import ParsedContent, ChunkType, Document, ProcessingStatus
from config import ParsingConfig

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    """Interface abstraite pour les parsers de documents"""
    
    def __init__(self, config: ParsingConfig):
        self.config = config
        self.supported_formats = config.supported_formats
    
    @abstractmethod
    def parse(self, file_path: str) -> Document:
        """Parse un document et retourne un objet Document"""
        pass
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash d'un fichier"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _is_supported_format(self, file_path: str) -> bool:
        """Vérifie si le format de fichier est supporté"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats

class PDFParser(BaseParser):
    """Parser pour les documents PDF avec extraction de texte, tableaux et images"""
    
    def __init__(self, config: ParsingConfig):
        super().__init__(config)
        self.supported_formats = ['.pdf']
    
    def parse(self, file_path: str) -> Document:
        """Parse un PDF et extrait texte, tableaux et images"""
        if not self._is_supported_format(file_path):
            raise ValueError(f"Format de fichier non supporté: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # Création du document
        document = Document(
            file_path=file_path,
            file_name=Path(file_path).name,
            file_hash=self._calculate_file_hash(file_path),
            processing_status=ProcessingStatus.PROCESSING
        )
        
        try:
            doc = fitz.open(file_path)
            document.total_pages = len(doc)
            
            logger.info(f"Parsing PDF: {file_path} ({document.total_pages} pages)")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extraction du texte
                if self.config.extract_text:
                    text_content = self._extract_text(page, page_num)
                    document.parsed_content.extend(text_content)
                
                # Extraction des tableaux
                if self.config.extract_tables:
                    table_content = self._extract_tables(page, page_num)
                    document.parsed_content.extend(table_content)
                
                # Extraction des images
                if self.config.extract_images:
                    image_content = self._extract_images(page, page_num)
                    document.parsed_content.extend(image_content)
            
            doc.close()
            document.update_status(ProcessingStatus.COMPLETED)
            
            # Ajout des métadonnées du document
            document.metadata.update({
                "parser": "PDFParser",
                "total_pages": document.total_pages,
                "content_types": self._get_content_types_stats(document.parsed_content)
            })
            
            logger.info(f"Parsing terminé: {len(document.parsed_content)} éléments extraits")
            
        except Exception as e:
            document.update_status(ProcessingStatus.FAILED)
            logger.error(f"Erreur lors du parsing: {e}")
            raise
        
        return document
    
    def _extract_text(self, page, page_num: int) -> List[ParsedContent]:
        """Extrait le texte d'une page"""
        text_content = []
        
        try:
            # Extraction du texte avec informations de position
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:  # Bloc de texte
                    block_text = ""
                    block_bbox = block.get("bbox", [0, 0, 0, 0])
                    
                    for line in block["lines"]:
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        block_text += line_text + "\n"
                    
                    if block_text.strip():
                        text_content.append(ParsedContent(
                            content=block_text.strip(),
                            content_type=ChunkType.TEXT,
                            page_number=page_num + 1,
                            bbox=block_bbox,
                            metadata={
                                "extraction_method": "pymupdf_text_dict",
                                "char_count": len(block_text),
                                "font_info": self._extract_font_info(block)
                            }
                        ))
            
            # Fallback: extraction de texte simple si aucun bloc trouvé
            if not text_content:
                simple_text = page.get_text()
                if simple_text.strip():
                    text_content.append(ParsedContent(
                        content=simple_text.strip(),
                        content_type=ChunkType.TEXT,
                        page_number=page_num + 1,
                        metadata={
                            "extraction_method": "pymupdf_text_simple",
                            "char_count": len(simple_text)
                        }
                    ))
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction de texte page {page_num + 1}: {e}")
        
        return text_content
    
    def _extract_font_info(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les informations de police d'un bloc"""
        font_info = {"fonts": []}
        
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_info["fonts"].append({
                    "font": span.get("font", "unknown"),
                    "size": span.get("size", 0),
                    "flags": span.get("flags", 0)
                })
        
        return font_info
    
    def _extract_tables(self, page, page_num: int) -> List[ParsedContent]:
        """Extrait les tableaux d'une page"""
        tables = []
        
        try:
            # Recherche de structures tabulaires
            table_data = page.find_tables()
            
            for i, table in enumerate(table_data):
                df = table.to_pandas()
                
                if not df.empty and len(df) > 1:  # Au moins 2 lignes
                    # Nettoyage du DataFrame
                    df = df.dropna(how='all')  # Supprimer les lignes vides
                    
                    # Conversion en différents formats
                    table_text = df.to_string(index=False)
                    table_json = df.to_json(orient='records')
                    table_csv = df.to_csv(index=False)
                    
                    # Extraction de la bbox du tableau
                    table_bbox = table.bbox
                    
                    tables.append(ParsedContent(
                        content=table_text,
                        content_type=ChunkType.TABLE,
                        page_number=page_num + 1,
                        bbox=table_bbox,
                        metadata={
                            "extraction_method": "pymupdf_table",
                            "table_id": f"table_{page_num}_{i}",
                            "rows": len(df),
                            "columns": len(df.columns),
                            "column_names": df.columns.tolist(),
                            "json_data": table_json,
                            "csv_data": table_csv,
                            "confidence": getattr(table, 'confidence', 1.0)
                        }
                    ))
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des tableaux page {page_num + 1}: {e}")
        
        return tables
    
    def _extract_images(self, page, page_num: int) -> List[ParsedContent]:
        """Extrait les images d'une page"""
        images = []
        
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    # Vérifier si l'image est dans un format supporté
                    if pix.n - pix.alpha < 4:  # GRAY ou RGB
                        # Conversion en PNG
                        img_data = pix.tobytes("png")
                        
                        # Génération d'une description de l'image
                        description = self._generate_image_description(
                            img_data, img_index, page_num
                        )
                        
                        # Obtenir la position de l'image sur la page
                        img_bbox = self._get_image_bbox(page, xref)
                        
                        images.append(ParsedContent(
                            content=description,
                            content_type=ChunkType.IMAGE,
                            page_number=page_num + 1,
                            bbox=img_bbox,
                            metadata={
                                "extraction_method": "pymupdf_image",
                                "image_id": f"image_{page_num}_{img_index}",
                                "image_data": base64.b64encode(img_data).decode(),
                                "width": pix.width,
                                "height": pix.height,
                                "format": self.config.image_format,
                                "colorspace": pix.colorspace.name if pix.colorspace else "unknown",
                                "xref": xref
                            }
                        ))
                    
                    pix = None
                
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction d'image {img_index} page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction d'images page {page_num + 1}: {e}")
        
        return images
    
    def _generate_image_description(self, img_data: bytes, img_index: int, page_num: int) -> str:
        """Génère une description basique de l'image"""
        try:
            img = Image.open(io.BytesIO(img_data))
            
            # Analyse basique de l'image
            mode = img.mode
            size = img.size
            format_name = img.format or "PNG"
            
            # Calcul du ratio d'aspect
            aspect_ratio = round(size[0] / size[1], 2) if size[1] > 0 else 1.0
            
            # Classification basique selon la taille et le ratio
            if size[0] > 1000 or size[1] > 1000:
                image_type = "haute résolution"
            elif aspect_ratio > 2.0:
                image_type = "panoramique"
            elif 0.8 <= aspect_ratio <= 1.2:
                image_type = "carrée"
            else:
                image_type = "rectangulaire"
            
            description = (
                f"Image {img_index + 1} de la page {page_num + 1}: "
                f"Image {image_type} au format {format_name} "
                f"de taille {size[0]}x{size[1]} pixels en mode {mode}"
            )
            
            return description
            
        except Exception as e:
            logger.warning(f"Erreur lors de la génération de description d'image: {e}")
            return f"Image {img_index + 1} de la page {page_num + 1}: Données d'image"
    
    def _get_image_bbox(self, page, xref: int) -> Optional[List[float]]:
        """Obtient la bounding box d'une image sur la page"""
        try:
            # Recherche de l'image dans les objets de la page
            for item in page.get_images():
                if item[0] == xref:
                    # Recherche dans les objets graphiques
                    for block in page.get_drawings():
                        if hasattr(block, 'rect'):
                            return list(block.rect)
            
            # Fallback: retourner None si position non trouvée
            return None
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction de la bbox d'image: {e}")
            return None
    
    def _get_content_types_stats(self, parsed_content: List[ParsedContent]) -> Dict[str, int]:
        """Calcule les statistiques par type de contenu"""
        stats = {}
        for content in parsed_content:
            content_type = content.content_type.value
            stats[content_type] = stats.get(content_type, 0) + 1
        return stats

class TextParser(BaseParser):
    """Parser pour les fichiers texte simples"""
    
    def __init__(self, config: ParsingConfig):
        super().__init__(config)
        self.supported_formats = ['.txt', '.md', '.rst']
    
    def parse(self, file_path: str) -> Document:
        """Parse un fichier texte"""
        if not self._is_supported_format(file_path):
            raise ValueError(f"Format de fichier non supporté: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        document = Document(
            file_path=file_path,
            file_name=Path(file_path).name,
            file_hash=self._calculate_file_hash(file_path),
            processing_status=ProcessingStatus.PROCESSING
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                document.parsed_content.append(ParsedContent(
                    content=content.strip(),
                    content_type=ChunkType.TEXT,
                    page_number=1,
                    metadata={
                        "extraction_method": "text_file",
                        "char_count": len(content),
                        "encoding": "utf-8",
                        "file_extension": Path(file_path).suffix
                    }
                ))
            
            document.total_pages = 1
            document.update_status(ProcessingStatus.COMPLETED)
            
            document.metadata.update({
                "parser": "TextParser",
                "total_pages": 1,
                "content_types": self._get_content_types_stats(document.parsed_content)
            })
            
        except Exception as e:
            document.update_status(ProcessingStatus.FAILED)
            logger.error(f"Erreur lors du parsing du fichier texte: {e}")
            raise
        
        return document
    
    def _get_content_types_stats(self, parsed_content: List[ParsedContent]) -> Dict[str, int]:
        """Calcule les statistiques par type de contenu"""
        stats = {}
        for content in parsed_content:
            content_type = content.content_type.value
            stats[content_type] = stats.get(content_type, 0) + 1
        return stats

class ParserFactory:
    """Factory pour créer des parsers selon le type de fichier"""
    
    def __init__(self, config: ParsingConfig):
        self.config = config
        self.parsers = {
            '.pdf': PDFParser,
            '.txt': TextParser,
            '.md': TextParser,
            '.rst': TextParser
        }
    
    def create_parser(self, file_path: str) -> BaseParser:
        """Crée un parser approprié pour le fichier"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.parsers:
            raise ValueError(f"Format de fichier non supporté: {file_extension}")
        
        parser_class = self.parsers[file_extension]
        return parser_class(self.config)
    
    def get_supported_formats(self) -> List[str]:
        """Retourne la liste des formats supportés"""
        return list(self.parsers.keys())
    
    def is_supported(self, file_path: str) -> bool:
        """Vérifie si le fichier est supporté"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.parsers

def parse_document(file_path: str, config: ParsingConfig) -> Document:
    """Fonction utilitaire pour parser un document"""
    factory = ParserFactory(config)
    parser = factory.create_parser(file_path)
    return parser.parse(file_path)