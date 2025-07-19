import logging
from pathlib import Path
from typing import Dict, Tuple, Any
import whisper
import librosa
import numpy as np

logger = logging.getLogger(__name__)

class AudioExtractor:
    """Extract transcription and features from audio files."""
    
    def __init__(self, model_size: str = "base"):
        self.supported_formats = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        
        try:
            self.whisper_model = whisper.load_model(model_size)
            logger.info(f"Whisper model '{model_size}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            self.whisper_model = None
    
    def extract(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract transcription and metadata from audio."""
        try:
            # Transcribe audio using Whisper
            transcription, whisper_metadata = self._transcribe_audio(file_path)
            
            # Extract audio features
            audio_features = self._extract_audio_features(file_path)
            
            metadata = {
                'extractor': 'audio',
                'transcription': transcription,
                **whisper_metadata,
                **audio_features
            }
            
            return transcription, metadata
            
        except Exception as e:
            logger.error(f"Error extracting audio {file_path}: {str(e)}")
            raise
    
    def _transcribe_audio(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Transcribe audio using Whisper."""
        if self.whisper_model is None:
            return "Audio transcription not available", {}
        
        try:
            result = self.whisper_model.transcribe(str(file_path))
            
            metadata = {
                'language': result.get('language', 'unknown'),
                'segments': len(result.get('segments', [])),
                'duration': result.get('duration', 0),
                'confidence': np.mean([seg.get('confidence', 0) for seg in result.get('segments', [])]) if result.get('segments') else 0
            }
            
            return result['text'], metadata
            
        except Exception as e:
            logger.warning(f"Transcription failed: {str(e)}")
            return "Transcription failed", {}
    
    def _extract_audio_features(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic audio features."""
        try:
            # Load audio file
            y, sr = librosa.load(str(file_path))
            
            # Extract features
            duration = librosa.duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossings = librosa.feature.zero_crossing_rate(y)
            
            return {
                'duration': float(duration),
                'sample_rate': int(sr),
                'tempo': float(tempo),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'zero_crossing_rate_mean': float(np.mean(zero_crossings)),
                'rms_energy': float(np.mean(librosa.feature.rms(y=y)))
            }
            
        except Exception as e:
            logger.warning(f"Audio feature extraction failed: {str(e)}")
            return {}