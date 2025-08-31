from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    
    # Question Content
    question_text = Column(Text, nullable=False)  # Default language text
    question_translations = Column(JSON, nullable=True)  # Translations in other languages
    question_type = Column(String(50), nullable=False)  # multiple_choice, text, yes_no, rating, etc.
    
    # Question Configuration
    order_number = Column(Integer, nullable=False)  # Question order in survey
    is_required = Column(Boolean, default=True)
    is_conditional = Column(Boolean, default=False)
    conditional_logic = Column(JSON, nullable=True)  # Logic for conditional questions
    
    # Options for multiple choice questions
    options = Column(JSON, nullable=True)  # List of options
    options_translations = Column(JSON, nullable=True)  # Translations of options
    
    # Validation
    validation_rules = Column(JSON, nullable=True)  # Validation rules
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    
    # AI Configuration
    ai_clarification_enabled = Column(Boolean, default=True)
    clarification_prompts = Column(JSON, nullable=True)  # AI prompts for clarification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    survey = relationship("Survey", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, text='{self.question_text[:50]}...', type='{self.question_type}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, question_id: int) -> Optional["Question"]:
        """Get question by ID"""
        result = await db.execute(select(cls).where(cls.id == question_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_questions(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        question_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List["Question"]:
        """Get questions with optional filtering"""
        query = select(cls)
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
        if question_type:
            query = query.where(cls.question_type == question_type)
        
        # If user_id is provided, filter by survey ownership
        if user_id:
            from app.models.survey import Survey
            query = query.join(Survey).where(Survey.created_by == user_id)
        
        query = query.order_by(cls.order_number).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def count_questions(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        question_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """Count questions with optional filtering"""
        from sqlalchemy import func as sql_func
        
        query = select(sql_func.count(cls.id))
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
        if question_type:
            query = query.where(cls.question_type == question_type)
        
        # If user_id is provided, filter by survey ownership
        if user_id:
            from app.models.survey import Survey
            query = query.join(Survey).where(Survey.created_by == user_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    @classmethod
    async def get_survey_questions_ordered(
        cls,
        db: AsyncSession,
        survey_id: int,
        language: str = "en"
    ) -> List["Question"]:
        """Get questions for a survey in order with translations"""
        result = await db.execute(
            select(cls)
            .where(cls.survey_id == survey_id)
            .order_by(cls.order_number)
        )
        questions = result.scalars().all()
        
        # Add translated text to each question
        for question in questions:
            question.translated_text = question.get_translated_text(language)
            question.translated_options = question.get_translated_options(language)
        
        return questions
    
    @classmethod
    async def get_by_survey(cls, db: AsyncSession, survey_id: int):
        """Get all questions for a survey ordered by order_number"""
        result = await db.execute(
            select(cls)
            .where(cls.survey_id == survey_id)
            .order_by(cls.order_number)
        )
        return result.scalars().all()
    
    @classmethod
    async def create_question(
        cls,
        db: AsyncSession,
        survey_id: int,
        question_text: str,
        question_type: str,
        order_number: int,
        question_translations: Dict[str, str] = None,
        is_required: bool = True,
        is_conditional: bool = False,
        conditional_logic: dict = None,
        options: List[str] = None,
        options_translations: Dict[str, List[str]] = None,
        validation_rules: dict = None,
        min_length: int = None,
        max_length: int = None,
        ai_clarification_enabled: bool = True,
        clarification_prompts: Dict[str, str] = None
    ) -> "Question":
        """Create a new question"""
        question = cls(
            survey_id=survey_id,
            question_text=question_text,
            question_type=question_type,
            order_number=order_number,
            question_translations=question_translations or {},
            is_required=is_required,
            is_conditional=is_conditional,
            conditional_logic=conditional_logic or {},
            options=options or [],
            options_translations=options_translations or {},
            validation_rules=validation_rules or {},
            min_length=min_length,
            max_length=max_length,
            ai_clarification_enabled=ai_clarification_enabled,
            clarification_prompts=clarification_prompts or {}
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question
    
    @classmethod
    async def update_question(cls, db: AsyncSession, question_id: int, **kwargs) -> Optional["Question"]:
        """Update question by ID"""
        question = await cls.get_by_id(db=db, question_id=question_id)
        if not question:
            return None
            
        for field, value in kwargs.items():
            if hasattr(question, field):
                setattr(question, field, value)
        
        await db.commit()
        await db.refresh(question)
        return question
    
    @classmethod
    async def delete_question(cls, db: AsyncSession, question_id: int) -> bool:
        """Delete question by ID"""
        question = await cls.get_by_id(db=db, question_id=question_id)
        if not question:
            return False
            
        await db.delete(question)
        await db.commit()
        return True
    
    @classmethod
    async def bulk_create_questions(
        cls,
        db: AsyncSession,
        survey_id: int,
        questions_data: List[dict]
    ) -> List["Question"]:
        """Bulk create questions"""
        questions = []
        for i, data in enumerate(questions_data):
            question = cls(
                survey_id=survey_id,
                question_text=data.get("question_text"),
                question_type=data.get("question_type", "text"),
                order_number=data.get("order_number", i + 1),
                question_translations=data.get("question_translations", {}),
                is_required=data.get("is_required", True),
                is_conditional=data.get("is_conditional", False),
                conditional_logic=data.get("conditional_logic", {}),
                options=data.get("options", []),
                options_translations=data.get("options_translations", {}),
                validation_rules=data.get("validation_rules", {}),
                min_length=data.get("min_length"),
                max_length=data.get("max_length"),
                ai_clarification_enabled=data.get("ai_clarification_enabled", True),
                clarification_prompts=data.get("clarification_prompts", {})
            )
            questions.append(question)
        
        db.add_all(questions)
        await db.commit()
        
        # Refresh all questions
        for question in questions:
            await db.refresh(question)
        
        return questions
    
    async def update_question(self, db: AsyncSession, **kwargs):
        """Update question fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    def get_translated_text(self, language: str) -> str:
        """Get question text in specified language"""
        if language in self.question_translations:
            return self.question_translations[language]
        return self.question_text
    
    def get_translated_options(self, language: str) -> List[str]:
        """Get options in specified language"""
        if language in self.options_translations:
            return self.options_translations[language]
        return self.options or []
    
    def get_clarification_prompt(self, language: str) -> str:
        """Get clarification prompt in specified language"""
        if language in self.clarification_prompts:
            return self.clarification_prompts[language]
        # Default clarification prompt
        return f"Could you please clarify your response to: {self.get_translated_text(language)}"
    
    def validate_response(self, response_text: str) -> tuple[bool, str]:
        """Validate response based on question rules"""
        if not response_text and self.is_required:
            return False, "This question is required"
        
        if response_text:
            if self.min_length and len(response_text) < self.min_length:
                return False, f"Response must be at least {self.min_length} characters"
            
            if self.max_length and len(response_text) > self.max_length:
                return False, f"Response must be no more than {self.max_length} characters"
        
        return True, "Valid response"
