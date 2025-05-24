"""Plant knowledge service."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PlantKnowledgeBase:
    """Service for plant care knowledge and information."""
    
    # Common plant database (simplified version)
    PLANT_DATABASE = {
        "monstera_deliciosa": {
            "common_name": "Swiss Cheese Plant",
            "scientific_name": "Monstera deliciosa",
            "family": "Araceae",
            "origin": "Central America",
            "care": {
                "light": "Bright, indirect light",
                "water": "Water when top 2-3 inches of soil are dry",
                "humidity": "Prefers 60% or higher",
                "temperature": "65-85°F (18-29°C)",
                "soil": "Well-draining potting mix",
                "fertilizer": "Monthly during growing season",
            },
            "common_issues": [
                "Yellow leaves: Overwatering or nutrient deficiency",
                "Brown tips: Low humidity or fluoride in water",
                "No fenestrations: Needs more light or maturity",
            ],
        },
        "ficus_lyrata": {
            "common_name": "Fiddle Leaf Fig",
            "scientific_name": "Ficus lyrata",
            "family": "Moraceae",
            "origin": "West Africa",
            "care": {
                "light": "Bright, indirect to direct light",
                "water": "Water when top inch is dry",
                "humidity": "40-60%",
                "temperature": "60-75°F (15-24°C)",
                "soil": "Well-draining, slightly acidic",
                "fertilizer": "Every 2-4 weeks in growing season",
            },
            "common_issues": [
                "Brown spots: Root rot or bacterial infection",
                "Dropping leaves: Stress from environmental changes",
                "Yellowing: Overwatering or poor drainage",
            ],
        },
    }
    
    # Seasonal care adjustments
    SEASONAL_CARE = {
        "spring": {
            "general": "Active growing season begins",
            "watering": "Increase frequency as growth accelerates",
            "fertilizing": "Resume regular feeding schedule",
            "repotting": "Best time for repotting if needed",
            "pruning": "Good time for pruning and propagation",
        },
        "summer": {
            "general": "Peak growing season",
            "watering": "Monitor closely, may need daily watering",
            "fertilizing": "Regular feeding every 2-4 weeks",
            "humidity": "Increase humidity for tropical plants",
            "pests": "Watch for pest infestations",
        },
        "fall": {
            "general": "Growth slows down",
            "watering": "Gradually reduce frequency",
            "fertilizing": "Reduce or stop feeding",
            "light": "Consider grow lights as days shorten",
            "preparation": "Prepare for dormancy",
        },
        "winter": {
            "general": "Dormant season for most plants",
            "watering": "Minimal watering, let soil dry more",
            "fertilizing": "Stop fertilizing most plants",
            "temperature": "Keep away from cold drafts",
            "humidity": "Combat dry indoor air",
        },
    }
    
    @classmethod
    async def get_plant_info(cls, plant_identifier: str) -> Optional[Dict]:
        """
        Get plant information from knowledge base.
        
        Args:
            plant_identifier: Plant species or common name
            
        Returns:
            Plant information dict or None
        """
        # Normalize identifier
        normalized = plant_identifier.lower().replace(" ", "_")
        
        # Try exact match first
        if normalized in cls.PLANT_DATABASE:
            return cls.PLANT_DATABASE[normalized]
        
        # Try partial match
        for key, info in cls.PLANT_DATABASE.items():
            if normalized in key or normalized in info["common_name"].lower():
                return info
        
        return None
    
    @classmethod
    async def get_seasonal_care(cls, season: str) -> Dict:
        """
        Get seasonal care recommendations.
        
        Args:
            season: Current season
            
        Returns:
            Seasonal care guide
        """
        return cls.SEASONAL_CARE.get(season.lower(), cls.SEASONAL_CARE["spring"])
    
    @classmethod
    async def get_pest_solutions(cls, pest_type: str) -> List[Dict]:
        """
        Get solutions for common plant pests.
        
        Args:
            pest_type: Type of pest
            
        Returns:
            List of treatment options
        """
        pest_solutions = {
            "aphids": [
                {
                    "method": "Neem oil spray",
                    "description": "Mix 2 tsp neem oil with 1 quart water and spray",
                    "frequency": "Every 3-4 days until gone",
                },
                {
                    "method": "Insecticidal soap",
                    "description": "Spray directly on aphids",
                    "frequency": "Daily until eliminated",
                },
            ],
            "spider_mites": [
                {
                    "method": "Increase humidity",
                    "description": "Mist regularly or use humidifier",
                    "frequency": "Daily",
                },
                {
                    "method": "Rubbing alcohol",
                    "description": "70% isopropyl alcohol on cotton swab",
                    "frequency": "Spot treat affected areas",
                },
            ],
            "fungus_gnats": [
                {
                    "method": "Let soil dry",
                    "description": "Allow top 2 inches to dry between watering",
                    "frequency": "Adjust watering schedule",
                },
                {
                    "method": "Sticky traps",
                    "description": "Yellow sticky traps near soil",
                    "frequency": "Replace when full",
                },
            ],
        }
        
        return pest_solutions.get(pest_type.lower(), [])
    
    @classmethod
    async def get_fertilizer_guide(cls, plant_type: str, season: str) -> Dict:
        """
        Get fertilizer recommendations.
        
        Args:
            plant_type: Type of plant
            season: Current season
            
        Returns:
            Fertilizer guide
        """
        # Simplified guide
        if season.lower() in ["fall", "winter"]:
            return {
                "frequency": "Reduce or stop fertilizing",
                "reason": "Most plants are dormant",
                "exceptions": ["Winter-blooming plants", "Actively growing tropicals"],
            }
        
        return {
            "frequency": "Every 2-4 weeks",
            "type": "Balanced liquid fertilizer (10-10-10)",
            "dilution": "Half strength recommended on package",
            "application": "Water first, then apply fertilizer",
            "signs_needed": ["Slow growth", "Pale leaves", "Small new leaves"],
            "signs_excess": ["Salt buildup", "Brown leaf tips", "Rapid weak growth"],
        }
