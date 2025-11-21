"""
Database Schemas for Consciousness Work / Reality Creation App

Each Pydantic model represents a collection in MongoDB. The collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Intention(BaseModel):
    """Users capture clear intentions/goals they are committing to."""
    title: str = Field(..., min_length=2, max_length=140, description="Short, specific intention")
    why: Optional[str] = Field(None, max_length=500, description="Deeper reason/meaning")
    category: Optional[str] = Field(None, description="Area of life: health, career, love, etc.")
    target_date: Optional[datetime] = Field(None, description="Optional target date for intention")
    is_active: bool = Field(True, description="Whether this intention is currently active")


class Affirmation(BaseModel):
    """Affirmations that reinforce identity and desired states."""
    text: str = Field(..., min_length=2, max_length=200, description="Affirmation phrase in present tense")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional tags like confidence, money, love")
    intensity: Optional[int] = Field(3, ge=1, le=5, description="How resonant/powerful it feels now")


class Session(BaseModel):
    """Practice sessions users log after doing mental exercises."""
    intention_id: Optional[str] = Field(None, description="Related intention id as string")
    practice_type: str = Field("visualization", description="Type: visualization, scripting, SATS, breathwork, etc.")
    minutes: int = Field(..., ge=1, le=240, description="Duration in minutes")
    mood_before: Optional[int] = Field(None, ge=1, le=5, description="Mood before session (1-5)")
    mood_after: Optional[int] = Field(None, ge=1, le=5, description="Mood after session (1-5)")
    notes: Optional[str] = Field(None, max_length=1000, description="Insights or vivid details")
