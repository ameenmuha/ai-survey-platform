from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Call Information
    call_session_id = Column(String(255), unique=True, nullable=False)
    twilio_call_sid = Column(String(255), nullable=True)  # Twilio call identifier
    phone_number = Column(String(20), nullable=False)
    
    # Call Status
    status = Column(String(50), default="initiated")  # initiated, ringing, answered, completed, failed, busy, no-answer
    call_result = Column(String(50), nullable=True)  # answered, busy, no-answer, failed, completed
    
    # Call Duration and Timing
    call_duration = Column(Integer, nullable=True)  # Total call duration in seconds
    ring_duration = Column(Integer, nullable=True)  # Time spent ringing
    answer_duration = Column(Integer, nullable=True)  # Time from answer to hangup
    
    # Call Flow
    questions_asked = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    survey_completed = Column(Boolean, default=False)
    
    # Language and AI
    detected_language = Column(String(10), nullable=True)
    language_switches = Column(Integer, default=0)
    ai_clarifications_used = Column(Integer, default=0)
    
    # Quality Metrics
    audio_quality_score = Column(Float, nullable=True)
    connection_quality = Column(String(20), nullable=True)  # good, fair, poor
    
    # Error Information
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Call Metadata
    call_start_time = Column(DateTime(timezone=True), nullable=True)
    call_end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    survey = relationship("Survey", back_populates="call_logs")
    contact = relationship("Contact", back_populates="call_logs")
    
    def __repr__(self):
        return f"<CallLog(id={self.id}, session_id='{self.call_session_id}', status='{self.status}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, call_log_id: int) -> Optional["CallLog"]:
        """Get call log by ID"""
        result = await db.execute(select(cls).where(cls.id == call_log_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_session_id(cls, db: AsyncSession, session_id: str) -> Optional["CallLog"]:
        """Get call log by session ID"""
        result = await db.execute(select(cls).where(cls.call_session_id == session_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_survey(cls, db: AsyncSession, survey_id: int, skip: int = 0, limit: int = 1000):
        """Get call logs for a survey"""
        result = await db.execute(
            select(cls)
            .where(cls.survey_id == survey_id)
            .order_by(cls.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_contact(cls, db: AsyncSession, contact_id: int):
        """Get call logs for a contact"""
        result = await db.execute(
            select(cls)
            .where(cls.contact_id == contact_id)
            .order_by(cls.created_at.desc())
        )
        return result.scalars().all()
    
    @classmethod
    async def create_call_log(
        cls,
        db: AsyncSession,
        survey_id: int,
        contact_id: int,
        call_session_id: str,
        phone_number: str,
        twilio_call_sid: str = None
    ) -> "CallLog":
        """Create a new call log"""
        call_log = cls(
            survey_id=survey_id,
            contact_id=contact_id,
            call_session_id=call_session_id,
            phone_number=phone_number,
            twilio_call_sid=twilio_call_sid,
            call_start_time=func.now()
        )
        db.add(call_log)
        await db.commit()
        await db.refresh(call_log)
        return call_log
    
    async def update_call_log(self, db: AsyncSession, **kwargs):
        """Update call log fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_answered(self, db: AsyncSession):
        """Mark call as answered"""
        self.status = "answered"
        self.call_result = "answered"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_completed(self, db: AsyncSession, duration: int = None):
        """Mark call as completed"""
        self.status = "completed"
        self.call_result = "completed"
        self.survey_completed = True
        self.call_end_time = func.now()
        if duration:
            self.call_duration = duration
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_failed(self, db: AsyncSession, error_code: str = None, error_message: str = None):
        """Mark call as failed"""
        self.status = "failed"
        self.call_result = "failed"
        self.call_end_time = func.now()
        self.error_code = error_code
        self.error_message = error_message
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_busy(self, db: AsyncSession):
        """Mark call as busy"""
        self.status = "failed"
        self.call_result = "busy"
        self.call_end_time = func.now()
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_no_answer(self, db: AsyncSession):
        """Mark call as no answer"""
        self.status = "failed"
        self.call_result = "no-answer"
        self.call_end_time = func.now()
        await db.commit()
        await db.refresh(self)
        return self
    
    async def increment_questions_asked(self, db: AsyncSession):
        """Increment questions asked counter"""
        self.questions_asked += 1
        await db.commit()
        await db.refresh(self)
        return self
    
    async def increment_questions_answered(self, db: AsyncSession):
        """Increment questions answered counter"""
        self.questions_answered += 1
        await db.commit()
        await db.refresh(self)
        return self
    
    async def increment_ai_clarifications(self, db: AsyncSession):
        """Increment AI clarifications counter"""
        self.ai_clarifications_used += 1
        await db.commit()
        await db.refresh(self)
        return self
    
    def get_call_summary(self) -> dict:
        """Get a summary of the call"""
        return {
            "id": self.id,
            "session_id": self.call_session_id,
            "phone_number": self.phone_number,
            "status": self.status,
            "call_result": self.call_result,
            "duration": self.call_duration,
            "questions_asked": self.questions_asked,
            "questions_answered": self.questions_answered,
            "survey_completed": self.survey_completed,
            "ai_clarifications": self.ai_clarifications_used,
            "detected_language": self.detected_language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "call_start_time": self.call_start_time.isoformat() if self.call_start_time else None,
            "call_end_time": self.call_end_time.isoformat() if self.call_end_time else None
        }
