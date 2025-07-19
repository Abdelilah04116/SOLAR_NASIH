import logging
from pathlib import Path
from typing import Dict, Tuple, Any
import torch
from PIL import Image
import clip
import requests
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)

class ImageExtractor:
    """Extract descriptions and features from images."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        # Initialize CLIP model
        try:
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            logger.info("CLIP model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load CLIP model: {str(e)}")
            self.clip_model = None
        
        # Initialize BLIP model for image captioning
        try:
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
            logger.info("BLIP model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load BLIP model: {str(e)}")
            self.blip_model = None
    
    def extract(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract description and metadata from image."""
        try:
            # Load and process image
            image = Image.open(file_path).convert('RGB')
            
            # Generate caption using BLIP
            caption = self._generate_caption(image)
            
            # Extract visual features using CLIP
            features = self._extract_features(image)
            
            # Get basic image metadata
            image_metadata = self._get_image_metadata(image, file_path)
            
            metadata = {
                'extractor': 'image',
                'caption': caption,
                'features': features,
                **image_metadata
            }
            
            # Use caption as main content
            content = caption if caption else f"Image: {file_path.name}"
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error extracting image {file_path}: {str(e)}")
            raise
    
    def _generate_caption(self, image: Image.Image) -> str:
        """Generate caption for image using BLIP."""
        if self.blip_model is None:
            return "Image caption generation not available"
        
        try:
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            out = self.blip_model.generate(**inputs, max_length=50)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
            
        except Exception as e:
            logger.warning(f"Caption generation failed: {str(e)}")
            return "Caption generation failed"
    
    def _extract_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract visual features using CLIP."""
        if self.clip_model is None:
            return {}
        
        try:
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            return {
                'clip_features': image_features.cpu().numpy().tolist(),
                'feature_dimension': image_features.shape[-1]
            }
            
        except Exception as e:
            logger.warning(f"Feature extraction failed: {str(e)}")
            return {}
    
    def _get_image_metadata(self, image: Image.Image, file_path: Path) -> Dict[str, Any]:
        """Get basic image metadata."""
        return {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'file_size': file_path.stat().st_size
        }