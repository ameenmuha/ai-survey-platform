from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class SurveyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    primary_language: str = Field(default="en", regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    supported_languages: List[str] = Field(default=["en"])
    max_questions: int = Field(default=20, ge=1, le=100)
    estimated_duration: int = Field(default=10, ge=1, le=60)  # minutes
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_interval: int = Field(default=24, ge=1, le=168)  # hours
    ai_clarification_enabled: bool = True
    ai_summary_enabled: bool = True
    confidence_threshold: int = Field(default=70, ge=0, le=100)

class SurveyCreate(SurveyBase):
    call_schedule: Optional[Dict] = None

class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    primary_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    supported_languages: Optional[List[str]] = None
    max_questions: Optional[int] = Field(None, ge=1, le=100)
    estimated_duration: Optional[int] = Field(None, ge=1, le=60)
    call_schedule: Optional[Dict] = None
    retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    retry_interval: Optional[int] = Field(None, ge=1, le=168)
    ai_clarification_enabled: Optional[bool] = None
    ai_summary_enabled: Optional[bool] = None
    confidence_threshold: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, regex="^(draft|active|paused|completed)$")

class SurveyResponse(SurveyBase):
    id: int
    created_by: int
    status: str
    is_active: bool
    call_schedule: Optional[Dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SurveyList(BaseModel):
    surveys: List[SurveyResponse]
    total: int
    page: int
    size: int
    pages: int

class SurveyStatistics(BaseModel):
    total_contacts: int
    completed_calls: int
    response_rate: float
    status: str
