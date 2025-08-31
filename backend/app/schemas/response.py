from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResponseBase(BaseModel):
    survey_id: int
    contact_id: int
    question_id: int
    raw_response: Optional[str] = None
    transcribed_text: Optional[str] = None
    processed_response: Optional[str] = None
    response_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    response_type: str = Field(default="text", regex="^(text|audio|multiple_choice|yes_no|rating|number)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    call_session_id: Optional[str] = None
    response_timestamp: Optional[datetime] = None
    response_duration: Optional[int] = Field(None, ge=0)
    audio_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    transcription_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(BaseModel):
    raw_response: Optional[str] = None
    transcribed_text: Optional[str] = None
    processed_response: Optional[str] = None
    response_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    response_type: Optional[str] = Field(None, regex="^(text|audio|multiple_choice|yes_no|rating|number)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_status: Optional[str] = Field(None, regex="^(pending|processing|completed|failed)$")
    ai_clarification_used: Optional[bool] = None
    clarification_attempts: Optional[int] = Field(None, ge=0)
    clarification_history: Optional[Dict[str, Any]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    call_session_id: Optional[str] = None
    response_timestamp: Optional[datetime] = None
    response_duration: Optional[int] = Field(None, ge=0)
    audio_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    transcription_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[str] = Field(None, regex="^(pending|completed|failed|needs_clarification)$")

class ResponseResponse(ResponseBase):
    id: int
    processing_status: str
    ai_clarification_used: bool
    clarification_attempts: int
    clarification_history: Optional[Dict[str, Any]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResponseList(BaseModel):
    responses: List[ResponseResponse]
    total: int
    skip: int
    limit: int

class ResponseSummary(BaseModel):
    id: int
    question_id: int
    response_text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    status: str
    ai_clarification_used: bool
    clarification_attempts: int
    created_at: datetime

class ResponseProcessing(BaseModel):
    response_id: int
    processed_text: str
    confidence_score: float
    ai_insights: Optional[Dict[str, Any]] = None
    needs_clarification: bool = False

class SurveyResponsesSummary(BaseModel):
    total_responses: int
    status_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    average_confidence: Optional[float] = None
    completed_responses: int
    pending_responses: int
    failed_responses: int
