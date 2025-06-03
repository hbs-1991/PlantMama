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
        
        # Extract RGB channels
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        
        # Green detection: green channel is significantly higher than red and blue
        green_mask = (g > r * 1.2) & (g > b * 1.2) & (g > 40) & (g < 250)
        
        return round(float(np.sum(green_mask) / green_mask.size), 3)
    
    @staticmethod
    def _calculate_brown_ratio(img_array: np.ndarray) -> float:
        """Calculate the ratio of brown pixels (potential dead/diseased areas)."""
        if len(img_array.shape) != 3 or img_array.shape[2] != 3:
            return 0.0
        
        # Extract RGB channels
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        
        # Brown detection: red > green > blue, and not too bright
        brown_mask = (r > g) & (g > b) & (r > 50) & (r < 180) & (g > 30) & (g < 140)
        
        return round(float(np.sum(brown_mask) / brown_mask.size), 3)
    
    @staticmethod
    def _calculate_texture_complexity(img_array: np.ndarray) -> float:
        """Calculate texture complexity using edge detection."""
        if len(img_array.shape) == 3:
            # Convert to grayscale
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array
        
        # Simple edge detection using gradient
        grad_x = np.abs(np.diff(gray, axis=0))
        grad_y = np.abs(np.diff(gray, axis=1))
        
        # Average gradient magnitude
        avg_gradient = (np.mean(grad_x) + np.mean(grad_y)) / 2
        
        return round(float(avg_gradient), 2)
    
    @staticmethod
    def _detect_leaf_edges(img_array: np.ndarray) -> dict:
        """Detect potential leaf edges in the image."""
        if len(img_array.shape) == 3:
            # Use green channel for leaf detection
            green = img_array[:, :, 1]
        else:
            green = img_array
        
        # Simple edge detection
        edges = np.abs(np.diff(green, axis=0))
        edge_strength = float(np.mean(edges))
        
        return {
            "edge_strength": round(edge_strength, 2),
            "has_clear_edges": edge_strength > 20
        }
    
    @staticmethod
    def _detect_visual_issues(features: dict) -> list:
        """Detect potential plant issues based on visual features."""
        issues = []
        
        # Check for too much brown (potential disease/dead areas)
        if features.get("brown_ratio", 0) > 0.3:
            issues.append("High brown color ratio - possible dead or diseased areas")
        
        # Check for low green ratio
        if features.get("green_ratio", 0) < 0.1:
            issues.append("Low green color ratio - may not be a healthy plant")
        
        # Check brightness issues
        brightness = features.get("brightness", 128)
        if brightness < 50:
            issues.append("Image too dark for accurate analysis")
        elif brightness > 220:
            issues.append("Image overexposed - details may be lost")
        
        # Check contrast
        if features.get("contrast", 50) < 20:
            issues.append("Low contrast - image may be blurry or out of focus")
        
        return issues
    
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
            processed_data, metadata = await cls.process_image(image_data)
            
            # Extract features
            features = await cls.extract_plant_features(processed_data)
            
            # Check for critical issues
            if features.get("green_ratio", 0) < 0.05:
                return False, "Image doesn't appear to contain a plant (very low green content)"
            
            brightness = features.get("brightness", 128)
            if brightness < 30:
                return False, "Image is too dark for analysis"
            elif brightness > 250:
                return False, "Image is too bright/overexposed for analysis"
            
            if features.get("brightness", 0) > 250:
                return False, "Image is too bright/overexposed"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False, str(e)
