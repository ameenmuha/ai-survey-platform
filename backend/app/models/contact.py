from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    
    # Contact Information
    phone_number = Column(String(20), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    preferred_language = Column(String(10), default="en")
    
    # Additional Data (from CSV upload)
    additional_data = Column(JSON, nullable=True)  # Store any additional columns from CSV
    
    # Call Status
    status = Column(String(50), default="pending")  # pending, scheduled, called, completed, failed
    call_attempts = Column(Integer, default=0)
    last_call_attempt = Column(DateTime(timezone=True), nullable=True)
    next_call_scheduled = Column(DateTime(timezone=True), nullable=True)
    
    # Call Results
    call_duration = Column(Integer, nullable=True)  # in seconds
    call_result = Column(String(50), nullable=True)  # answered, busy, no-answer, failed
    response_language = Column(String(10), nullable=True)  # detected language during call
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    survey = relationship("Survey", back_populates="contacts")
    responses = relationship("Response", back_populates="contact", cascade="all, delete-orphan")
    call_logs = relationship("CallLog", back_populates="contact", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, phone='{self.phone_number}', status='{self.status}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, contact_id: int) -> Optional["Contact"]:
        """Get contact by ID"""
        result = await db.execute(select(cls).where(cls.id == contact_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_contacts(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List["Contact"]:
        """Get contacts with optional filtering"""
        query = select(cls)
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
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
    async def count_contacts(
        cls,
        db: AsyncSession,
        survey_id: Optional[int] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """Count contacts with optional filtering"""
        from sqlalchemy import func as sql_func
        
        query = select(sql_func.count(cls.id))
        
        if survey_id:
            query = query.where(cls.survey_id == survey_id)
        if status:
            query = query.where(cls.status == status)
        
        # If user_id is provided, filter by survey ownership
        if user_id:
            from app.models.survey import Survey
            query = query.join(Survey).where(Survey.created_by == user_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    @classmethod
    async def get_survey_stats(cls, db: AsyncSession, survey_id: int) -> Dict:
        """Get contact statistics for a survey"""
        from sqlalchemy import func as sql_func
        
        # Get total contacts
        total_result = await db.execute(
            select(sql_func.count(cls.id)).where(cls.survey_id == survey_id)
        )
        total = total_result.scalar()
        
        # Get contacts by status
        status_result = await db.execute(
            select(cls.status, sql_func.count(cls.id))
            .where(cls.survey_id == survey_id)
            .group_by(cls.status)
        )
        status_counts = dict(status_result.all())
        
        # Get contacts by language
        language_result = await db.execute(
            select(cls.preferred_language, sql_func.count(cls.id))
            .where(cls.survey_id == survey_id)
            .group_by(cls.preferred_language)
        )
        language_counts = dict(language_result.all())
        
        return {
            "total_contacts": total,
            "status_distribution": status_counts,
            "language_distribution": language_counts,
            "pending_calls": status_counts.get("pending", 0),
            "completed_calls": status_counts.get("completed", 0),
            "failed_calls": status_counts.get("failed", 0)
        }
    
    @classmethod
    async def get_by_survey(cls, db: AsyncSession, survey_id: int, skip: int = 0, limit: int = 1000):
        """Get contacts for a survey"""
        result = await db.execute(
            select(cls)
            .where(cls.survey_id == survey_id)
            .order_by(cls.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_pending_contacts(cls, db: AsyncSession, survey_id: int):
        """Get contacts pending calls"""
        result = await db.execute(
            select(cls)
            .where(
                cls.survey_id == survey_id,
                cls.status.in_(["pending", "scheduled"]),
                cls.call_attempts < 3
            )
        )
        return result.scalars().all()
    
    @classmethod
    async def create_contact(
        cls,
        db: AsyncSession,
        survey_id: int,
        phone_number: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        preferred_language: str = "en",
        additional_data: dict = None
    ) -> "Contact":
        """Create a new contact"""
        contact = cls(
            survey_id=survey_id,
            phone_number=phone_number,
            name=name,
            email=email,
            preferred_language=preferred_language,
            additional_data=additional_data or {}
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    
    @classmethod
    async def update_contact(cls, db: AsyncSession, contact_id: int, **kwargs) -> Optional["Contact"]:
        """Update contact by ID"""
        contact = await cls.get_by_id(db=db, contact_id=contact_id)
        if not contact:
            return None
            
        for field, value in kwargs.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        
        await db.commit()
        await db.refresh(contact)
        return contact
    
    @classmethod
    async def delete_contact(cls, db: AsyncSession, contact_id: int) -> bool:
        """Delete contact by ID"""
        contact = await cls.get_by_id(db=db, contact_id=contact_id)
        if not contact:
            return False
            
        await db.delete(contact)
        await db.commit()
        return True
    
    @classmethod
    async def bulk_create_contacts(
        cls,
        db: AsyncSession,
        survey_id: int,
        contacts_data: List[dict]
    ) -> List["Contact"]:
        """Bulk create contacts from CSV data"""
        contacts = []
        for data in contacts_data:
            contact = cls(
                survey_id=survey_id,
                phone_number=data.get("phone_number"),
                name=data.get("name"),
                email=data.get("email"),
                preferred_language=data.get("preferred_language", "en"),
                additional_data={k: v for k, v in data.items() 
                               if k not in ["phone_number", "name", "email", "preferred_language"]}
            )
            contacts.append(contact)
        
        db.add_all(contacts)
        await db.commit()
        
        # Refresh all contacts
        for contact in contacts:
            await db.refresh(contact)
        
        return contacts
    
    async def update_contact(self, db: AsyncSession, **kwargs):
        """Update contact fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def schedule_call(self, db: AsyncSession, scheduled_time):
        """Schedule a call for this contact"""
        self.status = "scheduled"
        self.next_call_scheduled = scheduled_time
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_called(self, db: AsyncSession, call_result: str, duration: int = None):
        """Mark contact as called"""
        self.status = "called"
        self.call_attempts += 1
        self.last_call_attempt = func.now()
        self.call_result = call_result
        if duration:
            self.call_duration = duration
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_completed(self, db: AsyncSession):
        """Mark contact as completed"""
        self.status = "completed"
        await db.commit()
        await db.refresh(self)
        return self
    
    async def mark_failed(self, db: AsyncSession):
        """Mark contact as failed"""
        self.status = "failed"
        await db.commit()
        await db.refresh(self)
        return self
