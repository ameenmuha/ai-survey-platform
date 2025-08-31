from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class QuestionBase(BaseModel):
    survey_id: int
    question_text: str = Field(..., min_length=1, max_length=1000)
    question_type: str = Field(..., regex="^(text|multiple_choice|yes_no|rating|number|date|email|phone)$")
    order_number: int = Field(..., ge=1)
    is_required: bool = True
    is_conditional: bool = False
    conditional_logic: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    options_translations: Optional[Dict[str, List[str]]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    ai_clarification_enabled: bool = True
    clarification_prompts: Optional[Dict[str, str]] = None
    question_translations: Optional[Dict[str, str]] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    question_type: Optional[str] = Field(None, regex="^(text|multiple_choice|yes_no|rating|number|date|email|phone)$")
    order_number: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    is_conditional: Optional[bool] = None
    conditional_logic: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    options_translations: Optional[Dict[str, List[str]]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    ai_clarification_enabled: Optional[bool] = None
    clarification_prompts: Optional[Dict[str, str]] = None
    question_translations: Optional[Dict[str, str]] = None

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    translated_text: Optional[str] = None
    translated_options: Optional[List[str]] = None

    class Config:
        from_attributes = True

class QuestionList(BaseModel):
    questions: List[QuestionResponse]
    total: int
    skip: int
    limit: int

class QuestionValidation(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    question_id: int

class QuestionTranslation(BaseModel):
    language: str
    question_text: str
    options: Optional[List[str]] = None
    clarification_prompt: Optional[str] = None
