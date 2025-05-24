"""Input validators."""

import re
from typing import Optional, Tuple

from config.settings import settings


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_telegram_id(telegram_id: str) -> bool:
        """
        Validate Telegram user ID.
        
        Args:
            telegram_id: Telegram ID to validate
            
        Returns:
            True if valid
        """
        return telegram_id.isdigit() and len(telegram_id) <= 20
    
    @staticmethod
    def validate_plant_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate plant name.
        
        Args:
            name: Plant name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Plant name cannot be empty"
        
        if len(name) > 100:
            return False, "Plant name is too long (max 100 characters)"
        
        if not re.match(r"^[a-zA-Z0-9\s\-'.]+$", name):
            return False, "Plant name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_image_size(image_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate image file size.
        
        Args:
            image_size: Size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if image_size <= 0:
            return False, "Invalid image size"
        
        if image_size > settings.MAX_IMAGE_SIZE:
            max_mb = settings.MAX_IMAGE_SIZE / (1024 * 1024)
            return False, f"Image too large (max {max_mb}MB)"
        
        return True, None
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Limit length
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Remove control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
        
        return text.strip()
    
    @staticmethod
    def validate_season(season: str) -> bool:
        """
        Validate season name.
        
        Args:
            season: Season name
            
        Returns:
            True if valid
        """
        valid_seasons = {"spring", "summer", "fall", "autumn", "winter"}
        return season.lower() in valid_seasons
    
    @staticmethod
    def validate_pot_size(size: str) -> bool:
        """
        Validate pot size.
        
        Args:
            size: Pot size (small/medium/large)
            
        Returns:
            True if valid
        """
        valid_sizes = {"small", "medium", "large", "extra large", "xl"}
        return size.lower() in valid_sizes
