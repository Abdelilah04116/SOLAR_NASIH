"""
Module d'embedding multimodal pour générer des vecteurs
"""
import logging
import base64
import io
from typing import List, Dict, Any, Optional, Union
import numpy as np

import torch
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

from models import Chunk, ChunkType
from config import EmbeddingConfig

logger = logging.getLogger(__name__)

class BaseEmbedder:
    """Interface de base pour les embedders"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.device = self._get_device()
        self.normalize_embeddings = config.normalize_embeddings
        self.batch_size = config.batch_size
    
    def _get_device(self) -> torch.device:
        """Détermine le device à utiliser"""
        if self.config.device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            return torch.device(self.config.device)

class TextEmbedder(BaseEmbedder):
    """Embedder pour le texte et les tableaux"""
    
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.model_name = config.text_model_name
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle d'embedding de texte"""
        try:
            logger.info(f"Chargement du modèle text embedding: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.model.to(self.device)
            logger.info(f"Modèle chargé sur {self.device}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle text: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Génère des embeddings pour une liste de textes"""
        if not texts:
            return np.array([])
        
        try:
            # Traitement par batch
            embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                
                with torch.no_grad():
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        convert_to_numpy=True,
                        normalize_embeddings=self.normalize_embeddings
                    )
                
                embeddings.append(batch_embeddings)
            
            # Concaténation des résultats
            all_embeddings = np.vstack(embeddings)
            
            return all_embeddings.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding de texte: {e}")
            raise
    
    def embed_single_text(self, text: str) -> np.ndarray:
        """Génère un embedding pour un seul texte"""
        embeddings = self.embed_texts([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])

class ImageEmbedder(BaseEmbedder):
    """Embedder pour les images avec CLIP"""
    
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.model_name = config.image_model_name
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle CLIP pour les images"""
        try:
            logger.info(f"Chargement du modèle image embedding: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.to(self.device)
            logger.info(f"Modèle CLIP chargé sur {self.device}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle CLIP: {e}")
            raise
    
    def embed_images(self, images: List[Image.Image]) -> np.ndarray:
        """Génère des embeddings pour une liste d'images"""
        if not images:
            return np.array([])
        
        try:
            embeddings = []
            
            for i in range(0, len(images), self.batch_size):
                batch_images = images[i:i + self.batch_size]
                
                # Préparation des inputs
                inputs = self.processor(
                    images=batch_images,
                    return_tensors="pt",
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    
                    if self.normalize_embeddings:
                        image_features = torch.nn.functional.normalize(image_features, p=2, dim=1)
                
                batch_embeddings = image_features.cpu().numpy()
                embeddings.append(batch_embeddings)
            
            all_embeddings = np.vstack(embeddings)
            return all_embeddings.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding d'image: {e}")
            raise
    
    def embed_single_image(self, image: Image.Image) -> np.ndarray:
        """Génère un embedding pour une seule image"""
        embeddings = self.embed_images([image])
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    def embed_image_from_base64(self, base64_data: str) -> np.ndarray:
        """Génère un embedding à partir de données image base64"""
        try:
            # Décoder l'image
            img_bytes = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(img_bytes))
            
            # Convertir en RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return self.embed_single_image(image)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding d'image depuis base64: {e}")
            return np.array([])

class MultimodalEmbedder:
    """Embedder principal qui gère tous les types de contenu"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.text_embedder = TextEmbedder(config)
        self.image_embedder = ImageEmbedder(config)
        
        # Dimensions des embeddings
        self.text_dim = self._get_text_embedding_dim()
        self.image_dim = self._get_image_embedding_dim()
        
        logger.info(f"Embedder initialisé - Text dim: {self.text_dim}, Image dim: {self.image_dim}")
    
    def _get_text_embedding_dim(self) -> int:
        """Obtient la dimension des embeddings de texte"""
        try:
            test_embedding = self.text_embedder.embed_single_text("test")
            return len(test_embedding)
        except Exception:
            return 384  # Dimension par défaut pour MiniLM
    
    def _get_image_embedding_dim(self) -> int:
        """Obtient la dimension des embeddings d'image"""
        try:
            # Créer une image de test
            test_image = Image.new('RGB', (224, 224), color='white')
            test_embedding = self.image_embedder.embed_single_image(test_image)
            return len(test_embedding)
        except Exception:
            return 512  # Dimension par défaut pour CLIP
    
    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Génère des embeddings pour tous les chunks"""
        updated_chunks = []
        
        # Séparer les chunks par type pour un traitement par batch efficace
        text_chunks = []
        table_chunks = []
        image_chunks = []
        
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.TEXT:
                text_chunks.append(chunk)
            elif chunk.chunk_type == ChunkType.TABLE:
                table_chunks.append(chunk)
            elif chunk.chunk_type == ChunkType.IMAGE:
                image_chunks.append(chunk)
        
        # Traitement par batch pour chaque type
        if text_chunks:
            self._embed_text_chunks(text_chunks)
            updated_chunks.extend(text_chunks)
        
        if table_chunks:
            self._embed_table_chunks(table_chunks)
            updated_chunks.extend(table_chunks)
        
        if image_chunks:
            self._embed_image_chunks(image_chunks)
            updated_chunks.extend(image_chunks)
        
        logger.info(f"Embeddings générés pour {len(updated_chunks)} chunks")
        return updated_chunks
    
    def _embed_text_chunks(self, chunks: List[Chunk]):
        """Traite les chunks de texte par batch"""
        texts = []
        
        for chunk in chunks:
            # Combiner le contenu avec les questions hypothétiques
            combined_text = chunk.content
            
            if chunk.hypothetical_questions:
                questions_text = " ".join(chunk.hypothetical_questions)
                combined_text = f"{chunk.content} {questions_text}"
            
            texts.append(combined_text)
        
        # Génération des embeddings par batch
        try:
            embeddings = self.text_embedder.embed_texts(texts)
            
            for i, chunk in enumerate(chunks):
                chunk.embedding = embeddings[i]
                
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding des chunks de texte: {e}")
            # Fallback: embedding individuel
            for chunk in chunks:
                try:
                    chunk.embedding = self.text_embedder.embed_single_text(chunk.content)
                except Exception as e2:
                    logger.warning(f"Échec de l'embedding pour chunk {chunk.id}: {e2}")
                    chunk.embedding = np.zeros(self.text_dim, dtype=np.float32)
    
    def _embed_table_chunks(self, chunks: List[Chunk]):
        """Traite les chunks de tableau (similaire au texte mais avec preprocessing)"""
        texts = []
        
        for chunk in chunks:
            # Préparation spéciale pour les tableaux
            table_text = self._preprocess_table_content(chunk)
            
            if chunk.hypothetical_questions:
                questions_text = " ".join(chunk.hypothetical_questions)
                table_text = f"{table_text} {questions_text}"
            
            texts.append(table_text)
        
        try:
            embeddings = self.text_embedder.embed_texts(texts)
            
            for i, chunk in enumerate(chunks):
                chunk.embedding = embeddings[i]
                
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding des chunks de tableau: {e}")
            for chunk in chunks:
                try:
                    chunk.embedding = self.text_embedder.embed_single_text(chunk.content)
                except Exception as e2:
                    logger.warning(f"Échec de l'embedding pour chunk table {chunk.id}: {e2}")
                    chunk.embedding = np.zeros(self.text_dim, dtype=np.float32)
    
    def _embed_image_chunks(self, chunks: List[Chunk]):
        """Traite les chunks d'image"""
        for chunk in chunks:
            try:
                # Essayer d'abord l'embedding visuel
                image_data = chunk.metadata.get('image_data')
                
                if image_data:
                    embedding = self.image_embedder.embed_image_from_base64(image_data)
                    
                    if len(embedding) > 0:
                        chunk.embedding = embedding
                    else:
                        # Fallback sur l'embedding textuel de la description
                        self._fallback_text_embedding(chunk)
                else:
                    # Pas de données d'image, utiliser la description
                    self._fallback_text_embedding(chunk)
                    
            except Exception as e:
                logger.warning(f"Erreur lors de l'embedding d'image {chunk.id}: {e}")
                self._fallback_text_embedding(chunk)
    
    def _fallback_text_embedding(self, chunk: Chunk):
        """Génère un embedding textuel de fallback pour les images"""
        try:
            # Combiner description et questions
            combined_text = chunk.content
            if chunk.hypothetical_questions:
                questions_text = " ".join(chunk.hypothetical_questions)
                combined_text = f"{chunk.content} {questions_text}"
            
            chunk.embedding = self.text_embedder.embed_single_text(combined_text)
            
        except Exception as e:
            logger.warning(f"Échec du fallback text embedding pour {chunk.id}: {e}")
            chunk.embedding = np.zeros(self.text_dim, dtype=np.float32)
    
    def _preprocess_table_content(self, chunk: Chunk) -> str:
        """Préprocess le contenu d'un tableau pour l'embedding"""
        content = chunk.content
        
        # Ajouter des informations contextuelles sur le tableau
        context_parts = [content]
        
        # Ajouter des métadonnées utiles
        if 'rows' in chunk.metadata:
            context_parts.append(f"Ce tableau contient {chunk.metadata['rows']} lignes")
        
        if 'columns' in chunk.metadata:
            context_parts.append(f"et {chunk.metadata['columns']} colonnes")
        
        if 'column_names' in chunk.metadata:
            cols = chunk.metadata['column_names']
            context_parts.append(f"Les colonnes sont: {', '.join(cols)}")
        
        return ". ".join(context_parts)
    
    def embed_query(self, query: str, query_type: str = "text") -> np.ndarray:
        """Génère un embedding pour une requête"""
        if query_type == "text":
            return self.text_embedder.embed_single_text(query)
        elif query_type == "image" and hasattr(self, 'image_embedder'):
            # Pour les requêtes d'image, on s'attendrait à recevoir une image
            # Ici on traite comme du texte par défaut
            return self.text_embedder.embed_single_text(query)
        else:
            return self.text_embedder.embed_single_text(query)
    
    def get_embedding_dimensions(self) -> Dict[str, int]:
        """Retourne les dimensions des différents types d'embeddings"""
        return {
            "text": self.text_dim,
            "image": self.image_dim
        }

def create_embedder(config: EmbeddingConfig) -> MultimodalEmbedder:
    """Factory function pour créer un embedder"""
    return MultimodalEmbedder(config)