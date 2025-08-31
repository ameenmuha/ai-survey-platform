from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.models.contact import Contact
from app.models.response import Response
from app.models.call_log import CallLog
from app.models.question import Question

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    try:
        # Get user's surveys
        surveys = await Survey.get_surveys_by_user(db=db, user_id=current_user.id)
        
        # Calculate statistics
        total_surveys = len(surveys)
        active_surveys = len([s for s in surveys if s.is_active and s.status == "active"])
        
        # Get total contacts across all surveys
        total_contacts = 0
        total_responses = 0
        total_calls = 0
        completed_calls = 0
        
        for survey in surveys:
            survey_contacts = await Contact.count_contacts(db=db, survey_id=survey.id)
            survey_responses = await Response.count_responses(db=db, survey_id=survey.id)
            survey_calls = await CallLog.count_call_logs(db=db, survey_id=survey.id)
            survey_completed_calls = await CallLog.count_call_logs(
                db=db, survey_id=survey.id, call_result="completed"
            )
            
            total_contacts += survey_contacts
            total_responses += survey_responses
            total_calls += survey_calls
            completed_calls += survey_completed_calls
        
        # Calculate response rate
        response_rate = (total_responses / total_contacts * 100) if total_contacts > 0 else 0
        
        # Get recent activity
        recent_surveys = await Survey.get_recent_surveys(db=db, user_id=current_user.id, limit=5)
        recent_responses = await Response.get_recent_responses(db=db, user_id=current_user.id, limit=10)
        
        return {
            "total_surveys": total_surveys,
            "active_surveys": active_surveys,
            "total_contacts": total_contacts,
            "total_responses": total_responses,
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "response_rate": round(response_rate, 2),
            "recent_surveys": [
                {
                    "id": survey.id,
                    "title": survey.title,
                    "status": survey.status,
                    "created_at": survey.created_at.isoformat() if survey.created_at else None
                }
                for survey in recent_surveys
            ],
            "recent_responses": [
                {
                    "id": response.id,
                    "survey_id": response.survey_id,
                    "question_id": response.question_id,
                    "status": response.status,
                    "created_at": response.created_at.isoformat() if response.created_at else None
                }
                for response in recent_responses
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )

@router.get("/survey/{survey_id}")
async def get_survey_analytics(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for a specific survey"""
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
        
        # Get contact statistics
        contact_stats = await Contact.get_survey_stats(db=db, survey_id=survey_id)
        
        # Get response statistics
        response_stats = await Response.get_survey_responses_summary(db=db, survey_id=survey_id)
        
        # Get call statistics
        call_stats = await CallLog.get_survey_call_stats(db=db, survey_id=survey_id)
        
        # Get question-wise response distribution
        questions = await Question.get_by_survey(db=db, survey_id=survey_id)
        question_stats = []
        
        for question in questions:
            question_responses = await Response.get_by_question(db=db, question_id=question.id)
            question_stats.append({
                "question_id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "total_responses": len(question_responses),
                "completed_responses": len([r for r in question_responses if r.status == "completed"]),
                "average_confidence": sum([r.confidence_score or 0 for r in question_responses]) / len(question_responses) if question_responses else 0
            })
        
        return {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "contact_statistics": contact_stats,
            "response_statistics": response_stats,
            "call_statistics": call_stats,
            "question_statistics": question_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch survey analytics"
        )

@router.get("/trends")
async def get_trends_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trends analytics over a specified period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get surveys created in the period
        surveys_created = await Survey.get_surveys_by_date_range(
            db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
        
        # Get responses in the period
        responses_created = await Response.get_responses_by_date_range(
            db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
        
        # Get calls in the period
        calls_made = await CallLog.get_calls_by_date_range(
            db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
        
        # Calculate daily trends
        daily_stats = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            daily_stats[date_key] = {
                "surveys_created": 0,
                "responses_received": 0,
                "calls_made": 0,
                "calls_completed": 0
            }
            current_date += timedelta(days=1)
        
        # Populate daily stats
        for survey in surveys_created:
            date_key = survey.created_at.strftime("%Y-%m-%d")
            if date_key in daily_stats:
                daily_stats[date_key]["surveys_created"] += 1
        
        for response in responses_created:
            date_key = response.created_at.strftime("%Y-%m-%d")
            if date_key in daily_stats:
                daily_stats[date_key]["responses_received"] += 1
        
        for call in calls_made:
            date_key = call.created_at.strftime("%Y-%m-%d")
            if date_key in daily_stats:
                daily_stats[date_key]["calls_made"] += 1
                if call.call_result == "completed":
                    daily_stats[date_key]["calls_completed"] += 1
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_surveys_created": len(surveys_created),
            "total_responses_received": len(responses_created),
            "total_calls_made": len(calls_made),
            "total_calls_completed": len([c for c in calls_made if c.call_result == "completed"]),
            "daily_trends": daily_stats
        }
    except Exception as e:
        logger.error(f"Error fetching trends analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trends analytics"
        )

@router.get("/language-distribution")
async def get_language_distribution(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get language distribution across all surveys"""
    try:
        # Get all responses for user's surveys
        responses = await Response.get_responses_by_user(db=db, user_id=current_user.id)
        
        # Calculate language distribution
        language_counts = {}
        total_responses = len(responses)
        
        for response in responses:
            language = response.response_language or "unknown"
            language_counts[language] = language_counts.get(language, 0) + 1
        
        # Calculate percentages
        language_distribution = {}
        for language, count in language_counts.items():
            percentage = (count / total_responses * 100) if total_responses > 0 else 0
            language_distribution[language] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return {
            "total_responses": total_responses,
            "language_distribution": language_distribution
        }
    except Exception as e:
        logger.error(f"Error fetching language distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch language distribution"
        )

@router.get("/ai-insights")
async def get_ai_insights(
    survey_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated insights from responses"""
    try:
        # Get responses with AI insights
        responses = await Response.get_responses_with_ai_insights(
            db=db, user_id=current_user.id, survey_id=survey_id
        )
        
        # Aggregate insights
        insights = {
            "total_responses_with_insights": len(responses),
            "common_themes": {},
            "sentiment_analysis": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            },
            "clarification_needs": 0,
            "confidence_distribution": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        for response in responses:
            if response.ai_insights:
                # Analyze themes
                if "themes" in response.ai_insights:
                    for theme in response.ai_insights["themes"]:
                        insights["common_themes"][theme] = insights["common_themes"].get(theme, 0) + 1
                
                # Analyze sentiment
                if "sentiment" in response.ai_insights:
                    sentiment = response.ai_insights["sentiment"]
                    insights["sentiment_analysis"][sentiment] += 1
                
                # Count clarifications
                if response.ai_clarification_used:
                    insights["clarification_needs"] += 1
                
                # Analyze confidence
                if response.confidence_score:
                    if response.confidence_score >= 0.8:
                        insights["confidence_distribution"]["high"] += 1
                    elif response.confidence_score >= 0.6:
                        insights["confidence_distribution"]["medium"] += 1
                    else:
                        insights["confidence_distribution"]["low"] += 1
        
        return insights
    except Exception as e:
        logger.error(f"Error fetching AI insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch AI insights"
        )
