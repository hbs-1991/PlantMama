"""Image processing service."""

import io
import logging
import hashlib
from typing import Tuple, Optional
from pathlib import Path
from datetime import datetime

from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Service for processing plant images."""
    
    MAX_SIZE = (1024, 1024)  # Maximum image dimensions
    ALLOWED_FORMATS = {"JPEG", "PNG", "JPG", "WEBP"}
    
    @classmethod
    async def process_image(cls, image_data: bytes) -> Tuple[bytes, dict]:
        """
        Process and validate plant image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of processed image bytes and metadata
            
        Raises:
            ValueError: If image is invalid
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Validate format
            if image.format not in cls.ALLOWED_FORMATS:
                raise ValueError(f"Unsupported image format: {image.format}")
            
            # Get metadata
            metadata = {
                "original_format": image.format,
                "original_size": image.size,
                "mode": image.mode,
            }
            
            # Convert to RGB if necessary
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            
            # Resize if too large
            if image.size[0] > cls.MAX_SIZE[0] or image.size[1] > cls.MAX_SIZE[1]:
                image.thumbnail(cls.MAX_SIZE, Image.Resampling.LANCZOS)
                metadata["resized"] = True
                metadata["new_size"] = image.size
            
            # Save processed image
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=90, optimize=True)
            processed_data = output.getvalue()
            
            metadata["processed_size"] = len(processed_data)
            
            logger.info(f"Processed image: {metadata}")
            return processed_data, metadata
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @classmethod
    async def extract_plant_features(cls, image_data: bytes) -> dict:
        """
        Extract visual features from plant image.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary of extracted features
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to a numpy array
            img_array = np.array(image)
            
            # Basic feature extraction
            features = {
                "dominant_colors": cls._get_dominant_colors(img_array),
                "brightness": float(np.mean(img_array)),
                "contrast": float(np.std(img_array)),
                "green_ratio": cls._calculate_green_ratio(img_array),
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    @staticmethod
    def _get_dominant_colors(img_array: np.ndarray, n_colors: int = 3) -> list:
        """Get dominant colors from image."""
        # Simplified version - in production would use k-means clustering
        if len(img_array.shape) == 3:
            pixels = img_array.reshape(-1, 3)
            # Get unique colors and their counts
            unique, counts = np.unique(pixels, axis=0, return_counts=True)
            # Sort by frequency
            idx = np.argsort(-counts)[:n_colors]
            return [tuple(map(int, unique[i])) for i in idx]
        return []
    
    @staticmethod
    def _calculate_green_ratio(img_array: np.ndarray) -> float:
        """Calculate the ratio of green pixels in image."""
        if len(img_array.shape) != 3 or img_array.shape[2] != 3:
            return 0.0
        
        # Simple green detection
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        green_mask = (g > r * 1.1) & (g > b * 1.1) & (g > 50)
        
        return float(np.sum(green_mask) / green_mask.size)
    
    @classmethod
    async def validate_plant_image(cls, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate if image contains a plant.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Process image first
            _, metadata = await cls.process_image(image_data)
            
            # Extract features
            features = await cls.extract_plant_features(image_data)
            
            # Basic validation
            if features.get("green_ratio", 0) < 0.05:
                return False, "Image doesn't appear to contain a plant"
            
            if features.get("brightness", 0) < 30:
                return False, "Image is too dark"
            
            if features.get("brightness", 0) > 250:
                return False, "Image is too bright/overexposed"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False, str(e)
