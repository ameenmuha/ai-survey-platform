from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.models.contact import Contact
from app.models.call_log import CallLog
from app.schemas.call_log import CallLogCreate, CallLogUpdate, CallLogResponse, CallLogList

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=CallLogList)
async def get_call_logs(
    survey_id: Optional[int] = Query(None),
    contact_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    call_result: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get call logs with optional filtering"""
    try:
        call_logs = await CallLog.get_call_logs(
            db=db,
            survey_id=survey_id,
            contact_id=contact_id,
            status=status,
            call_result=call_result,
            skip=skip,
            limit=limit,
            user_id=current_user.id
        )
        
        total = await CallLog.count_call_logs(
            db=db,
            survey_id=survey_id,
            contact_id=contact_id,
            status=status,
            call_result=call_result,
            user_id=current_user.id
        )
        
        return CallLogList(
            call_logs=[CallLogResponse.model_validate(call_log) for call_log in call_logs],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching call logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch call logs"
        )

@router.get("/{call_log_id}", response_model=CallLogResponse)
async def get_call_log(
    call_log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get call log by ID"""
    try:
        call_log = await CallLog.get_by_id(db=db, call_log_id=call_log_id)
        if not call_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call log not found"
            )
        
        # Check if user has access to this call log's survey
        survey = await Survey.get_by_id(db=db, survey_id=call_log.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return CallLogResponse.model_validate(call_log)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call log {call_log_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch call log"
        )

@router.post("/", response_model=CallLogResponse)
async def create_call_log(
    call_log_data: CallLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new call log"""
    try:
        # Verify survey exists and user has access
        survey = await Survey.get_by_id(db=db, survey_id=call_log_data.survey_id)
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
        contact = await Contact.get_by_id(db=db, contact_id=call_log_data.contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        call_log = await CallLog.create_call_log(
            db=db,
            survey_id=call_log_data.survey_id,
            contact_id=call_log_data.contact_id,
            call_session_id=call_log_data.call_session_id,
            twilio_call_sid=call_log_data.twilio_call_sid,
            phone_number=call_log_data.phone_number,
            status=call_log_data.status,
            call_result=call_log_data.call_result,
            call_duration=call_log_data.call_duration,
            ring_duration=call_log_data.ring_duration,
            answer_duration=call_log_data.answer_duration,
            questions_asked=call_log_data.questions_asked,
            questions_answered=call_log_data.questions_answered,
            survey_completed=call_log_data.survey_completed,
            detected_language=call_log_data.detected_language,
            language_switches=call_log_data.language_switches,
            ai_clarifications_used=call_log_data.ai_clarifications_used,
            audio_quality_score=call_log_data.audio_quality_score,
            connection_quality=call_log_data.connection_quality,
            error_code=call_log_data.error_code,
            error_message=call_log_data.error_message,
            call_start_time=call_log_data.call_start_time,
            call_end_time=call_log_data.call_end_time
        )
        
        return CallLogResponse.model_validate(call_log)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating call log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create call log"
        )

@router.put("/{call_log_id}", response_model=CallLogResponse)
async def update_call_log(
    call_log_id: int,
    call_log_data: CallLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update call log information"""
    try:
        call_log = await CallLog.get_by_id(db=db, call_log_id=call_log_id)
        if not call_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call log not found"
            )
        
        # Check if user has access to this call log's survey
        survey = await Survey.get_by_id(db=db, survey_id=call_log.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        updated_call_log = await CallLog.update_call_log(
            db=db,
            call_log_id=call_log_id,
            **call_log_data.model_dump(exclude_unset=True)
        )
        
        return CallLogResponse.model_validate(updated_call_log)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating call log {call_log_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update call log"
        )

@router.delete("/{call_log_id}")
async def delete_call_log(
    call_log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete call log"""
    try:
        call_log = await CallLog.get_by_id(db=db, call_log_id=call_log_id)
        if not call_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call log not found"
            )
        
        # Check if user has access to this call log's survey
        survey = await Survey.get_by_id(db=db, survey_id=call_log.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        await CallLog.delete_call_log(db=db, call_log_id=call_log_id)
        
        return {"message": "Call log deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting call log {call_log_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete call log"
        )

@router.get("/survey/{survey_id}/stats")
async def get_survey_call_stats(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get call statistics for a survey"""
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
        
        stats = await CallLog.get_survey_call_stats(db=db, survey_id=survey_id)
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey call stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch survey call statistics"
        )

@router.get("/contact/{contact_id}/calls")
async def get_contact_call_history(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get call history for a specific contact"""
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
        
        call_logs = await CallLog.get_contact_call_history(db=db, contact_id=contact_id)
        
        return {
            "contact_id": contact_id,
            "call_logs": [CallLogResponse.model_validate(call_log) for call_log in call_logs]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact call history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact call history"
        )

@router.post("/{call_log_id}/update-status")
async def update_call_status(
    call_log_id: int,
    status: str,
    call_result: Optional[str] = None,
    call_duration: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update call status and result"""
    try:
        call_log = await CallLog.get_by_id(db=db, call_log_id=call_log_id)
        if not call_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call log not found"
            )
        
        # Check if user has access to this call log's survey
        survey = await Survey.get_by_id(db=db, survey_id=call_log.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        updated_call_log = await CallLog.update_call_status(
            db=db,
            call_log_id=call_log_id,
            status=status,
            call_result=call_result,
            call_duration=call_duration
        )
        
        return CallLogResponse.model_validate(updated_call_log)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating call status {call_log_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update call status"
        )
