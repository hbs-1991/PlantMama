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
    Инструмент для подбора удобрений. LLM возвращает строго JSON-массив объектов:
    [
      {
        "name": "...",
        "npk_ratio": "...",
        "frequency": "...",
        "amount": "...",
        "organic": <true|false>,
        "price_range": "..."
      },
      ...
    ]
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = (
        "Ты — эксперт по удобрениям для домашних растений. "
        "На вход тебе даются тип растения, состояние почвы и время года. "
        "Верни строго JSON-массив из трёх объектов с полями:\n"
        "  name, npk_ratio, frequency, amount, organic, price_range.\n"
        "Пример ответа:\n"
        "[\n"
        "  {\"name\": \"Удобрение A\", \"npk_ratio\": \"10-10-10\", \"frequency\": \"раз в 2 недели\", "
        "\"amount\": \"5 г\", \"organic\": true, \"price_range\": \"500-700 ₽\"},\n"
        "  {\"name\": \"Удобрение B\", \"npk_ratio\": \"20-20-20\", \"frequency\": \"раз в месяц\", "
        "\"amount\": \"7 г\", \"organic\": false, \"price_range\": \"400-600 ₽\"},\n"
        "  {\"name\": \"Удобрение C\", \"npk_ratio\": \"5-5-5\", \"frequency\": \"раз в 3 недели\", "
        "\"amount\": \"10 г\", \"organic\": true, \"price_range\": \"600-800 ₽\"}\n"
        "]\n"
        "Никакого другого текста."
    )

    user_prompt = (
        f"Тип растения: {plant_type}.\n"
        f"Состояние почвы: {soil_condition}.\n"
        f"Сезон: {season}.\n\n"
        "Сформируй JSON-массив из трёх рекомендаций."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
        )

        fert_text = response.choices[0].message.content.strip()
        logger.info(f"Raw fertilizer recommendations response: {fert_text}")

        data = json.loads(fert_text)
        result = [FertilizerRecommendation.parse_obj(item) for item in data]
        return result

    except Exception as exc:
        logger.error(f"Ошибка recommend_fertilizers: {exc}", exc_info=True)
        # Возвращаем «пустой» список с одним дефолтом
        return [
            FertilizerRecommendation(
                name="Универсальное удобрение",
                npk_ratio="NPK неизвестно",
                frequency="раз в месяц",
                amount="5 г",
                organic=False,
                price_range="от 300 ₽",
            )
        ]


@tool
async def recommend_tools(care_task: str, plant_size: str) -> List[ToolRecommendation]:
    """
    Инструмент для подбора инструментов для ухода. LLM возвращает строго JSON-массив:
    [
      {
        "name": "...",
        "purpose": "...",
        "price_range": "...",
        "brand": "...",
        "purchase_links": ["магазин1", "магазин2"]
      },
      ...
    ]
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = (
        "Ты — бот, отвечающий за подбор садового инвентаря. "
        "На вход тебе дается задача по уходу (care_task) и размер растения. "
        "Верни строго JSON-массив из трёх объектов с ключами:\n"
        "  name, purpose, price_range, brand, purchase_links.\n"
        "Пример:\n"
        "[\n"
        "  {\"name\": \"Ножницы для обрезки\", \"purpose\": \"обрезка сухих веток\", "
        "\"price_range\": \"500-700 ₽\", \"brand\": \"Gardena\", "
        "\"purchase_links\": [\"Леруа Мерлен\", \"Ozon\"]},\n"
        "  {\"name\": \"Перчатки садовые\", \"purpose\": \"защита рук\", "
        "\"price_range\": \"200-300 ₽\", \"brand\": \"Fiskars\", "
        "\"purchase_links\": [\"Петрович\", \"Wildberries\"]},\n"
        "  {\"name\": \"Компостёр\", \"purpose\": \"приготовление компоста\", "
        "\"price_range\": \"1500-2000 ₽\", \"brand\": \"BioMaster\", "
        "\"purchase_links\": [\"Ozon\", \"Садовый центр\"]}\n"
        "]\n"
        "Никакого лишнего текста."
    )

    user_prompt = (
        f"Задача по уходу: {care_task}.\n"
        f"Размер растения: {plant_size}.\n\n"
        "Выведи JSON-массив."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
        )

        tools_text = response.choices[0].message.content.strip()
        logger.info(f"Raw tool recommendations response: {tools_text}")

        data = json.loads(tools_text)
        result = [ToolRecommendation.parse_obj(item) for item in data]
        return result

    except Exception as exc:
        logger.error(f"Ошибка recommend_tools: {exc}", exc_info=True)
        # Возвращаем «пустой» дефолт
        return [
            ToolRecommendation(
                name="Стандартные перчатки",
                purpose="защита рук при уходе",
                price_range="200-300 ₽",
                brand="Generic",
                purchase_links=["Любой садовый магазин"],
            )
        ]
