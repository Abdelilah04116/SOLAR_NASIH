import logging
from typing import List, Union, Dict, Any
import numpy as np
from .text_embeddings import TextEmbeddings

logger = logging.getLogger(__name__)

class AudioEmbeddings:
    """Audio embedding generation (via transcription embeddings)."""
    
    def __init__(self, text_model_name: str = "all-MiniLM-L6-v2"):
        # For now, we embed audio via its transcription
        # In future, could add specialized audio embedding models
        self.text_embedder = TextEmbeddings(text_model_name)
        self.embedding_dim = self.text_embedder.get_embedding_dim()
        
        logger.info("Audio embedding initialized (using text embeddings of transcriptions)")
    
    def embed_audio_transcription(self, transcriptions: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for audio transcriptions."""
        try:
            return self.text_embedder.embed_text(transcriptions)
        except Exception as e:
            logger.error(f"Audio transcription embedding failed: {str(e)}")
            raise
    
    def embed_audio_features(self, audio_features: Dict[str, Any]) -> np.ndarray:
        """Generate embeddings from audio features (temporal, spectral, etc.)."""
        try:
            # Create a feature vector from audio characteristics
            feature_list = []
            
            # Add available features
            if 'duration' in audio_features:
                feature_list.append(audio_features['duration'])
            if 'tempo' in audio_features:
                feature_list.append(audio_features['tempo'])
            if 'spectral_centroid_mean' in audio_features:
                feature_list.append(audio_features['spectral_centroid_mean'])
            if 'zero_crossing_rate_mean' in audio_features:
                feature_list.append(audio_features['zero_crossing_rate_mean'])
            if 'rms_energy' in audio_features:
                feature_list.append(audio_features['rms_energy'])
            
            # Pad or truncate to fixed size
            target_size = 128
            if len(feature_list) < target_size:
                feature_list.extend([0.0] * (target_size - len(feature_list)))
            else:
                feature_list = feature_list[:target_size]
            
            # Normalize features
            feature_array = np.array(feature_list, dtype=np.float32)
            feature_array = feature_array / (np.linalg.norm(feature_array) + 1e-8)
            
            return feature_array.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Audio feature embedding failed: {str(e)}")
            raise
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim