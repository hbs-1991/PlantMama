"""User management tools."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from agents import tool
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.connection import get_db_session
from database.models import User, Plant, Session, Message, Diagnosis, Reminder

logger = logging.getLogger(__name__)


class SessionData(BaseModel):
    """User session data."""
    
    session_id: str = Field(description="Unique session identifier")
    user_id: str = Field(description="User identifier")
    start_time: datetime = Field(description="Session start timestamp")
    messages: List[dict] = Field(description="List of messages in session")
    plant_ids: List[str] = Field(description="Plants discussed in session")
    tokens_used: int = Field(description="Total tokens used")


class PlantRecord(BaseModel):
    """User's plant record."""
    
    plant_id: str = Field(description="Unique plant identifier")
    species: str = Field(description="Plant species name")
    nickname: Optional[str] = Field(description="User's nickname for plant")
    added_date: datetime = Field(description="When plant was added")
    last_diagnosis: Optional[datetime] = Field(description="Last diagnosis date")
    health_score: Optional[float] = Field(description="Current health score")
    location: Optional[str] = Field(description="Where plant is located")
    care_notes: Optional[str] = Field(description="Care notes")


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
