import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

from agents import function_tool
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from config.settings import settings
from services.plant_knowledge import PlantKnowledgeBase

logger = logging.getLogger(__name__)


class WateringSchedule(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 💥 обязательный параметр
    frequency_days: int = Field(description="Интервал полива (в днях)")
    amount_ml: int = Field(description="Количество воды (в мл)")
    indicators: List[str] = Field(description="Признаки, указывающие на необходимость полива")


class PlantInfo(BaseModel):
    common_name: str = Field(description="Распространенное название растения")
    scientific_name: str = Field(description="Латинское название растения")
    family: str = Field(description="Ботаническое семейство")
    origin: str = Field(description="Регион происхождения")
    description: str = Field(description="Краткое описание вида")
    difficulty: str = Field(description="Уровень сложности в уходе: easy, medium, hard")
    watering: str = Field(description="Общие рекомендации по поливу")
    lighting: str = Field(description="Общие рекомендации по освещению")
    fertilizing: str = Field(description="Общие рекомендации по удобрению")
    temperature_range: str = Field(description="Оптимальный температурный диапазон")
    propagation: str = Field(description="Методы размножения")
    pet_friendly: bool = Field(description="Безопасно ли для домашних животных")
    watering_schedule: WateringSchedule = Field(description="Структура с расписанием полива")


@function_tool
async def get_plant_encyclopedia(plant_name: str) -> PlantInfo:
    """
    Инструмент для получения справочной информации о растении.
    Сначала проверяем локальную БД, затем, при необходимости, дополняем через LLM.
    LLM должен вернуть JSON вида:
    {
      "common_name": "...",
      "scientific_name": "...",
      "family": "...",
      "origin": "...",
      "description": "...",
      "difficulty": "easy"|"medium"|"hard",
      "watering": "...",
      "lighting": "...",
      "fertilizing": "...",
      "temperature_range": "...",
      "propagation": "...",
      "pet_friendly": <true|false>,
      "watering_schedule": {
        "frequency_days": <int>,
        "amount_ml": <int>,
        "indicators": ["...", "..."]
      }
    }
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Попытка получить данные из локальной БД
    local_info = await PlantKnowledgeBase.get_plant_info(plant_name)

    # Заведем «скелет» ответа, чтобы везде были дефолты
    result_dict: Dict = {
        "common_name": plant_name,
        "scientific_name": "Неизвестно",
        "family": "Неизвестно",
        "origin": "Неизвестно",
        "description": "Нет доступной информации.",
        "difficulty": "medium",
        "watering": "",
        "lighting": "",
        "fertilizing": "",
        "temperature_range": "",
        "propagation": "",
        "pet_friendly": False,
        "watering_schedule": {
            "frequency_days": 7,
            "amount_ml": 200,
            "indicators": [],
        },
    }

    # Если локальная БД есть — подставляем ее значения
    if local_info:
        for key, value in local_info.items():
            if key in result_dict:
                result_dict[key] = value

    # Теперь формируем запрос к LLM, чтобы дополнить недостающие поля
    # Определим текущий сезон по дате сервера (UTC). Если нужно брать локально по пользователю — сюда передавать его timezone.
    month = datetime.now().month
    if month in (12, 1, 2):
        season = "зима"
    elif month in (3, 4, 5):
        season = "весна"
    elif month in (6, 7, 8):
        season = "лето"
    else:
        season = "осень"

    system_prompt = (
        "Ты — бот-энциклопедия по комнатным растениям. "
        "Тебе дано частичное описание растения (в JSON) с некоторыми полями. "
        "Твоя задача — дополнить недостающие текстовые поля и поля watering_schedule, "
        "вернув строго JSON точно по схеме PlantInfo.\n"
        "Формат ответа строго JSON:\n"
        "{\n"
        '  "common_name": "...",\n'
        '  "scientific_name": "...",\n'
        '  "family": "...",\n'
        '  "origin": "...",\n'
        '  "description": "...",\n'
        '  "difficulty": "easy"|"medium"|"hard",\n'
        '  "watering": "...",\n'
        '  "lighting": "...",\n'
        '  "fertilizing": "...",\n'
        '  "temperature_range": "...",\n'
        '  "propagation": "...",\n'
        '  "pet_friendly": <true|false>,\n'
        '  "watering_schedule": {\n'
        '    "frequency_days": <int>,\n'
        '    "amount_ml": <int>,\n'
        '    "indicators": ["...", "..."]\n'
        "  }\n"
        "}\n"
        "Никакого дополнительного текста."
    )

    partial_json = json.dumps(result_dict, ensure_ascii=False)

    user_prompt = (
        f"Частичные данные:\n{partial_json}\n"
        f"Текущий сезон: {season}.\n\n"
        "Дополни их и верни полный JSON."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
        )

        info_text = response.choices[0].message.content.strip()
        logger.info(f"Raw encyclopedia response: {info_text}")

        data = json.loads(info_text)
        return PlantInfo.model_validate(data)

    except Exception as exc:
        logger.error(f"Ошибка get_plant_encyclopedia: {exc}", exc_info=True)
        # Возвращаем тот скелет, что был
        return PlantInfo.model_validate(result_dict)


@function_tool
async def calculate_watering_schedule(
    plant_id: str,
    pot_size: str,
    humidity: float,
) -> WateringSchedule:
    """
    Инструмент для расчёта расписания полива. Возвращает строго JSON вида:
    {
      "frequency_days": <int>,
      "amount_ml": <int>,
      "indicators": ["...", "..."]
    }
    """
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Определяем текущий сезон
    month = datetime.now().month
    if month in (12, 1, 2):
        season = "зима"
    elif month in (3, 4, 5):
        season = "весна"
    elif month in (6, 7, 8):
        season = "лето"
    else:
        season = "осень"

    system_prompt = (
        "Ты — бот, рассчитывающий расписание полива для дома. "
        "Тебе даны plant_id, размер горшка (pot_size), процент влажности почвы (humidity) и текущий сезон. "
        "Верни строго JSON:\n"
        "{\n"
        '  "frequency_days": <целое число>,\n'
        '  "amount_ml": <целое число>,\n'
        '  "indicators": ["строка1", "строка2"]\n'
        "}\n"
        "Никакого дополнительного текста."
    )

    user_prompt = (
        f"Plant ID: {plant_id}.\n"
        f"Размер горшка: {pot_size}.\n"
        f"Влажность почвы: {humidity}.\n"
        f"Сезон: {season}.\n\n"
        "Сформируй JSON."
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

        schedule_text = response.choices[0].message.content.strip()
        logger.info(f"Raw watering schedule response: {schedule_text}")

        data = json.loads(schedule_text)
        return WateringSchedule.model_validate(data)

    except Exception as exc:
        logger.error(f"Ошибка calculate_watering_schedule: {exc}", exc_info=True)
        # Дефолтное расписание
        return WateringSchedule(
            frequency_days=7,
            amount_ml=200,
            indicators=["Сухая поверхность почвы", "Листья поникли"],
        )
