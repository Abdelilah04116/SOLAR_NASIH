import logging
from typing import List, Dict, Any, Union
import numpy as np
from .text_embeddings import TextEmbeddings
from .image_embeddings import ImageEmbeddings
from .audio_embeddings import AudioEmbeddings

logger = logging.getLogger(__name__)

class MultimodalEmbeddings:
    """Unified embedding generation for all modalities."""
    
    def __init__(self, 
                 text_model: str = "all-MiniLM-L6-v2",
                 image_model: str = "ViT-B/32"):
        
        self.text_embedder = TextEmbeddings(text_model)
        self.image_embedder = ImageEmbeddings(image_model)
        self.audio_embedder = AudioEmbeddings(text_model)
        
        # Store embedding dimensions
        self.text_dim = self.text_embedder.get_embedding_dim()
        self.image_dim = self.image_embedder.get_embedding_dim()
        self.audio_dim = self.audio_embedder.get_embedding_dim()
        
        logger.info("Multimodal embeddings initialized")
    
    def embed_chunk(self, chunk: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Generate embeddings for a multimodal chunk."""
        try:
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            doc_type = metadata.get('doc_type', 'text')
            
            embeddings = {}
            
            # Always generate text embedding from content
            if content:
                text_embedding = self.text_embedder.embed_text(content)
                embeddings['text'] = text_embedding
            
            # Generate modality-specific embeddings
            if doc_type == 'image':
                # For images, use the description for text embedding
                # Could also embed the actual image if available
                if 'clip_features' in metadata:
                    # Use pre-computed CLIP features
                    clip_features = np.array(metadata['clip_features'])
                    embeddings['image'] = clip_features.reshape(1, -1)
                elif 'file_path' in metadata:
                    # Generate image embedding from file
                    try:
                        img_embedding = self.image_embedder.embed_image(metadata['file_path'])
                        embeddings['image'] = img_embedding
                    except Exception as e:
                        logger.warning(f"Image embedding failed: {str(e)}")
            
            elif doc_type == 'audio':
                # For audio, embed the transcription
                if 'transcription' in metadata:
                    audio_text_embedding = self.audio_embedder.embed_audio_transcription(
                        metadata['transcription']
                    )
                    embeddings['audio_text'] = audio_text_embedding
                
                # Also embed audio features if available
                audio_features = {k: v for k, v in metadata.items() 
                                if k in ['duration', 'tempo', 'spectral_centroid_mean', 
                                        'zero_crossing_rate_mean', 'rms_energy']}
                if audio_features:
                    audio_feat_embedding = self.audio_embedder.embed_audio_features(audio_features)
                    embeddings['audio_features'] = audio_feat_embedding
            
            elif doc_type == 'video':
                # For video, embed transcription and frame descriptions
                if 'audio' in metadata and 'transcription' in metadata['audio']:
                    video_text_embedding = self.text_embedder.embed_text(
                        metadata['audio']['transcription']
                    )
                    embeddings['video_audio'] = video_text_embedding
                
                # Embed frame descriptions
                if 'descriptions' in metadata:
                    frame_descriptions = ' '.join(metadata['descriptions'])
                    frame_embedding = self.text_embedder.embed_text(frame_descriptions)
                    embeddings['video_frames'] = frame_embedding
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Multimodal embedding generation failed: {str(e)}")
            raise
    
    def get_primary_embedding(self, embeddings: Dict[str, np.ndarray], doc_type: str) -> np.ndarray:
        """Get the primary embedding for a document type."""
        if doc_type == 'image' and 'image' in embeddings:
            return embeddings['image']
        elif doc_type == 'audio' and 'audio_text' in embeddings:
            return embeddings['audio_text']
        elif doc_type == 'video' and 'video_audio' in embeddings:
            return embeddings['video_audio']
        else:
            return embeddings.get('text', np.array([]))

