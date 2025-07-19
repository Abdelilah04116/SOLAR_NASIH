import logging
from pathlib import Path
from typing import Dict, Tuple, Any, List
import cv2
import numpy as np
from .audio_extractor import AudioExtractor
from .image_extractor import ImageExtractor

logger = logging.getLogger(__name__)

class VideoExtractor:
    """Extract frames, audio transcription, and metadata from videos."""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.wmv', '.mkv']
        self.audio_extractor = AudioExtractor()
        self.image_extractor = ImageExtractor()
    
    def extract(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from video."""
        try:
            # Extract basic video metadata
            video_metadata = self._get_video_metadata(file_path)
            
            # Extract key frames
            frames_info = self._extract_key_frames(file_path)
            
            # Extract audio (if available)
            audio_content = ""
            audio_metadata = {}
            try:
                audio_content, audio_metadata = self._extract_audio_from_video(file_path)
            except Exception as e:
                logger.warning(f"Audio extraction failed: {str(e)}")
            
            # Combine frame descriptions and audio transcription
            content_parts = []
            
            if frames_info['descriptions']:
                content_parts.append("Video scenes: " + "; ".join(frames_info['descriptions']))
            
            if audio_content:
                content_parts.append("Audio transcription: " + audio_content)
            
            content = " | ".join(content_parts) if content_parts else f"Video: {file_path.name}"
            
            metadata = {
                'extractor': 'video',
                **video_metadata,
                **frames_info,
                'audio': audio_metadata
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error extracting video {file_path}: {str(e)}")
            raise
    
    def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic video metadata."""
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'file_size': file_path.stat().st_size
            }
            
        except Exception as e:
            logger.warning(f"Video metadata extraction failed: {str(e)}")
            return {}
    
    def _extract_key_frames(self, file_path: Path, max_frames: int = 10) -> Dict[str, Any]:
        """Extract and describe key frames from video."""
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                return {'frame_count': 0, 'descriptions': []}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame intervals
            if frame_count <= max_frames:
                frame_indices = list(range(0, frame_count, max(1, frame_count // max_frames)))
            else:
                frame_indices = list(range(0, frame_count, frame_count // max_frames))
            
            descriptions = []
            
            for frame_idx in frame_indices[:max_frames]:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert frame to PIL Image and extract description
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    from PIL import Image
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Use image extractor to get description
                    try:
                        description = self.image_extractor._generate_caption(pil_image)
                        if description:
                            descriptions.append(f"Frame {frame_idx}: {description}")
                    except Exception as e:
                        logger.warning(f"Frame description failed: {str(e)}")
            
            cap.release()
            
            return {
                'extracted_frames': len(descriptions),
                'descriptions': descriptions
            }
            
        except Exception as e:
            logger.warning(f"Key frame extraction failed: {str(e)}")
            return {'frame_count': 0, 'descriptions': []}
    
    def _extract_audio_from_video(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract audio track from video and transcribe it."""
        try:
            # Use ffmpeg to extract audio (requires ffmpeg installation)
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                # Extract audio using ffmpeg
                cmd = [
                    'ffmpeg', '-i', str(file_path), 
                    '-vn', '-acodec', 'pcm_s16le', 
                    '-ar', '16000', '-ac', '1', 
                    temp_audio.name, '-y'
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Transcribe extracted audio
                audio_content, audio_metadata = self.audio_extractor.extract(Path(temp_audio.name))
                
                # Clean up temporary file
                Path(temp_audio.name).unlink()
                
                return audio_content, audio_metadata
                
        except Exception as e:
            logger.warning(f"Video audio extraction failed: {str(e)}")
            return "", {}