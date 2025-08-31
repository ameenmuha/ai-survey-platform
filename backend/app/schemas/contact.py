from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ContactBase(BaseModel):
    survey_id: int
    phone_number: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    preferred_language: str = Field(default="en", regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    additional_data: Optional[Dict[str, Any]] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    preferred_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")
    additional_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, regex="^(pending|scheduled|called|completed|failed)$")
    call_attempts: Optional[int] = Field(None, ge=0)
    call_result: Optional[str] = Field(None, regex="^(answered|busy|no-answer|failed)$")
    response_language: Optional[str] = Field(None, regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$")

class ContactResponse(ContactBase):
    id: int
    status: str
    call_attempts: int
    last_call_attempt: Optional[datetime] = None
    next_call_scheduled: Optional[datetime] = None
    call_duration: Optional[int] = None
    call_result: Optional[str] = None
    response_language: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContactList(BaseModel):
    contacts: List[ContactResponse]
    total: int
    skip: int
    limit: int

class ContactUpload(BaseModel):
    survey_id: int
    file_url: Optional[str] = None
    total_contacts: int
    uploaded_at: datetime

class ContactStats(BaseModel):
    total_contacts: int
    status_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    pending_calls: int
    completed_calls: int
    failed_calls: int
