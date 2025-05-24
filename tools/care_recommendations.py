"""Care recommendation tools."""

from typing import List

from agents import tool
from pydantic import BaseModel, Field


class CareInstructions(BaseModel):
    """Personalized care instructions."""
    
    watering: str = Field(description="Watering schedule and amount")
    lighting: str = Field(description="Light requirements")
    temperature: str = Field(description="Temperature range")
    humidity: str = Field(description="Humidity requirements")
    soil: str = Field(description="Soil type and pH")
    seasonal_tips: List[str] = Field(description="Season-specific care tips")


class FertilizerRecommendation(BaseModel):
    """Fertilizer recommendation."""
    
    name: str = Field(description="Fertilizer name/type")
    npk_ratio: str = Field(description="NPK ratio (e.g., 10-10-10)")
    frequency: str = Field(description="Application frequency")
    amount: str = Field(description="Amount per application")
    organic: bool = Field(description="Is organic fertilizer")
    price_range: str = Field(description="Price category: budget/medium/premium")


class ToolRecommendation(BaseModel):
    """Gardening tool recommendation."""
    
    tool_name: str = Field(description="Tool name")
    purpose: str = Field(description="What it's used for")
    price_range: str = Field(description="Price range")
    brand_suggestions: List[str] = Field(description="Recommended brands")
    purchase_links: List[str] = Field(description="Where to buy")


@tool
async def generate_care_instructions(
    plant_id: str,
    diagnosis: dict,
    season: str,
) -> CareInstructions:
    """
    Generate personalized care instructions based on plant type and diagnosis.
    
    Args:
        plant_id: Plant identifier or species
        diagnosis: Diagnosis results
        season: Current season
        
    Returns:
        Detailed care instructions
    """
    # Placeholder implementation
    return CareInstructions(
        watering="Water when top 2 inches of soil are dry (approximately twice a week)",
        lighting="Bright, indirect light. Avoid direct sunlight.",
        temperature="65-80°F (18-27°C)",
        humidity="50-60% humidity preferred",
        soil="Well-draining potting mix with perlite",
        seasonal_tips=[
            "Reduce watering frequency in winter",
            "Increase humidity with a pebble tray",
            "Fertilize monthly during growing season",
        ],
    )


@tool
async def recommend_fertilizers(
    plant_type: str,
    soil_condition: str,
    season: str,
) -> List[FertilizerRecommendation]:
    """
    Recommend suitable fertilizers based on plant needs.
    
    Args:
        plant_type: Type/species of plant
        soil_condition: Current soil condition
        season: Current season
        
    Returns:
        List of fertilizer recommendations
    """
    # Placeholder implementation
    return [
        FertilizerRecommendation(
            name="Balanced Liquid Fertilizer",
            npk_ratio="10-10-10",
            frequency="Every 2 weeks during growing season",
            amount="1/4 strength of package directions",
            organic=False,
            price_range="budget",
        ),
        FertilizerRecommendation(
            name="Organic Compost Tea",
            npk_ratio="3-2-2",
            frequency="Weekly during summer",
            amount="Dilute 1:5 with water",
            organic=True,
            price_range="medium",
        ),
    ]


@tool
async def recommend_tools(care_task: str, plant_size: str) -> List[ToolRecommendation]:
    """
    Recommend appropriate gardening tools for specific tasks.
    
    Args:
        care_task: Type of care task (pruning, repotting, etc.)
        plant_size: Size of the plant (small/medium/large)
        
    Returns:
        List of tool recommendations
    """
    # Placeholder implementation
    return [
        ToolRecommendation(
            tool_name="Pruning Shears",
            purpose="Clean cuts for pruning and deadheading",
            price_range="$15-40",
            brand_suggestions=["Fiskars", "Felco", "Corona"],
            purchase_links=["Amazon", "Local garden center"],
        ),
        ToolRecommendation(
            tool_name="Moisture Meter",
            purpose="Check soil moisture levels accurately",
            price_range="$10-25",
            brand_suggestions=["XLUX", "Sonkir", "Dr.meter"],
            purchase_links=["Amazon", "Home Depot"],
        ),
    ]
