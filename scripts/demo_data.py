#!/usr/bin/env python3
"""
Demo Data Script for AI-Powered Multilingual Survey Platform

This script populates the database with sample data for testing and demonstration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.survey import Survey
from app.models.contact import Contact
from app.models.question import Question
from app.core.security import get_password_hash

async def create_demo_users():
    """Create demo users"""
    async with AsyncSessionLocal() as db:
        # Create admin user
        admin_user = await User.create_user(
            db=db,
            email="admin@example.com",
            full_name="Admin User",
            password="admin123456",
            role="admin",
            organization="Demo Organization"
        )
        print(f"✅ Created admin user: {admin_user.email}")
        
        # Create surveyor user
        surveyor_user = await User.create_user(
            db=db,
            email="surveyor@example.com",
            full_name="Demo Surveyor",
            password="demo123456",
            role="surveyor",
            organization="Demo Organization"
        )
        print(f"✅ Created surveyor user: {surveyor_user.email}")
        
        # Create analyst user
        analyst_user = await User.create_user(
            db=db,
            email="analyst@example.com",
            full_name="Demo Analyst",
            password="demo123456",
            role="analyst",
            organization="Demo Organization"
        )
        print(f"✅ Created analyst user: {analyst_user.email}")
        
        return admin_user, surveyor_user, analyst_user

async def create_demo_surveys(surveyor_user):
    """Create demo surveys"""
    async with AsyncSessionLocal() as db:
        # Survey 1: Customer Satisfaction
        survey1 = await Survey.create_survey(
            db=db,
            title="Customer Satisfaction Survey 2024",
            created_by=surveyor_user.id,
            description="A comprehensive survey to understand customer satisfaction levels across different touchpoints.",
            primary_language="en",
            supported_languages=["en", "hi", "bn"],
            max_questions=10,
            estimated_duration=8,
            ai_clarification_enabled=True,
            ai_summary_enabled=True,
            confidence_threshold=75
        )
        print(f"✅ Created survey: {survey1.title}")
        
        # Survey 2: Healthcare Access
        survey2 = await Survey.create_survey(
            db=db,
            title="Healthcare Access Survey",
            created_by=surveyor_user.id,
            description="Survey to understand healthcare access and quality in rural areas.",
            primary_language="hi",
            supported_languages=["hi", "en", "bn", "te", "mr"],
            max_questions=15,
            estimated_duration=12,
            ai_clarification_enabled=True,
            ai_summary_enabled=True,
            confidence_threshold=80
        )
        print(f"✅ Created survey: {survey2.title}")
        
        # Survey 3: Education Quality
        survey3 = await Survey.create_survey(
            db=db,
            title="Education Quality Assessment",
            created_by=surveyor_user.id,
            description="Assessment of education quality and infrastructure in government schools.",
            primary_language="en",
            supported_languages=["en", "hi", "ta", "te", "gu"],
            max_questions=12,
            estimated_duration=10,
            ai_clarification_enabled=True,
            ai_summary_enabled=True,
            confidence_threshold=70
        )
        print(f"✅ Created survey: {survey3.title}")
        
        return survey1, survey2, survey3

async def create_demo_questions(surveys):
    """Create demo questions for surveys"""
    async with AsyncSessionLocal() as db:
        survey1, survey2, survey3 = surveys
        
        # Questions for Customer Satisfaction Survey
        questions1 = [
            {
                "question_text": "How satisfied are you with our product quality?",
                "question_translations": {
                    "hi": "आप हमारे उत्पाद की गुणवत्ता से कितने संतुष्ट हैं?",
                    "bn": "আপনি আমাদের পণ্যের মান নিয়ে কতটা সন্তুষ্ট?"
                },
                "question_type": "rating",
                "order_number": 1,
                "is_required": True
            },
            {
                "question_text": "How likely are you to recommend our service to others?",
                "question_translations": {
                    "hi": "आप हमारी सेवा को दूसरों को सिफारिश करने की कितनी संभावना रखते हैं?",
                    "bn": "আপনি কতটা সম্ভাবনা রাখেন যে অন্যকে আমাদের পরিষেবার সুপারিশ করবেন?"
                },
                "question_type": "rating",
                "order_number": 2,
                "is_required": True
            },
            {
                "question_text": "What aspects of our service need improvement?",
                "question_translations": {
                    "hi": "हमारी सेवा के किन पहलुओं में सुधार की आवश्यकता है?",
                    "bn": "আমাদের পরিষেবার কোন দিকগুলি উন্নতির প্রয়োজন?"
                },
                "question_type": "text",
                "order_number": 3,
                "is_required": False
            },
            {
                "question_text": "How did you hear about our service?",
                "question_translations": {
                    "hi": "आपने हमारी सेवा के बारे में कैसे सुना?",
                    "bn": "আপনি কীভাবে আমাদের পরিষেবার কথা শুনেছেন?"
                },
                "question_type": "multiple_choice",
                "order_number": 4,
                "is_required": True,
                "options": ["Social Media", "Friend/Family", "Advertisement", "Search Engine", "Other"],
                "options_translations": {
                    "hi": ["सोशल मीडिया", "दोस्त/परिवार", "विज्ञापन", "सर्च इंजन", "अन्य"],
                    "bn": ["সোশ্যাল মিডিয়া", "বন্ধু/পরিবার", "বিজ্ঞাপন", "সার্চ ইঞ্জিন", "অন্যান্য"]
                }
            }
        ]
        
        # Questions for Healthcare Survey
        questions2 = [
            {
                "question_text": "Do you have access to a primary healthcare facility within 5 km?",
                "question_translations": {
                    "hi": "क्या आपको 5 किमी के भीतर प्राथमिक स्वास्थ्य सुविधा तक पहुंच है?",
                    "bn": "আপনার কি 5 কিলোমিটারের মধ্যে প্রাথমিক স্বাস্থ্যসেবা সুবিধা আছে?",
                    "te": "మీకు 5 కి.మీ లోపల ప్రాథమిక ఆరోగ్య సంరక్షణ సౌకర్యం ఉందా?",
                    "mr": "तुम्हाला 5 किमी मध्ये प्राथमिक आरोग्य सुविधा उपलब्ध आहे का?"
                },
                "question_type": "yes_no",
                "order_number": 1,
                "is_required": True
            },
            {
                "question_text": "How often do you visit a healthcare facility?",
                "question_translations": {
                    "hi": "आप कितनी बार स्वास्थ्य सुविधा का दौरा करते हैं?",
                    "bn": "আপনি কতবার স্বাস্থ্যসেবা সুবিধা পরিদর্শন করেন?",
                    "te": "మీరు ఆరోగ్య సంరక్షణ సౌకర్యాన్ని ఎంత తరచుగా సందర్శిస్తారు?",
                    "mr": "तुम्ही किती वेळा आरोग्य सुविधेला भेट देतात?"
                },
                "question_type": "multiple_choice",
                "order_number": 2,
                "is_required": True,
                "options": ["Never", "Once a year", "2-3 times a year", "Monthly", "Weekly"],
                "options_translations": {
                    "hi": ["कभी नहीं", "साल में एक बार", "साल में 2-3 बार", "महीने में", "साप्ताहिक"],
                    "bn": ["কখনও না", "বছরে একবার", "বছরে 2-3 বার", "মাসিক", "সাপ্তাহিক"],
                    "te": ["ఎప్పుడూ లేదు", "సంవత్సరానికి ఒక్కసారి", "సంవత్సరానికి 2-3 సార్లు", "నెలవారీ", "వారపు"],
                    "mr": ["कधीही नाही", "वर्षाला एकदा", "वर्षाला 2-3 वेळा", "महिन्याला", "आठवड्याला"]
                }
            },
            {
                "question_text": "What are the main challenges you face in accessing healthcare?",
                "question_translations": {
                    "hi": "स्वास्थ्य सेवा तक पहुंचने में आपको क्या मुख्य चुनौतियों का सामना करना पड़ता है?",
                    "bn": "স্বাস্থ্যসেবা পাওয়ার ক্ষেত্রে আপনি কী প্রধান চ্যালেঞ্জের মুখোমুখি হন?",
                    "te": "ఆరోగ్య సంరక్షణను పొందడంలో మీరు ఎదుర్కొంటున్న ప్రధాన సవాళ్లు ఏమిటి?",
                    "mr": "आरोग्यसेवा मिळवण्यासाठी तुम्हाला कोणत्या मुख्य आव्हानांचा सामना करावा लागतो?"
                },
                "question_type": "text",
                "order_number": 3,
                "is_required": False
            }
        ]
        
        # Questions for Education Survey
        questions3 = [
            {
                "question_text": "How would you rate the quality of education in your local school?",
                "question_translations": {
                    "hi": "आप अपने स्थानीय स्कूल में शिक्षा की गुणवत्ता को कैसे आंकेंगे?",
                    "ta": "உங்கள் உள்ளூர் பள்ளியில் கல்வியின் தரத்தை எப்படி மதிப்பிடுவீர்கள்?",
                    "te": "మీ స్థానిక పాఠశాలలో విద్యా నాణ్యతను మీరు ఎలా రేట్ చేస్తారు?",
                    "gu": "તમે તમારા સ્થાનિક શાળામાં શિક્ષણની ગુણવત્તાને કેવી રીતે રેટ કરશો?"
                },
                "question_type": "rating",
                "order_number": 1,
                "is_required": True
            },
            {
                "question_text": "Does your child have access to digital learning tools?",
                "question_translations": {
                    "hi": "क्या आपके बच्चे को डिजिटल लर्निंग टूल्स तक पहुंच है?",
                    "ta": "உங்கள் குழந்தைக்கு டிஜிட்டல் கற்றல் கருவிகள் உள்ளதா?",
                    "te": "మీ పిల్లలకు డిజిటల్ లెర్నింగ్ టూల్స్ ఉందా?",
                    "gu": "તમારા બાળકને ડિજિટલ શિક્ષણ સાધનો ઉપલબ્ધ છે?"
                },
                "question_type": "yes_no",
                "order_number": 2,
                "is_required": True
            },
            {
                "question_text": "What improvements would you suggest for the education system?",
                "question_translations": {
                    "hi": "शिक्षा प्रणाली में क्या सुधार आप सुझाव देंगे?",
                    "ta": "கல்வி முறைக்கு என்ன மேம்பாடுகளை நீங்கள் பரிந்துரைப்பீர்கள்?",
                    "te": "విద్యా వ్యవస్థకు మీరు ఏ మెరుగుదలలను సూచిస్తారు?",
                    "gu": "શિક્ષણ પ્રણાલીમાં તમે કયા સુધારાઓની સલાહ આપશો?"
                },
                "question_type": "text",
                "order_number": 3,
                "is_required": False
            }
        ]
        
        # Create questions for each survey
        for i, (survey, questions) in enumerate([(survey1, questions1), (survey2, questions2), (survey3, questions3)]):
            for question_data in questions:
                await Question.create_question(
                    db=db,
                    survey_id=survey.id,
                    **question_data
                )
            print(f"✅ Created {len(questions)} questions for survey {i+1}")

async def create_demo_contacts(surveys):
    """Create demo contacts for surveys"""
    async with AsyncSessionLocal() as db:
        survey1, survey2, survey3 = surveys
        
        # Demo contacts for Customer Satisfaction Survey
        contacts1_data = [
            {"phone_number": "+919876543210", "name": "Rahul Sharma", "preferred_language": "en"},
            {"phone_number": "+919876543211", "name": "Priya Patel", "preferred_language": "hi"},
            {"phone_number": "+919876543212", "name": "Amit Kumar", "preferred_language": "en"},
            {"phone_number": "+919876543213", "name": "Sneha Singh", "preferred_language": "hi"},
            {"phone_number": "+919876543214", "name": "Rajesh Verma", "preferred_language": "en"}
        ]
        
        # Demo contacts for Healthcare Survey
        contacts2_data = [
            {"phone_number": "+919876543215", "name": "Lakshmi Devi", "preferred_language": "hi"},
            {"phone_number": "+919876543216", "name": "Mohammed Ali", "preferred_language": "hi"},
            {"phone_number": "+919876543217", "name": "Sunita Kumari", "preferred_language": "hi"},
            {"phone_number": "+919876543218", "name": "Ramesh Yadav", "preferred_language": "hi"},
            {"phone_number": "+919876543219", "name": "Fatima Begum", "preferred_language": "bn"}
        ]
        
        # Demo contacts for Education Survey
        contacts3_data = [
            {"phone_number": "+919876543220", "name": "Anjali Desai", "preferred_language": "en"},
            {"phone_number": "+919876543221", "name": "Vikram Malhotra", "preferred_language": "en"},
            {"phone_number": "+919876543222", "name": "Meera Iyer", "preferred_language": "ta"},
            {"phone_number": "+919876543223", "name": "Krishna Reddy", "preferred_language": "te"},
            {"phone_number": "+919876543224", "name": "Pooja Shah", "preferred_language": "gu"}
        ]
        
        # Create contacts for each survey
        for i, (survey, contacts_data) in enumerate([(survey1, contacts1_data), (survey2, contacts2_data), (survey3, contacts3_data)]):
            for contact_data in contacts_data:
                await Contact.create_contact(
                    db=db,
                    survey_id=survey.id,
                    **contact_data
                )
            print(f"✅ Created {len(contacts_data)} contacts for survey {i+1}")

async def main():
    """Main function to create demo data"""
    print("🚀 Creating Demo Data for AI Survey Platform")
    print("=" * 50)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Create demo users
    admin_user, surveyor_user, analyst_user = await create_demo_users()
    
    # Create demo surveys
    surveys = await create_demo_surveys(surveyor_user)
    
    # Create demo questions
    await create_demo_questions(surveys)
    
    # Create demo contacts
    await create_demo_contacts(surveys)
    
    print("\n" + "=" * 50)
    print("🎉 Demo data created successfully!")
    print("=" * 50)
    
    print("\n📋 Demo Credentials:")
    print("Admin:     admin@example.com / admin123456")
    print("Surveyor:  surveyor@example.com / demo123456")
    print("Analyst:   analyst@example.com / demo123456")
    
    print("\n📊 Created Data:")
    print("- 3 Users (Admin, Surveyor, Analyst)")
    print("- 3 Surveys with different languages")
    print("- 9 Questions across all surveys")
    print("- 15 Contacts across all surveys")
    
    print("\n🔧 Next Steps:")
    print("1. Start the backend server")
    print("2. Start the frontend application")
    print("3. Login with demo credentials")
    print("4. Explore the surveys and contacts")

if __name__ == "__main__":
    asyncio.run(main())
