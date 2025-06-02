"""Plant diagnosis tools."""

import base64
import logging
import re
import json
from typing import Dict, Optional, List

from agents import tool
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class DiagnosisResult(BaseModel):
    health_score: float = Field(description="Индекс здоровья растения (1-10)")
    issues: List[str] = Field(description="Список обнаруженных проблем")
    severity: str = Field(description="Уровень тяжести: mild, moderate, severe")
    confidence: float = Field(description="Достоверность диагноза (0-1)")
    recommendations: List[str] = Field(description="Список рекомендаций по первичным действиям")


class PlantIdentification(BaseModel):
    species: str = Field(description="Название вида/таксона (вида)")
    common_name: str = Field(description="Распространенное название")
    scientific_name: str = Field(description="Научное латинское название")
    confidence: float = Field(description="Достоверность идентификации (0-1)")
    alternatives: List[str] = Field(description="Альтернативные варианты вида")


@tool
async def diagnose_plant_photo(
    image_data: bytes,
    user_context: Optional[Dict] = None,
) -> DiagnosisResult:
    """
    Инструмент для диагностики растения по загруженной фотографии.
    Ожидает, что LLM вернет строго JSON следующего вида:
    {
      "health_score": <float 1-10>,
      "issues": ["проблема1", "проблема2", ...],
      "severity": "mild" | "moderate" | "severe",
      "confidence": <float 0-1>,
      "recommendations": ["действие1", "действие2", ...]
    }
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Преобразуем байты картинки в base64 и встраиваем в запрос
    b64 = base64.b64encode(image_data).decode("utf-8")
    image_str = f"data:image/jpeg;base64,{b64}"

    system_prompt = (
        "Ты — эксперт по фитодиагностике. "
        "Твоя задача — проанализировать изображение растения и вернуть результат строго в формате JSON.\n"
        "JSON-объект должен содержать поля:\n"
        "  - health_score: число от 1 до 10 (чем выше — тем лучше),\n"
        "  - issues: массив строк (описание каждой обнаруженной проблемы),\n"
        "  - severity: один из вариантов \"mild\", \"moderate\", \"severe\",\n"
        "  - confidence: число от 0 до 1,\n"
        "  - recommendations: массив строк (рекомендации по первоочередным действиям).\n"
        "Никакого другого текста — только чистый JSON."
    )

    user_prompt = (
        f"Вот изображение растения:\n{image_str}\n\n"
        "Проанализируй его и верни JSON."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=800,
        )

        diagnosis_text = response.choices[0].message.content.strip()
        logger.info(f"Raw diagnose response: {diagnosis_text}")

        # Парсим JSON
        data = json.loads(diagnosis_text)
        # Валидируем через Pydantic
        result = DiagnosisResult.parse_obj(data)
        return result

    except Exception as exc:
        logger.error(f"Ошибка diagnose_plant_photo: {exc}", exc_info=True)
        # Возвращаем максимально нейтральный «пустой» диагноз
        return DiagnosisResult(
            health_score=5.0,
            issues=[],
            severity="moderate",
            confidence=0.0,
            recommendations=["Не удалось провести точную диагностику. Попробуйте сделать более чёткое фото и повторить запрос."],
        )


@tool
async def identify_plant_species(image_data: bytes) -> PlantIdentification:
    """
    Инструмент для идентификации вида растения по фотографии.
    LLM должен вернуть строго JSON:
    {
    "species": "<название вида>",
      "common_name": "<распространенное название>",
      "scientific_name": "<латинское название>",
      "confidence": <число 0-1>,
      "alternatives": ["вариант1", "вариант2", ...]
    }
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    b64 = base64.b64encode(image_data).decode("utf-8")
    image_str = f"data:image/jpeg;base64,{b64}"

    system_prompt = (
        "Ты — эксперт по ботанике. "
        "Твоя задача — по изображению растения определить вид и вернуть JSON.\n"
        "Формат JSON:\n"
        "  - species: строка (название вида),\n"
        "  - common_name: строка (распространенное название),\n"
        "  - scientific_name: строка (латинское название),\n"
        "  - confidence: число от 0 до 1,\n"
        "  - alternatives: массив строк (альтернативные близкие виды).\n"
        "Никакого другого текста — только JSON."
    )

    user_prompt = (
        f"Вот изображение растения:\n{image_str}\n\n"
        "Определи вид и верни JSON."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
        )

        ident_text = response.choices[0].message.content.strip()
        logger.info(f"Raw identify response: {ident_text}")

        data = json.loads(ident_text)
        result = PlantIdentification.parse_obj(data)
        return result

    except Exception as exc:
        logger.error(f"Ошибка identify_plant_species: {exc}", exc_info=True)
        # Пустая заглушка
        return PlantIdentification(
            species="Неизвестно",
            common_name="Неизвестно",
            scientific_name="Неизвестно",
            confidence=0.0,
            alternatives=[],
        )
