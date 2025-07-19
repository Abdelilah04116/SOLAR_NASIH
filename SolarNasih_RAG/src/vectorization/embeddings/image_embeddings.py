import logging
from typing import List, Union, Dict, Any
import numpy as np
import torch
import clip
from PIL import Image

logger = logging.getLogger(__name__)

class ImageEmbeddings:
    """Image embedding generation using CLIP."""
    
    def __init__(self, model_name: str = "ViT-B/32"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.model, self.preprocess = clip.load(model_name, device=self.device)
            # Test to get embedding dimension
            dummy_image = torch.zeros(1, 3, 224, 224).to(self.device)
            with torch.no_grad():
                dummy_embedding = self.model.encode_image(dummy_image)
                self.embedding_dim = dummy_embedding.shape[-1]
            
            logger.info(f"Image embedding model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load image embedding model: {str(e)}")
            raise
    
    def embed_image(self, images: Union[str, List[str], Image.Image, List[Image.Image]]) -> np.ndarray:
        """Generate embeddings for image(s)."""
        try:
            # Normalize input to list of PIL Images
            if isinstance(images, str):
                images = [Image.open(images)]
            elif isinstance(images, Image.Image):
                images = [images]
            elif isinstance(images, list) and isinstance(images[0], str):
                images = [Image.open(img_path) for img_path in images]
            
            # Preprocess images
            image_tensors = []
            for img in images:
                if isinstance(img, str):
                    img = Image.open(img)
                image_tensor = self.preprocess(img).unsqueeze(0)
                image_tensors.append(image_tensor)
            
            image_batch = torch.cat(image_tensors).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                embeddings = self.model.encode_image(image_batch)
                embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
            
            return embeddings.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Image embedding generation failed: {str(e)}")
            raise
    
    def embed_text_for_image_search(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate text embeddings for image search (using CLIP text encoder)."""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            # Tokenize text
            text_tokens = clip.tokenize(texts).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                text_embeddings = self.model.encode_text(text_tokens)
                text_embeddings = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)
            
            return text_embeddings.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Text-for-image embedding generation failed: {str(e)}")
            raise
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim