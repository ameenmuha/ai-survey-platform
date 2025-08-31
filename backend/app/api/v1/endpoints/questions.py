from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionList

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=QuestionList)
async def get_questions(
    survey_id: Optional[int] = Query(None),
    question_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get questions with optional filtering"""
    try:
        questions = await Question.get_questions(
            db=db,
            survey_id=survey_id,
            question_type=question_type,
            skip=skip,
            limit=limit,
            user_id=current_user.id
        )
        
        total = await Question.count_questions(
            db=db,
            survey_id=survey_id,
            question_type=question_type,
            user_id=current_user.id
        )
        
        return QuestionList(
            questions=[QuestionResponse.model_validate(question) for question in questions],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch questions"
        )

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID"""
    try:
        question = await Question.get_by_id(db=db, question_id=question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check if user has access to this question's survey
        survey = await Survey.get_by_id(db=db, survey_id=question.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return QuestionResponse.model_validate(question)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch question"
        )

@router.post("/", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new question"""
    try:
        # Verify survey exists and user has access
        survey = await Survey.get_by_id(db=db, survey_id=question_data.survey_id)
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
        
        question = await Question.create_question(
            db=db,
            survey_id=question_data.survey_id,
            question_text=question_data.question_text,
            question_translations=question_data.question_translations,
            question_type=question_data.question_type,
            order_number=question_data.order_number,
            is_required=question_data.is_required,
            is_conditional=question_data.is_conditional,
            conditional_logic=question_data.conditional_logic,
            options=question_data.options,
            options_translations=question_data.options_translations,
            validation_rules=question_data.validation_rules,
            min_length=question_data.min_length,
            max_length=question_data.max_length,
            ai_clarification_enabled=question_data.ai_clarification_enabled,
            clarification_prompts=question_data.clarification_prompts
        )
        
        return QuestionResponse.model_validate(question)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create question"
        )

@router.post("/bulk/{survey_id}")
async def create_questions_bulk(
    survey_id: int,
    questions_data: List[QuestionCreate],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple questions for a survey"""
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
        
        questions = await Question.bulk_create_questions(
            db=db,
            survey_id=survey_id,
            questions_data=questions_data
        )
        
        return {
            "message": f"Successfully created {len(questions)} questions",
            "questions_created": len(questions),
            "survey_id": survey_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating questions bulk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create questions"
        )

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update question information"""
    try:
        question = await Question.get_by_id(db=db, question_id=question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check if user has access to this question's survey
        survey = await Survey.get_by_id(db=db, survey_id=question.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        updated_question = await Question.update_question(
            db=db,
            question_id=question_id,
            **question_data.model_dump(exclude_unset=True)
        )
        
        return QuestionResponse.model_validate(updated_question)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update question"
        )

@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete question"""
    try:
        question = await Question.get_by_id(db=db, question_id=question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check if user has access to this question's survey
        survey = await Survey.get_by_id(db=db, survey_id=question.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        await Question.delete_question(db=db, question_id=question_id)
        
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete question"
        )

@router.get("/survey/{survey_id}/ordered")
async def get_survey_questions_ordered(
    survey_id: int,
    language: str = Query("en", regex="^(en|hi|bn|te|mr|ta|gu|kn|ml|pa)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get questions for a survey in order with translations"""
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
        
        questions = await Question.get_survey_questions_ordered(
            db=db,
            survey_id=survey_id,
            language=language
        )
        
        return {
            "survey_id": survey_id,
            "language": language,
            "questions": [QuestionResponse.model_validate(q) for q in questions]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch survey questions"
        )

@router.post("/{question_id}/validate-response")
async def validate_response(
    question_id: int,
    response_text: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate a response for a specific question"""
    try:
        question = await Question.get_by_id(db=db, question_id=question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check if user has access to this question's survey
        survey = await Survey.get_by_id(db=db, survey_id=question.survey_id)
        if not survey or (survey.created_by != current_user.id and not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        is_valid, error_message = question.validate_response(response_text)
        
        return {
            "is_valid": is_valid,
            "error_message": error_message if not is_valid else None,
            "question_id": question_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating response for question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate response"
        )
