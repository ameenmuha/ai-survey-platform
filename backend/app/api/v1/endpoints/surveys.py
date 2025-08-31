from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyResponse, SurveyList, SurveyStatistics
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=SurveyResponse)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new survey"""
    try:
        survey = await Survey.create_survey(
            db=db,
            title=survey_data.title,
            created_by=current_user.id,
            description=survey_data.description,
            primary_language=survey_data.primary_language,
            supported_languages=survey_data.supported_languages,
            max_questions=survey_data.max_questions,
            estimated_duration=survey_data.estimated_duration,
            call_schedule=survey_data.call_schedule,
            retry_attempts=survey_data.retry_attempts,
            retry_interval=survey_data.retry_interval,
            ai_clarification_enabled=survey_data.ai_clarification_enabled,
            ai_summary_enabled=survey_data.ai_summary_enabled,
            confidence_threshold=survey_data.confidence_threshold
        )
        return SurveyResponse.model_validate(survey)
    except Exception as e:
        logger.error(f"Survey creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create survey"
        )

@router.get("/", response_model=SurveyList)
async def get_surveys(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get surveys for current user"""
    try:
        surveys = await Survey.get_by_user(db, current_user.id, skip=skip, limit=limit)
        total = len(surveys)  # In a real app, you'd get total count separately
        
        return SurveyList(
            surveys=[SurveyResponse.model_validate(survey) for survey in surveys],
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        logger.error(f"Get surveys error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get surveys"
        )

@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific survey"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return SurveyResponse.model_validate(survey)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get survey error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get survey"
        )

@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: int,
    survey_data: SurveyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a survey"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update survey
        update_data = survey_data.dict(exclude_unset=True)
        survey = await survey.update_survey(db, **update_data)
        
        return SurveyResponse.model_validate(survey)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update survey error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update survey"
        )

@router.delete("/{survey_id}")
async def delete_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a survey"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete survey
        await survey.delete_survey(db)
        
        return {"message": "Survey deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete survey error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete survey"
        )

@router.post("/{survey_id}/activate")
async def activate_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a survey"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Activate survey
        survey = await survey.activate_survey(db)
        
        return {"message": "Survey activated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activate survey error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate survey"
        )

@router.post("/{survey_id}/pause")
async def pause_survey(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a survey"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Pause survey
        survey = await survey.pause_survey(db)
        
        return {"message": "Survey paused successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pause survey error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause survey"
        )

@router.get("/{survey_id}/statistics", response_model=SurveyStatistics)
async def get_survey_statistics(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get survey statistics"""
    try:
        survey = await Survey.get_by_id(db, survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if user has access to this survey
        if survey.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get statistics
        stats = await survey.get_statistics(db)
        
        return SurveyStatistics(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get survey statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get survey statistics"
        )
