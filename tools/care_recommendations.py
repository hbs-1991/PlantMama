import json
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime

from agents import function_tool
from pydantic import BaseModel, Field, ConfigDict
from openai import AsyncOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class CareInstructions(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 💥 обязательный параметр
    watering: str = Field(description="Рекомендации по поливу")
    lighting: str = Field(description="Рекомендации по освещению")
    soil: str = Field(description="Рекомендации по почве")
    seasonal_tips: List[str] = Field(description="Сезонные советы по уходу")


class FertilizerRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 💥 обязательный параметр
    name: str = Field(description="Название удобрения")
    npk_ratio: str = Field(description="Соотношение NPK")
    frequency: str = Field(description="Как часто применять")
    amount: str = Field(description="Количество за раз")
    organic: bool = Field(description="Является ли органическим")
    price_range: str = Field(description="Диапазон цен")


class ToolRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 💥 обязательный параметр
    name: str = Field(description="Название инструмента")
    purpose: str = Field(description="Назначение")
    price_range: str = Field(description="Диапазон цен")
    brand: str = Field(description="Рекомендуемый бренд")
    purchase_links: List[str] = Field(description="Где купить (общие магазины, без конкретных URL)")

class DiagnosisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    health_score: float = Field(description="Индекс здоровья растения (1-10)")
    issues: list[str] = Field(description="Список обнаруженных проблем")
    severity: str = Field(description="Уровень тяжести: mild, moderate, severe")
    confidence: float = Field(description="Достоверность диагноза (0-1)")
    recommendations: list[str] = Field(description="Список рекомендаций по первичным действиям")


@function_tool
async def generate_care_instructions(
    plant_id: str,
    diagnosis: Dict,
    season: str,
) -> CareInstructions:
    """
    Инструмент для генерации рекомендаций по уходу на основе диагноза и сезона.
    Возвращаемый JSON строго в формате:
    {
      "watering": "<строка>",
      "lighting": "<строка>",
      "soil": "<строка>",
      "seasonal_tips": ["<строка1>", "<строка2>", ...]
    }
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Подготавливаем JSON-строку с диагнозом для LLM
    diag_json = json.dumps(diagnosis, ensure_ascii=False)

    system_prompt = (
        "Ты — эксперт по уходу за растениями. "
        "Тебе дан диагноз в формате JSON и текущее время года. "
        "Верни строго JSON с ключами: watering, lighting, soil, seasonal_tips.\n"
        "Пример:\n"
        "{\n"
        '  "watering": "Полив раз в 5 дней...",\n'
        '  "lighting": "Нужен рассеянный свет...",\n'
        '  "soil": "Рекомендуется плодородная, питательная почва...",\n'
        '  "seasonal_tips": ["Совет 1", "Совет 2"]\n'
        "}\n"
        "Никакого дополнительного текста."
    )

    user_prompt = (
        f"Диагноз:\n{diag_json}\nСезон: {season}.\n\n"
        "Сформируй рекомендации по уходу строго в формате JSON."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=700,
        )

        instructions_text = response.choices[0].message.content.strip()
        logger.info(f"Raw care instructions response: {instructions_text}")

        data = json.loads(instructions_text)
        return CareInstructions.model_validate(data)

    except Exception as exc:
        logger.error(f"Ошибка generate_care_instructions: {exc}", exc_info=True)
        # Возвращаем «пустые» рекомендации
        return CareInstructions(
            watering="Не удалось сгенерировать рекомендации по поливу.",
            lighting="Не удалось сгенерировать рекомендации по освещению.",
            soil="Не удалось сгенерировать рекомендации по почве.",
            seasonal_tips=["Не удалось сгенерировать сезонные советы."],
        )


@function_tool
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
            model="gpt-4.1-mini",
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
        result = [FertilizerRecommendation.model_validate(item) for item in data]
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


@function_tool
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
        result = [ToolRecommendation.model_validate(item) for item in data]
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
