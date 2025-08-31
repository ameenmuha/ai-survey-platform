from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CallLogBase(BaseModel):
    survey_id: int
    contact_id: int
    call_session_id: str = Field(..., min_length=1, max_length=255)
    twilio_call_sid: Optional[str] = Field(None, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=20)
    status: str = Field(default="initiated", regex="^(initiated|ringing|answered|completed|failed|busy|no-answer)$")
    call_result: Optional[str] = Field(None, regex="^(answered|busy|no-answer|failed|completed)$")
    call_duration: Optional[int] = Field(None, ge=0)
    ring_duration: Optional[int] = Field(None, ge=0)
    answer_duration: Optional[int] = Field(None, ge=0)
    questions_asked: int = Field(default=0, ge=0)
    questions_answered: int = Field(default=0, ge=0)
    survey_completed: bool = False
    detected_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    language_switches: int = Field(default=0, ge=0)
    ai_clarifications_used: int = Field(default=0, ge=0)
    audio_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    connection_quality: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    error_code: Optional[str] = Field(None, max_length=50)
    error_message: Optional[str] = None
    call_start_time: Optional[datetime] = None
    call_end_time: Optional[datetime] = None

class CallLogCreate(CallLogBase):
    pass

class CallLogUpdate(BaseModel):
    status: Optional[str] = Field(None, regex="^(initiated|ringing|answered|completed|failed|busy|no-answer)$")
    call_result: Optional[str] = Field(None, regex="^(answered|busy|no-answer|failed|completed)$")
    call_duration: Optional[int] = Field(None, ge=0)
    ring_duration: Optional[int] = Field(None, ge=0)
    answer_duration: Optional[int] = Field(None, ge=0)
    questions_asked: Optional[int] = Field(None, ge=0)
    questions_answered: Optional[int] = Field(None, ge=0)
    survey_completed: Optional[bool] = None
    detected_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    language_switches: Optional[int] = Field(None, ge=0)
    ai_clarifications_used: Optional[int] = Field(None, ge=0)
    audio_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    connection_quality: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    error_code: Optional[str] = Field(None, max_length=50)
    error_message: Optional[str] = None
    call_start_time: Optional[datetime] = None
    call_end_time: Optional[datetime] = None

class CallLogResponse(CallLogBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CallLogList(BaseModel):
    call_logs: List[CallLogResponse]
    total: int
    skip: int
    limit: int

class CallLogStats(BaseModel):
    total_calls: int
    completed_calls: int
    failed_calls: int
    busy_calls: int
    no_answer_calls: int
    average_call_duration: Optional[float] = None
    average_ring_duration: Optional[float] = None
    completion_rate: float
    language_distribution: Dict[str, int]
    ai_clarifications_total: int
    average_questions_asked: float
    average_questions_answered: float

class CallQualityMetrics(BaseModel):
    audio_quality_average: Optional[float] = None
    connection_quality_distribution: Dict[str, int]
    error_rate: float
    successful_calls_percentage: float
