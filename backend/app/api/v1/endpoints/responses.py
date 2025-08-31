from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.models.contact import Contact
from app.models.question import Question
from app.models.response import Response
from app.schemas.response import ResponseCreate, ResponseUpdate, ResponseResponse, ResponseList
from ai_service.ai_clarification import ai_clarification_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=ResponseList)
async def get_responses(
    survey_id: Optional[int] = Query(None),
    contact_id: Optional[int] = Query(None),
    question_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get responses with optional filtering"""
    try:
        responses = await Response.get_responses(
            db=db,
            survey_id=survey_id,
            contact_id=contact_id,
            question_id=question_id,
            status=status,
            skip=skip,
            limit=limit,
            user_id=current_user.id
        )
        
        total = await Response.count_responses(
            db=db,
            survey_id=survey_id,
            contact_id=contact_id,
            question_id=question_id,
            status=status,
            user_id=current_user.id
        )
        
        return ResponseList(
            responses=[ResponseResponse.model_validate(response) for response in responses],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch responses"
        )

@router.get("/{response_id}", response_model=ResponseResponse)
async def get_response(
    response_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get response by ID"""
    try:
        response = await Response.get_by_id(db=db, response_id=response_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Check if user has access to this response's survey
        survey = await Survey.get_by_id(db=db, survey_id=response.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return ResponseResponse.model_validate(response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching response {response_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch response"
        )

@router.post("/", response_model=ResponseResponse)
async def create_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new response"""
    try:
        # Verify survey exists and user has access
        survey = await Survey.get_by_id(db=db, survey_id=response_data.survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.created_by != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Verify contact exists
        contact = await Contact.get_by_id(db=db, contact_id=response_data.contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Verify question exists
        question = await Question.get_by_id(db=db, question_id=response_data.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        response = await Response.create_response(
            db=db,
            survey_id=response_data.survey_id,
            contact_id=response_data.contact_id,
            question_id=response_data.question_id,
            raw_response=response_data.raw_response,
            transcribed_text=response_data.transcribed_text,
            processed_response=response_data.processed_response,
            response_language=response_data.response_language,
            response_type=response_data.response_type,
            confidence_score=response_data.confidence_score,
            call_session_id=response_data.call_session_id,
            response_timestamp=response_data.response_timestamp,
            response_duration=response_data.response_duration,
            audio_quality_score=response_data.audio_quality_score,
            transcription_accuracy=response_data.transcription_accuracy
        )
        
        return ResponseResponse.model_validate(response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create response"
        )

@router.put("/{response_id}", response_model=ResponseResponse)
async def update_response(
    response_id: int,
    response_data: ResponseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update response information"""
    try:
        response = await Response.get_by_id(db=db, response_id=response_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Check if user has access to this response's survey
        survey = await Survey.get_by_id(db=db, survey_id=response.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        updated_response = await Response.update_response(
            db=db,
            response_id=response_id,
            **response_data.model_dump(exclude_unset=True)
        )
        
        return ResponseResponse.model_validate(updated_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating response {response_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update response"
        )

@router.delete("/{response_id}")
async def delete_response(
    response_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete response"""
    try:
        response = await Response.get_by_id(db=db, response_id=response_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Check if user has access to this response's survey
        survey = await Survey.get_by_id(db=db, survey_id=response.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        await Response.delete_response(db=db, response_id=response_id)
        
        return {"message": "Response deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting response {response_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete response"
        )

@router.post("/{response_id}/process")
async def process_response(
    response_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Process a response with AI clarification if needed"""
    try:
        response = await Response.get_by_id(db=db, response_id=response_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Check if user has access to this response's survey
        survey = await Survey.get_by_id(db=db, survey_id=response.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Get the question for context
        question = await Question.get_by_id(db=db, question_id=response.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Process the response
        processed_response = await Response.process_response_with_ai(
            db=db,
            response_id=response_id,
            question=question,
            ai_service=ai_clarification_service
        )
        
        return ResponseResponse.model_validate(processed_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing response {response_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process response"
        )

@router.get("/survey/{survey_id}/summary")
async def get_survey_responses_summary(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary of responses for a survey"""
    try:
        # Verify survey exists and user has access
        survey = await Survey.get_by_id(db=db, survey_id=survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.created_by != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        summary = await Response.get_survey_responses_summary(db=db, survey_id=survey_id)
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey responses summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch survey responses summary"
        )

@router.get("/contact/{contact_id}/responses")
async def get_contact_responses(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all responses for a specific contact"""
    try:
        contact = await Contact.get_by_id(db=db, contact_id=contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check if user has access to this contact's survey
        survey = await Survey.get_by_id(db=db, survey_id=contact.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        responses = await Response.get_contact_responses(db=db, contact_id=contact_id)
        
        return {
            "contact_id": contact_id,
            "responses": [ResponseResponse.model_validate(r) for r in responses]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact responses"
        )
