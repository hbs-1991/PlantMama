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


class ReminderInfo(BaseModel):
    """Reminder information."""
    
    reminder_id: str = Field(description="Unique reminder ID")
    reminder_type: str = Field(description="Type of reminder")
    scheduled_time: datetime = Field(description="When reminder is scheduled")
    plant_name: Optional[str] = Field(description="Associated plant name")
    status: str = Field(description="Reminder status")


@tool
async def save_user_session(user_id: str, session_data: SessionData) -> None:
    """
    Save user session data to database.
    
    Args:
        user_id: User identifier (telegram ID)
        session_data: Session data to save
    """
    try:
        async with get_db_session() as db:
            # Check if user exists, create if not
            user = await db.get(User, user_id)
            if not user:
                user = User(
                    telegram_id=user_id,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                await db.flush()
            
            # Create or update session
            session = await db.get(Session, session_data.session_id)
            if not session:
                session = Session(
                    id=session_data.session_id,
                    user_id=user.id,
                    start_time=session_data.start_time,
                    messages_count=len(session_data.messages),
                    tokens_used=session_data.tokens_used
                )
                db.add(session)
            else:
                session.messages_count = len(session_data.messages)
                session.tokens_used = session_data.tokens_used
                session.end_time = datetime.utcnow()
            
            # Save messages
            for msg_data in session_data.messages:
                message = Message(
                    session_id=session.id,
                    role=msg_data.get("role", "user"),
                    content=msg_data.get("content", ""),
                    has_image=msg_data.get("has_image", False),
                    image_url=msg_data.get("image_url"),
                    timestamp=msg_data.get("timestamp", datetime.utcnow()),
                    tokens_used=msg_data.get("tokens_used", 0)
                )
                db.add(message)
            
            await db.commit()
            logger.info(f"Saved session {session_data.session_id} for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error saving user session: {str(e)}", exc_info=True)
        raise


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
