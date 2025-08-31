from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class Survey(Base):
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Survey Configuration
    primary_language = Column(String(10), default="en")  # en, hi, bn, etc.
    supported_languages = Column(JSON, default=["en"])  # List of supported languages
    max_questions = Column(Integer, default=20)
    estimated_duration = Column(Integer, default=10)  # in minutes
    
    # Call Configuration
    call_schedule = Column(JSON, nullable=True)  # Scheduling configuration
    retry_attempts = Column(Integer, default=3)
    retry_interval = Column(Integer, default=24)  # hours
    
    # AI Configuration
    ai_clarification_enabled = Column(Boolean, default=True)
    ai_summary_enabled = Column(Boolean, default=True)
    confidence_threshold = Column(Integer, default=70)  # percentage
    
    # Status
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    questions = relationship("Question", back_populates="survey", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="survey", cascade="all, delete-orphan")
    call_logs = relationship("CallLog", back_populates="survey", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Survey(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, survey_id: int) -> Optional["Survey"]:
        """Get survey by ID"""
        result = await db.execute(select(cls).where(cls.id == survey_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_user(cls, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
        """Get surveys created by a user"""
        result = await db.execute(
            select(cls)
            .where(cls.created_by == user_id)
            .order_by(cls.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_active_surveys(cls, db: AsyncSession):
        """Get all active surveys"""
        result = await db.execute(
            select(cls).where(cls.status == "active", cls.is_active == True)
        )
        return result.scalars().all()
    
    @classmethod
    async def create_survey(
        cls,
        db: AsyncSession,
        title: str,
        created_by: int,
        description: Optional[str] = None,
        primary_language: str = "en",
        supported_languages: List[str] = None,
        max_questions: int = 20,
        estimated_duration: int = 10,
        call_schedule: dict = None,
        retry_attempts: int = 3,
        retry_interval: int = 24,
        ai_clarification_enabled: bool = True,
        ai_summary_enabled: bool = True,
        confidence_threshold: int = 70
    ) -> "Survey":
        """Create a new survey"""
        if supported_languages is None:
            supported_languages = [primary_language]
            
        survey = cls(
            title=title,
            description=description,
            created_by=created_by,
            primary_language=primary_language,
            supported_languages=supported_languages,
            max_questions=max_questions,
            estimated_duration=estimated_duration,
            call_schedule=call_schedule,
            retry_attempts=retry_attempts,
            retry_interval=retry_interval,
            ai_clarification_enabled=ai_clarification_enabled,
            ai_summary_enabled=ai_summary_enabled,
            confidence_threshold=confidence_threshold
        )
        db.add(survey)
        await db.commit()
        await db.refresh(survey)
        return survey
    
    async def update_survey(self, db: AsyncSession, **kwargs):
        """Update survey fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def activate_survey(self, db: AsyncSession):
        """Activate a survey"""
        self.status = "active"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def pause_survey(self, db: AsyncSession):
        """Pause a survey"""
        self.status = "paused"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def complete_survey(self, db: AsyncSession):
        """Mark survey as completed"""
        self.status = "completed"
        self.completed_at = func.now()
        await db.commit()
        await db.refresh(self)
        return self
    
    async def get_statistics(self, db: AsyncSession) -> dict:
        """Get survey statistics"""
        from app.models.contact import Contact
        from app.models.response import Response
        
        # Get total contacts
        total_contacts = await db.execute(
            select(Contact).where(Contact.survey_id == self.id)
        )
        total_contacts = len(total_contacts.scalars().all())
        
        # Get completed calls
        completed_calls = await db.execute(
            select(Response).where(Response.survey_id == self.id, Response.status == "completed")
        )
        completed_calls = len(completed_calls.scalars().all())
        
        # Get response rate
        response_rate = (completed_calls / total_contacts * 100) if total_contacts > 0 else 0
        
        return {
            "total_contacts": total_contacts,
            "completed_calls": completed_calls,
            "response_rate": round(response_rate, 2),
            "status": self.status
        }
