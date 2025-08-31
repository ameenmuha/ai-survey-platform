from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response Data
    raw_response = Column(Text, nullable=True)  # Original audio/voice response
    transcribed_text = Column(Text, nullable=True)  # STT transcribed text
    processed_response = Column(Text, nullable=True)  # AI processed/cleaned response
    response_language = Column(String(10), nullable=True)  # Detected language
    
    # Response Metadata
    response_type = Column(String(50), nullable=False)  # text, audio, multiple_choice, etc.
    confidence_score = Column(Float, nullable=True)  # AI confidence in response
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # AI Processing
    ai_clarification_used = Column(Boolean, default=False)
    clarification_attempts = Column(Integer, default=0)
    clarification_history = Column(JSON, nullable=True)  # History of clarification attempts
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights about response
    
    # Call Context
    call_session_id = Column(String(255), nullable=True)  # Unique call session identifier
    response_timestamp = Column(DateTime(timezone=True), nullable=True)  # When response was given
    response_duration = Column(Integer, nullable=True)  # Response duration in seconds
    
    # Quality Metrics
    audio_quality_score = Column(Float, nullable=True)  # Audio quality assessment
    transcription_accuracy = Column(Float, nullable=True)  # STT accuracy score
    
    # Status
    status = Column(String(50), default="pending")  # pending, completed, failed, needs_clarification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    survey = relationship("Survey", back_populates="responses")
    contact = relationship("Contact", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(id={self.id}, question_id={self.question_id}, status='{self.status}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, response_id: int) -> Optional["Response"]:
        """Get response by ID"""
        result = await db.execute(select(cls).where(cls.id == response_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_responses(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        question_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List["Response"]:
        """Get responses with optional filtering"""
        query = select(cls)
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
        if contact_id:
            query = query.where(cls.contact_id == contact_id)
        if question_id:
            query = query.where(cls.question_id == question_id)
        if status:
            query = query.where(cls.status == status)
        
        # If user_id is provided, filter by survey ownership
        if user_id:
            from app.models.survey import Survey
            query = query.join(Survey).where(Survey.created_by == user_id)
        
        query = query.order_by(cls.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def count_responses(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        question_id: Optional[int] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """Count responses with optional filtering"""
        from sqlalchemy import func as sql_func
        
        query = select(sql_func.count(cls.id))
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
        if contact_id:
            query = query.where(cls.contact_id == contact_id)
        if question_id:
            query = query.where(cls.question_id == question_id)
        if status:
            query = query.where(cls.status == status)
        
        # If user_id is provided, filter by survey ownership
        if user_id:
            from app.models.survey import Survey
            query = query.join(Survey).where(Survey.created_by == user_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    @classmethod
    async def get_survey_responses_summary(cls, db: AsyncSession, survey_id: int) -> Dict[str, Any]:
        """Get summary of responses for a survey"""
        from sqlalchemy import func as sql_func
        
        # Get total responses
        total_result = await db.execute(
            select(sql_func.count(cls.id)).where(cls.survey_id == survey_id)
        )
        total = total_result.scalar()
        
        # Get responses by status
        status_result = await db.execute(
            select(cls.status, sql_func.count(cls.id))
            .where(cls.survey_id == survey_id)
            .group_by(cls.status)
        )
        status_counts = dict(status_result.all())
        
        # Get responses by language
        language_result = await db.execute(
            select(cls.response_language, sql_func.count(cls.id))
            .where(cls.survey_id == survey_id)
            .group_by(cls.response_language)
        )
        language_counts = dict(language_result.all())
        
        # Get average confidence score
        confidence_result = await db.execute(
            select(sql_func.avg(cls.confidence_score))
            .where(cls.survey_id == survey_id, cls.confidence_score.isnot(None))
        )
        avg_confidence = confidence_result.scalar()
        
        return {
            "total_responses": total,
            "status_distribution": status_counts,
            "language_distribution": language_counts,
            "average_confidence": float(avg_confidence) if avg_confidence else None,
            "completed_responses": status_counts.get("completed", 0),
            "pending_responses": status_counts.get("pending", 0),
            "failed_responses": status_counts.get("failed", 0)
        }
    
    @classmethod
    async def get_contact_responses(cls, db: AsyncSession, contact_id: int) -> List["Response"]:
        """Get all responses for a contact"""
        result = await db.execute(
            select(cls)
            .where(cls.contact_id == contact_id)
            .order_by(cls.created_at)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_survey(cls, db: AsyncSession, survey_id: int, skip: int = 0, limit: int = 1000):
        """Get all responses for a survey"""
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
        """Get all responses for a contact"""
        result = await db.execute(
            select(cls)
            .where(cls.contact_id == contact_id)
            .order_by(cls.created_at)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_question(cls, db: AsyncSession, question_id: int):
        """Get all responses for a question"""
        result = await db.execute(
            select(cls)
            .where(cls.question_id == question_id)
            .order_by(cls.created_at)
        )
        return result.scalars().all()
    
    @classmethod
    async def create_response(
        cls,
        db: AsyncSession,
        survey_id: int,
        contact_id: int,
        question_id: int,
        raw_response: str = None,
        transcribed_text: str = None,
        processed_response: str = None,
        response_language: str = None,
        response_type: str = "text",
        confidence_score: float = None,
        call_session_id: str = None,
        response_timestamp = None,
        response_duration: int = None,
        audio_quality_score: float = None,
        transcription_accuracy: float = None
    ) -> "Response":
        """Create a new response"""
        response = cls(
            survey_id=survey_id,
            contact_id=contact_id,
            question_id=question_id,
            raw_response=raw_response,
            transcribed_text=transcribed_text,
            processed_response=processed_response,
            response_language=response_language,
            response_type=response_type,
            confidence_score=confidence_score,
            call_session_id=call_session_id,
            response_timestamp=response_timestamp or func.now(),
            response_duration=response_duration,
            audio_quality_score=audio_quality_score,
            transcription_accuracy=transcription_accuracy
        )
        db.add(response)
        await db.commit()
        await db.refresh(response)
        return response
    
    @classmethod
    async def update_response(cls, db: AsyncSession, response_id: int, **kwargs) -> Optional["Response"]:
        """Update response by ID"""
        response = await cls.get_by_id(db=db, response_id=response_id)
        if not response:
            return None
            
        for field, value in kwargs.items():
            if hasattr(response, field):
                setattr(response, field, value)
        
        await db.commit()
        await db.refresh(response)
        return response
    
    @classmethod
    async def delete_response(cls, db: AsyncSession, response_id: int) -> bool:
        """Delete response by ID"""
        response = await cls.get_by_id(db=db, response_id=response_id)
        if not response:
            return False
            
        await db.delete(response)
        await db.commit()
        return True
    
    @classmethod
    async def process_response_with_ai(
        cls,
        db: AsyncSession,
        response_id: int,
        question: "Question",
        ai_service: Any
    ) -> "Response":
        """Process a response with AI clarification if needed"""
        response = await cls.get_by_id(db=db, response_id=response_id)
        if not response:
            raise ValueError("Response not found")
        
        # Get the response text to process
        response_text = response.get_best_response_text()
        if not response_text:
            await response.mark_failed(db, "No response text available")
            return response
        
        try:
            # Process with AI clarification
            clarified_text, confidence, insights = await ai_service.clarify_response(
                response_text=response_text,
                question_text=question.question_text,
                question_type=question.question_type,
                language=response.response_language or "en",
                context={"survey_id": response.survey_id, "contact_id": response.contact_id}
            )
            
            # Update response with processed data
            response.processed_response = clarified_text
            response.confidence_score = confidence
            response.ai_insights = insights
            response.processing_status = "completed"
            response.status = "completed"
            response.processed_at = func.now()
            
            if confidence < 0.7:  # Low confidence threshold
                response.status = "needs_clarification"
                response.ai_clarification_used = True
            
            await db.commit()
            await db.refresh(response)
            
        except Exception as e:
            logger.error(f"AI processing failed for response {response_id}: {e}")
            await response.mark_failed(db, f"AI processing failed: {str(e)}")
        
        return response
    
    async def update_response(self, db: AsyncSession, **kwargs):
        """Update response fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def set_transcription(self, db: AsyncSession, transcribed_text: str, confidence: float = None):
        """Set transcribed text from STT"""
        self.transcribed_text = transcribed_text
        self.confidence_score = confidence
        self.processing_status = "transcribed"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def set_processed_response(self, db: AsyncSession, processed_text: str, language: str = None):
        """Set AI processed response"""
        self.processed_response = processed_text
        self.response_language = language
        self.processing_status = "completed"
        self.processed_at = func.now()
        self.status = "completed"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def add_clarification_attempt(self, db: AsyncSession, clarification_text: str, ai_response: str):
        """Add a clarification attempt"""
        if not self.clarification_history:
            self.clarification_history = []
        
        self.clarification_history.append({
            "timestamp": func.now().isoformat(),
            "clarification_text": clarification_text,
            "ai_response": ai_response
        })
        self.clarification_attempts += 1
        self.ai_clarification_used = True
        await db.commit()
        await db.refresh(self)
        return self
    
    async def set_ai_insights(self, db: AsyncSession, insights: dict):
        """Set AI-generated insights"""
        self.ai_insights = insights
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_failed(self, db: AsyncSession, error_message: str = None):
        """Mark response as failed"""
        self.status = "failed"
        self.processing_status = "failed"
        if error_message:
            if not self.ai_insights:
                self.ai_insights = {}
            self.ai_insights["error"] = error_message
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_needs_clarification(self, db: AsyncSession):
        """Mark response as needing clarification"""
        self.status = "needs_clarification"
        await db.commit()
        await db.refresh(self)
        return self
    
    def get_best_response_text(self) -> str:
        """Get the best available response text"""
        if self.processed_response:
            return self.processed_response
        elif self.transcribed_text:
            return self.transcribed_text
        elif self.raw_response:
            return self.raw_response
        return ""
    
    def get_response_summary(self) -> dict:
        """Get a summary of the response"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "response_text": self.get_best_response_text(),
            "language": self.response_language,
            "confidence": self.confidence_score,
            "status": self.status,
            "ai_clarification_used": self.ai_clarification_used,
            "clarification_attempts": self.clarification_attempts,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
