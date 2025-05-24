"""Database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default="en")
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    plants = relationship("Plant", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")


class Plant(Base):
    """Plant model."""
    
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    species = Column(String(200), nullable=True)
    scientific_name = Column(String(200), nullable=True)
    nickname = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)
    location = Column(String(100), nullable=True)
    pot_size = Column(String(50), nullable=True)
    soil_type = Column(String(100), nullable=True)
    last_watered = Column(DateTime, nullable=True)
    last_fertilized = Column(DateTime, nullable=True)
    health_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="plants")
    diagnoses = relationship("Diagnosis", back_populates="plant", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="plant", cascade="all, delete-orphan")


class Session(Base):
    """Session model."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    messages_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Message model."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    has_image = Column(Boolean, default=False)
    image_url = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)
    
    # Relationships
    session = relationship("Session", back_populates="messages")


class Diagnosis(Base):
    """Diagnosis model."""
    
    __tablename__ = "diagnoses"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    image_url = Column(String(500), nullable=True)
    health_score = Column(Float, nullable=False)
    issues = Column(JSON, default=[])
    severity = Column(String(20), nullable=False)  # mild, moderate, severe
    recommendations = Column(JSON, default=[])
    confidence = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plant = relationship("Plant", back_populates="diagnoses")


class Reminder(Base):
    """Reminder model."""
    
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    type = Column(String(50), nullable=False)  # watering, fertilizing, pruning, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending, sent, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    plant = relationship("Plant", back_populates="reminders")
