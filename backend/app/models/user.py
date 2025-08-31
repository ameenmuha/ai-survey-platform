from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.security import get_password_hash
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="surveyor")  # surveyor, admin, analyst
    organization = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        result = await db.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Optional["User"]:
        """Get user by email"""
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()
    
    @classmethod
    async def create_user(
        cls, 
        db: AsyncSession, 
        email: str, 
        full_name: str, 
        password: str,
        role: str = "surveyor",
        organization: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> "User":
        """Create a new user"""
        hashed_password = get_password_hash(password)
        user = cls(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            organization=organization,
            phone_number=phone_number
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @classmethod
    async def get_users(
        cls, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[str] = None,
        organization: Optional[str] = None
    ) -> List["User"]:
        """Get users with optional filtering"""
        query = select(cls)
        
        if role:
            query = query.where(cls.role == role)
        if organization:
            query = query.where(cls.organization == organization)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def count_users(
        cls, 
        db: AsyncSession,
        role: Optional[str] = None,
        organization: Optional[str] = None
    ) -> int:
        """Count users with optional filtering"""
        from sqlalchemy import func as sql_func
        
        query = select(sql_func.count(cls.id))
        
        if role:
            query = query.where(cls.role == role)
        if organization:
            query = query.where(cls.organization == organization)
            
        result = await db.execute(query)
        return result.scalar()
    
    @classmethod
    async def get_all_users(cls, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all users with pagination"""
        result = await db.execute(
            select(cls).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, **kwargs) -> Optional["User"]:
        """Update user by ID"""
        user = await cls.get_by_id(db=db, user_id=user_id)
        if not user:
            return None
            
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: int) -> bool:
        """Delete user by ID"""
        user = await cls.get_by_id(db=db, user_id=user_id)
        if not user:
            return False
            
        await db.delete(user)
        await db.commit()
        return True
    
    async def update_user(self, db: AsyncSession, **kwargs):
        """Update user fields"""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def delete_user(self, db: AsyncSession):
        """Delete user"""
        await db.delete(self)
        await db.commit()
