from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import pandas as pd
import io
import logging
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.survey import Survey
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, ContactList, ContactUpload
from app.schemas.survey import SurveyResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=ContactList)
async def get_contacts(
    survey_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contacts with optional filtering"""
    try:
        contacts = await Contact.get_contacts(
            db=db,
            survey_id=survey_id,
            status=status,
            skip=skip,
            limit=limit,
            user_id=current_user.id
        )
        
        total = await Contact.count_contacts(
            db=db,
            survey_id=survey_id,
            status=status,
            user_id=current_user.id
        )
        
        return ContactList(
            contacts=[ContactResponse.model_validate(contact) for contact in contacts],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contacts"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contact by ID"""
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
        
        return ContactResponse.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact {contact_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact"
        )

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    try:
        # Verify survey exists and user has access
        survey = await Survey.get_by_id(db=db, survey_id=contact_data.survey_id)
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
        
        contact = await Contact.create_contact(
            db=db,
            survey_id=contact_data.survey_id,
            phone_number=contact_data.phone_number,
            name=contact_data.name,
            email=contact_data.email,
            preferred_language=contact_data.preferred_language,
            additional_data=contact_data.additional_data
        )
        
        return ContactResponse.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contact"
        )

@router.post("/upload-csv/{survey_id}")
async def upload_contacts_csv(
    survey_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload contacts from CSV file"""
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
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV"
            )
        
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['phone_number']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process contacts
        contacts_data = []
        for _, row in df.iterrows():
            contact_data = {
                'phone_number': str(row['phone_number']),
                'name': row.get('name'),
                'email': row.get('email'),
                'preferred_language': row.get('preferred_language', 'en'),
                'additional_data': {k: v for k, v in row.items() 
                                  if k not in ['phone_number', 'name', 'email', 'preferred_language']}
            }
            contacts_data.append(contact_data)
        
        # Create contacts in bulk
        contacts = await Contact.bulk_create_contacts(
            db=db,
            survey_id=survey_id,
            contacts_data=contacts_data
        )
        
        return {
            "message": f"Successfully uploaded {len(contacts)} contacts",
            "contacts_created": len(contacts),
            "survey_id": survey_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading contacts CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload contacts"
        )

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update contact information"""
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
        
        updated_contact = await Contact.update_contact(
            db=db,
            contact_id=contact_id,
            **contact_data.model_dump(exclude_unset=True)
        )
        
        return ContactResponse.model_validate(updated_contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact"
        )

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete contact"""
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
        
        await Contact.delete_contact(db=db, contact_id=contact_id)
        
        return {"message": "Contact deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact"
        )

@router.get("/survey/{survey_id}/stats")
async def get_contact_stats(
    survey_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contact statistics for a survey"""
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
        
        stats = await Contact.get_survey_stats(db=db, survey_id=survey_id)
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact stats for survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact statistics"
        )
