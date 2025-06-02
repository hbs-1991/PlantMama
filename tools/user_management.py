"""User management tools."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from agents import tool
from pydantic import BaseModel, Field

logger_name = "user_management"
# Можно добавить логгер, если потребуется: logging.getLogger(logger_name)
# Но пока оставим без явного логгера.


class SessionData(BaseModel):
    session_id: str = Field(description="Уникальный идентификатор сессии")
    user_id: str = Field(description="ID пользователя")
    start_time: datetime = Field(description="Время начала сессии")
    messages: List[dict] = Field(description="История сообщений в рамках этой сессии")
    plant_ids: List[str] = Field(description="Список ID растений, с которыми взаимодействовал пользователь")


class PlantRecord(BaseModel):
    plant_id: str = Field(description="ID растения в базе")
    added_date: datetime = Field(description="Дата добавления растения")
    last_diagnosis: datetime = Field(description="Дата последней диагностики")
    health_history: List[dict] = Field(description="История изменений здоровья (дата + значение)")


class WateringScheduleUser(BaseModel):
    frequency_days: int = Field(description="Интервал полива (в днях)")
    amount_ml: int = Field(description="Количество воды (в мл)")
    next_watering: datetime = Field(description="Дата/время следующего полива")
    indicators: List[str] = Field(description="Признаки, указывающие на необходимость полива")


@tool
async def save_user_session(user_id: str, session_data: SessionData) -> None:
    """
    Заглушка для сохранения сессии пользователя в базу.
    """
    # Здесь код для сохранения session_data в вашу БД
    return None


@tool
async def get_user_plant_history(user_id: str) -> List[PlantRecord]:
    """
    Заглушка для получения истории растений пользователя.
    """
    # В продакшене тут запрос к БД.
    now = datetime.now()
    dummy = PlantRecord(
        plant_id="example_plant",
        added_date=now,
        last_diagnosis=now,
        health_history=[{"date": now.isoformat(), "health_score": 7.5}],
    )
    return [dummy]


@tool
async def schedule_reminder(
    user_id: str,
    reminder_type: str,
    scheduled_time: datetime,
) -> None:
    """
    Заглушка для планирования напоминания пользователю.
    reminder_type может быть, например, 'watering', 'fertilizing' и т. д.
    """
    # Здесь код, который сохранит напоминание в очередь / cron / calendar
    return None


@tool
async def calculate_watering_schedule_user(
    plant_id: str,
    pot_size: str,
    humidity: float,
) -> WateringScheduleUser:
    """
    Альтернативная версия расчёта расписания полива в модуле user_management.
    Если он не нужен, можно удалить этот метод.
    """
    now = datetime.now()
    # Делаем грубую заглушку: полив раз в 7 дней по 200 мл
    return WateringScheduleUser(
        frequency_days=7,
        amount_ml=200,
        next_watering=now,
        indicators=["Сухая поверхность почвы", "Потеря тургора листьев"],
    )
