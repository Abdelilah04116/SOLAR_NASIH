import logging
from typing import List, Dict, Any
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class ImageChunker:
    """Split images into patches or regions."""
    
    def __init__(self, patch_size: int = 224, max_patches: int = 16):
        self.patch_size = patch_size
        self.max_patches = max_patches
    
    def chunk_image(self, image_path: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split image into patches."""
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Calculate optimal grid
            width, height = image.size
            patches_x = min(width // self.patch_size, int(np.sqrt(self.max_patches)))
            patches_y = min(height // self.patch_size, int(np.sqrt(self.max_patches)))
            
            if patches_x == 0 or patches_y == 0:
                # Image too small, return as single chunk
                return [{
                    'content': f"Full image: {image_path}",
                    'metadata': {
                        **metadata,
                        'chunk_id': 0,
                        'chunk_type': 'image_full',
                        'patch_coordinates': (0, 0, width, height)
                    }
                }]
            
            chunk_objects = []
            chunk_id = 0
            
            for i in range(patches_x):
                for j in range(patches_y):
                    # Calculate patch coordinates
                    x1 = i * (width // patches_x)
                    y1 = j * (height // patches_y)
                    x2 = min((i + 1) * (width // patches_x), width)
                    y2 = min((j + 1) * (height // patches_y), height)
                    
                    # Extract patch
                    patch = image.crop((x1, y1, x2, y2))
                    
                    chunk_metadata = {
                        **metadata,
                        'chunk_id': chunk_id,
                        'chunk_type': 'image_patch',
                        'patch_coordinates': (x1, y1, x2, y2),
                        'patch_size': (x2-x1, y2-y1),
                        'grid_position': (i, j),
                        'total_patches': patches_x * patches_y
                    }
                    
                    chunk_objects.append({
                        'content': f"Image patch ({i},{j}) from {image_path}",
                        'metadata': chunk_metadata,
                        'patch_image': patch
                    })
                    
                    chunk_id += 1
            
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Image chunking failed: {str(e)}")
            raise