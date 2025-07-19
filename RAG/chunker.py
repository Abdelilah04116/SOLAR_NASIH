"""
Module de chunking pour diviser le contenu en chunks cohérents
"""
import logging
import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from models import Chunk, ChunkType, ParsedContent, Document
from config import ChunkingConfig

logger = logging.getLogger(__name__)

class BaseChunker(ABC):
    """Interface abstraite pour les chunkers"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    @abstractmethod
    def chunk_content(self, parsed_content: List[ParsedContent]) -> List[Chunk]:
        """Découpe le contenu parsé en chunks"""
        pass

class TextChunker:
    """Chunker spécialisé pour le texte"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.chunk_size = config.text_chunk_size
        self.chunk_overlap = config.text_chunk_overlap
        self.prefer_sentence_boundaries = config.prefer_sentence_boundaries
        self.min_chunk_size = config.min_chunk_size
    
    def chunk_text(self, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Découpe le texte en chunks avec chevauchement intelligent"""
        text = content.content
        chunks = []
        
        if len(text) <= self.chunk_size:
            # Texte assez court pour être un seul chunk
            chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TEXT, content.page_number) if chunker_manager else f"text_{content.page_number}_0"
            chunk = Chunk(
                id=chunk_id,
                content=text,
                chunk_type=ChunkType.TEXT,
                page_number=content.page_number,
                start_char=0,
                end_char=len(text),
                metadata={
                    **content.metadata,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "chunking_method": "single_chunk"
                }
            )
            chunks.append(chunk)
            return chunks
        
        # Découpage avec chevauchement
        if self.prefer_sentence_boundaries:
            chunks = self._chunk_by_sentences(text, content, chunker_manager)
        else:
            chunks = self._chunk_by_characters(text, content, chunker_manager)
        
        return chunks
    
    def _chunk_by_sentences(self, text: str, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Découpe le texte en respectant les limites de phrases"""
        # Découpage en phrases
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            
            # Vérifier si ajouter cette phrase dépasse la taille limite
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Créer un chunk avec le contenu actuel
                chunk_end = current_start + len(current_chunk)
                
                if len(current_chunk.strip()) >= self.min_chunk_size:
                    chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TEXT, content.page_number) if chunker_manager else f"text_{content.page_number}_{chunk_index}"
                    chunk = Chunk(
                        id=chunk_id,
                        content=current_chunk.strip(),
                        chunk_type=ChunkType.TEXT,
                        page_number=content.page_number,
                        start_char=current_start,
                        end_char=chunk_end,
                        metadata={
                            **content.metadata,
                            "chunk_index": chunk_index,
                            "chunking_method": "sentence_boundary",
                            "sentence_count": len(self._split_into_sentences(current_chunk))
                        }
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Préparer le chunk suivant avec chevauchement
                overlap_text = self._get_overlap_text(current_chunk)
                current_start = chunk_end - len(overlap_text)
                current_chunk = overlap_text
            
            current_chunk += sentence + " "
            i += 1
        
        # Ajouter le dernier chunk
        if current_chunk.strip() and len(current_chunk.strip()) >= self.min_chunk_size:
            chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TEXT, content.page_number) if chunker_manager else f"text_{content.page_number}_{chunk_index}"
            chunk = Chunk(
                id=chunk_id,
                content=current_chunk.strip(),
                chunk_type=ChunkType.TEXT,
                page_number=content.page_number,
                start_char=current_start,
                end_char=current_start + len(current_chunk),
                metadata={
                    **content.metadata,
                    "chunk_index": chunk_index,
                    "chunking_method": "sentence_boundary",
                    "sentence_count": len(self._split_into_sentences(current_chunk))
                }
            )
            chunks.append(chunk)
        
        # Mettre à jour le total de chunks dans les métadonnées
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def _chunk_by_characters(self, text: str, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Découpe le texte par nombre de caractères"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Essayer de couper à un endroit plus naturel
            if end < len(text) and self.prefer_sentence_boundaries:
                # Chercher la fin de phrase la plus proche
                last_sentence = chunk_text.rfind('.')
                last_exclamation = chunk_text.rfind('!')
                last_question = chunk_text.rfind('?')
                
                sentence_end = max(last_sentence, last_exclamation, last_question)
                
                if sentence_end > start + self.chunk_size // 2:
                    end = start + sentence_end + 1
                    chunk_text = text[start:end]
            
            if chunk_text.strip() and len(chunk_text.strip()) >= self.min_chunk_size:
                chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TEXT, content.page_number) if chunker_manager else f"text_{content.page_number}_{chunk_index}"
                chunk = Chunk(
                    id=chunk_id,
                    content=chunk_text.strip(),
                    chunk_type=ChunkType.TEXT,
                    page_number=content.page_number,
                    start_char=start,
                    end_char=end,
                    metadata={
                        **content.metadata,
                        "chunk_index": chunk_index,
                        "chunking_method": "character_boundary"
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        # Mettre à jour le total de chunks
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise le texte en phrases"""
        # Pattern pour détecter les fins de phrases
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Obtient le texte de chevauchement"""
        if len(text) <= self.chunk_overlap:
            return text
        
        overlap_text = text[-self.chunk_overlap:]
        
        # Essayer de commencer au début d'une phrase pour le chevauchement
        if self.prefer_sentence_boundaries:
            sentences = self._split_into_sentences(overlap_text)
            if len(sentences) > 1:
                # Prendre les dernières phrases complètes
                return ' '.join(sentences[-2:])
        
        return overlap_text

class TableChunker:
    """Chunker spécialisé pour les tableaux"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.max_chunk_size = config.table_chunk_size
    
    def chunk_table(self, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Traite les tableaux comme des chunks uniques ou les divise si nécessaire"""
        table_text = content.content
        
        # Si le tableau est petit, le traiter comme un chunk unique
        if len(table_text) <= self.max_chunk_size:
            chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TABLE, content.page_number) if chunker_manager else f"table_{content.page_number}_{content.metadata.get('table_id', '0')}"
            chunk = Chunk(
                id=chunk_id,
                content=table_text,
                chunk_type=ChunkType.TABLE,
                page_number=content.page_number,
                metadata={
                    **content.metadata,
                    "chunking_method": "single_table"
                }
            )
            return [chunk]
        
        # Pour les gros tableaux, essayer de les diviser par lignes
        return self._chunk_large_table(content, chunker_manager)
    
    def _chunk_large_table(self, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Divise un gros tableau en plusieurs chunks"""
        chunks = []
        
        try:
            # Essayer d'utiliser les données JSON si disponibles
            json_data = content.metadata.get('json_data')
            if json_data:
                import json
                rows = json.loads(json_data)
                return self._chunk_table_rows(rows, content, chunker_manager)
        except Exception as e:
            logger.warning(f"Erreur lors du chunking de tableau par JSON: {e}")
        
        # Fallback: découpage par lignes de texte
        lines = content.content.split('\n')
        header = lines[0] if lines else ""
        
        current_chunk_lines = [header]
        current_size = len(header)
        chunk_index = 0
        
        for line in lines[1:]:
            if current_size + len(line) > self.max_chunk_size and len(current_chunk_lines) > 1:
                # Créer un chunk
                chunk_content = '\n'.join(current_chunk_lines)
                chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TABLE, content.page_number) if chunker_manager else f"table_{content.page_number}_{chunk_index}"
                chunk = Chunk(
                    id=chunk_id,
                    content=chunk_content,
                    chunk_type=ChunkType.TABLE,
                    page_number=content.page_number,
                    metadata={
                        **content.metadata,
                        "chunk_index": chunk_index,
                        "chunking_method": "table_rows",
                        "row_count": len(current_chunk_lines) - 1  # -1 pour l'en-tête
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Nouveau chunk avec en-tête
                current_chunk_lines = [header, line]
                current_size = len(header) + len(line)
            else:
                current_chunk_lines.append(line)
                current_size += len(line)
        
        # Ajouter le dernier chunk
        if len(current_chunk_lines) > 1:
            chunk_content = '\n'.join(current_chunk_lines)
            chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TABLE, content.page_number) if chunker_manager else f"table_{content.page_number}_{chunk_index}"
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                chunk_type=ChunkType.TABLE,
                page_number=content.page_number,
                metadata={
                    **content.metadata,
                    "chunk_index": chunk_index,
                    "chunking_method": "table_rows",
                    "row_count": len(current_chunk_lines) - 1
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_table_rows(self, rows: List[Dict], content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Divise un tableau en chunks basés sur les lignes JSON"""
        chunks = []
        chunk_index = 0
        current_rows = []
        current_size = 0
        
        for row in rows:
            row_text = str(row)
            
            if current_size + len(row_text) > self.max_chunk_size and current_rows:
                # Créer un chunk
                chunk_content = self._format_rows_as_table(current_rows)
                chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TABLE, content.page_number) if chunker_manager else f"table_{content.page_number}_{chunk_index}"
                chunk = Chunk(
                    id=chunk_id,
                    content=chunk_content,
                    chunk_type=ChunkType.TABLE,
                    page_number=content.page_number,
                    metadata={
                        **content.metadata,
                        "chunk_index": chunk_index,
                        "chunking_method": "table_json_rows",
                        "row_count": len(current_rows)
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
                
                current_rows = [row]
                current_size = len(row_text)
            else:
                current_rows.append(row)
                current_size += len(row_text)
        
        # Ajouter le dernier chunk
        if current_rows:
            chunk_content = self._format_rows_as_table(current_rows)
            chunk_id = chunker_manager.get_next_chunk_id(ChunkType.TABLE, content.page_number) if chunker_manager else f"table_{content.page_number}_{chunk_index}"
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                chunk_type=ChunkType.TABLE,
                page_number=content.page_number,
                metadata={
                    **content.metadata,
                    "chunk_index": chunk_index,
                    "chunking_method": "table_json_rows",
                    "row_count": len(current_rows)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _format_rows_as_table(self, rows: List[Dict]) -> str:
        """Formate les lignes comme un tableau texte"""
        if not rows:
            return ""
        
        # Obtenir toutes les colonnes
        columns = set()
        for row in rows:
            columns.update(row.keys())
        columns = sorted(columns)
        
        # Créer le tableau
        lines = []
        
        # En-tête
        header = " | ".join(columns)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Lignes de données
        for row in rows:
            line = " | ".join(str(row.get(col, "")) for col in columns)
            lines.append(line)
        
        return "\n".join(lines)

class ImageChunker:
    """Chunker spécialisé pour les images"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    def chunk_image(self, content: ParsedContent, chunker_manager=None) -> List[Chunk]:
        """Traite les images comme des chunks uniques"""
        chunk_id = chunker_manager.get_next_chunk_id(ChunkType.IMAGE, content.page_number) if chunker_manager else f"image_{content.page_number}_{content.metadata.get('image_id', '0')}"
        # Copie le chemin de l'image dans le metadata du chunk si présent
        chunk_metadata = {
            **content.metadata,
            "chunking_method": "single_image"
        }
        if "image_path" in content.metadata:
            chunk_metadata["image_path"] = content.metadata["image_path"]
        chunk = Chunk(
            id=chunk_id,
            content=content.content,
            chunk_type=ChunkType.IMAGE,
            page_number=content.page_number,
            metadata=chunk_metadata
        )
        return [chunk]

class MultimodalChunker(BaseChunker):
    """Chunker principal qui gère tous les types de contenu"""
    
    def __init__(self, config: ChunkingConfig):
        super().__init__(config)
        self.text_chunker = TextChunker(config)
        self.table_chunker = TableChunker(config)
        self.image_chunker = ImageChunker(config)
        
        # Compteurs globaux pour garantir l'unicité des IDs
        self.global_chunk_counter = 0
        self.type_counters = {
            ChunkType.TEXT: 0,
            ChunkType.TABLE: 0,
            ChunkType.IMAGE: 0
        }
    
    def chunk_content(self, parsed_content: List[ParsedContent]) -> List[Chunk]:
        """Découpe le contenu parsé en chunks selon le type"""
        all_chunks = []
        
        # Réinitialiser les compteurs pour ce document
        self.global_chunk_counter = 0
        self.type_counters = {
            ChunkType.TEXT: 0,
            ChunkType.TABLE: 0,
            ChunkType.IMAGE: 0
        }
        
        for content in parsed_content:
            try:
                if content.content_type == ChunkType.TEXT:
                    chunks = self.text_chunker.chunk_text(content, self)
                elif content.content_type == ChunkType.TABLE:
                    chunks = self.table_chunker.chunk_table(content, self)
                elif content.content_type == ChunkType.IMAGE:
                    chunks = self.image_chunker.chunk_image(content, self)
                else:
                    logger.warning(f"Type de contenu non supporté: {content.content_type}")
                    continue
                
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Erreur lors du chunking du contenu {content.content_type}: {e}")
                continue
        
        logger.info(f"Chunking terminé: {len(all_chunks)} chunks créés")
        return all_chunks
    
    def get_next_chunk_id(self, chunk_type: ChunkType, page_number: int) -> str:
        """Génère un ID unique pour un chunk"""
        type_counter = self.type_counters[chunk_type]
        self.type_counters[chunk_type] += 1
        self.global_chunk_counter += 1
        
        # Format: type_pageXX_globalXXX_typeXX
        chunk_id = f"{chunk_type.value}_page{page_number:02d}_global{self.global_chunk_counter:03d}_type{type_counter:03d}"
        return chunk_id
    
    def chunk_document(self, document: Document) -> Document:
        """Chunk un document complet et met à jour ses chunks"""
        chunks = self.chunk_content(document.parsed_content)
        
        for chunk in chunks:
            document.add_chunk(chunk)
        
        return document

def create_chunker(config: ChunkingConfig) -> MultimodalChunker:
    """Factory function pour créer un chunker"""
    return MultimodalChunker(config)