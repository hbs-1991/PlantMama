"""User management tools."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from agents import function_tool
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


@function_tool
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


@function_tool
async def get_user_plant_history(user_id: str) -> List[PlantRecord]:
    """
    Retrieve user's plant history and records.
    
    Args:
        user_id: User identifier (telegram ID)
        
    Returns:
        List of plant records with their latest health status
    """
    try:
        async with get_db_session() as db:
            # Get user
            stmt = select(User).where(User.telegram_id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.info(f"No user found with telegram_id {user_id}")
                return []
            
            # Get user's plants
            stmt = select(Plant).where(Plant.user_id == user.id)
            result = await db.execute(stmt)
            plants = result.scalars().all()
            
            plant_records = []
            for plant in plants:
                # Get latest diagnosis for each plant
                stmt = (
                    select(Diagnosis)
                    .where(Diagnosis.plant_id == plant.id)
                    .order_by(desc(Diagnosis.created_at))
                    .limit(1)
                )
                result = await db.execute(stmt)
                latest_diagnosis = result.scalar_one_or_none()
                
                record = PlantRecord(
                    plant_id=str(plant.id),
                    species=plant.species or plant.name,
                    nickname=plant.nickname,
                    added_date=plant.added_at,
                    last_diagnosis=latest_diagnosis.created_at if latest_diagnosis else None,
                    health_score=latest_diagnosis.health_score if latest_diagnosis else plant.health_score,
                    location=plant.location,
                    care_notes=plant.notes
                )
                plant_records.append(record)
            
            logger.info(f"Retrieved {len(plant_records)} plants for user {user_id}")
            return plant_records
            
    except Exception as e:
        logger.error(f"Error retrieving plant history: {str(e)}", exc_info=True)
        return []


@tool
async def schedule_reminder(
    user_id: str,
    reminder_type: str,
    scheduled_time: datetime,
    plant_id: Optional[str] = None,
    description: Optional[str] = None
) -> ReminderInfo:
    """
    Schedule a care reminder for the user.
    
    Args:
        user_id: User identifier (telegram ID)
        reminder_type: Type of reminder (watering, fertilizing, pruning, etc.)
        scheduled_time: When to send the reminder
        plant_id: Optional plant ID this reminder is for
        description: Optional description for the reminder
        
    Returns:
        Created reminder information
    """
    try:
        async with get_db_session() as db:
            # Get user
            stmt = select(User).where(User.telegram_id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                # Create user if doesn't exist
                user = User(
                    telegram_id=user_id,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                await db.flush()
            
            # Create reminder
            reminder = Reminder(
                user_id=user.id,
                plant_id=int(plant_id) if plant_id else None,
                type=reminder_type,
                title=f"{reminder_type.capitalize()} reminder",
                description=description or f"Time to {reminder_type} your plant!",
                scheduled_at=scheduled_time,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(reminder)
            await db.commit()
            
            # Get plant name if plant_id provided
            plant_name = None
            if plant_id:
                plant = await db.get(Plant, int(plant_id))
                if plant:
                    plant_name = plant.nickname or plant.name
            
            logger.info(f"Scheduled {reminder_type} reminder for user {user_id} at {scheduled_time}")
            
            return ReminderInfo(
                reminder_id=str(reminder.id),
                reminder_type=reminder_type,
                scheduled_time=scheduled_time,
                plant_name=plant_name,
                status="pending"
            )
            
    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}", exc_info=True)
        # Return a basic reminder info even on error
        return ReminderInfo(
            reminder_id="error",
            reminder_type=reminder_type,
            scheduled_time=scheduled_time,
            plant_name=None,
            status="failed"
        )
