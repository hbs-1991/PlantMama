"""Image processing service."""

import io
import logging
import hashlib
from typing import Tuple, Optional
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageOps, ImageEnhance
import numpy as np

from config.settings import settings

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Service for processing plant images."""
    
    MAX_SIZE = (1024, 1024)  # Maximum image dimensions
    ALLOWED_FORMATS = {"JPEG", "PNG", "JPG", "WEBP"}
    MIN_SIZE = (100, 100)  # Minimum acceptable image size
    
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
            
            # Validate size
            if image.size[0] < cls.MIN_SIZE[0] or image.size[1] < cls.MIN_SIZE[1]:
                raise ValueError(f"Image too small: {image.size}")
            
            # Get metadata
            metadata = {
                "original_format": image.format,
                "original_size": image.size,
                "mode": image.mode,
                "file_size": len(image_data),
            }
            
            # Calculate hash for deduplication
            metadata["hash"] = hashlib.md5(image_data).hexdigest()
            
            # Fix orientation using EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Convert to RGB if necessary
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
                metadata["converted_to_rgb"] = True
            
            # Enhance image for better plant detection
            image = cls._enhance_plant_image(image)
            
            # Resize if too large
            if image.size[0] > cls.MAX_SIZE[0] or image.size[1] > cls.MAX_SIZE[1]:
                image.thumbnail(cls.MAX_SIZE, Image.Resampling.LANCZOS)
                metadata["resized"] = True
                metadata["new_size"] = image.size
            
            # Save processed image
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85, optimize=True)
            processed_data = output.getvalue()
            
            metadata["processed_size"] = len(processed_data)
            metadata["compression_ratio"] = round(len(processed_data) / len(image_data), 2)
            
            logger.info(f"Processed image: {metadata}")
            return processed_data, metadata
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @classmethod
    def _enhance_plant_image(cls, image: Image.Image) -> Image.Image:
        """Enhance image for better plant detection."""
        # Slightly increase contrast
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(1.1)
        
        # Slightly increase color saturation
        color = ImageEnhance.Color(image)
        image = color.enhance(1.1)
        
        # Ensure good sharpness
        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(1.1)
        
        return image
    
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
            
            # Convert to RGB for consistent analysis
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract features
            features = {
                "dominant_colors": cls._get_dominant_colors(img_array),
                "brightness": float(np.mean(img_array)),
                "contrast": float(np.std(img_array)),
                "green_ratio": cls._calculate_green_ratio(img_array),
                "brown_ratio": cls._calculate_brown_ratio(img_array),
                "texture_complexity": cls._calculate_texture_complexity(img_array),
                "leaf_edge_detection": cls._detect_leaf_edges(img_array),
            }
            
            # Detect potential issues
            features["potential_issues"] = cls._detect_visual_issues(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    @staticmethod
    def _get_dominant_colors(img_array: np.ndarray, n_colors: int = 5) -> list:
        """Get dominant colors from image using simple quantization."""
        if len(img_array.shape) != 3:
            return []
        
        # Reshape to list of pixels
        pixels = img_array.reshape(-1, 3)
        
        # Simple color quantization
        # Reduce color space to 6 bits per channel (64 colors per channel)
        quantized = (pixels >> 2) << 2
        
        # Get unique colors and their counts
        unique, counts = np.unique(quantized, axis=0, return_counts=True)
        
        # Sort by frequency
        idx = np.argsort(-counts)[:n_colors]
        
        # Return as list of RGB tuples with percentages
        total_pixels = len(pixels)
        dominant_colors = []
        for i in idx:
            color = tuple(map(int, unique[i]))
            percentage = round(counts[i] / total_pixels * 100, 1)
            dominant_colors.append({"color": color, "percentage": percentage})
        
        return dominant_colors
    
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
