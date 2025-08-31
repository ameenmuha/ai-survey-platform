"""
Twilio Voice Service for Survey Calls

This module handles outbound voice calls using Twilio's API for conducting
AI-powered multilingual surveys.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from twilio.rest import Client
from twilio.twiml import VoiceResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class TwilioVoiceService:
    """Service for handling Twilio voice calls"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    async def make_outbound_call(
        self,
        to_number: str,
        survey_id: int,
        contact_id: int,
        webhook_url: str,
        language: str = "en"
    ) -> Dict:
        """
        Make an outbound call for survey
        
        Args:
            to_number: Phone number to call
            survey_id: Survey ID
            contact_id: Contact ID
            webhook_url: Webhook URL for call handling
            language: Preferred language for the call
            
        Returns:
            Dictionary with call details
        """
        try:
            if not self.client:
                raise Exception("Twilio client not initialized")
            
            # Create call parameters
            call_params = {
                'to': to_number,
                'from_': self.phone_number,
                'url': f"{webhook_url}?survey_id={survey_id}&contact_id={contact_id}&language={language}",
                'method': 'POST',
                'status_callback': f"{webhook_url}/status",
                'status_callback_method': 'POST',
                'status_callback_event': ['initiated', 'ringing', 'answered', 'completed'],
                'record': True,
                'recording_status_callback': f"{webhook_url}/recording",
                'recording_status_callback_method': 'POST'
            }
            
            # Make the call
            call = self.client.calls.create(**call_params)
            
            logger.info(f"Outbound call initiated: {call.sid} to {to_number}")
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": to_number,
                "from": self.phone_number,
                "survey_id": survey_id,
                "contact_id": contact_id,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Failed to make outbound call: {e}")
            raise
    
    async def get_call_status(self, call_sid: str) -> Dict:
        """Get the status of a call"""
        try:
            if not self.client:
                raise Exception("Twilio client not initialized")
            
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "price_unit": call.price_unit
            }
            
        except Exception as e:
            logger.error(f"Failed to get call status: {e}")
            raise
    
    async def end_call(self, call_sid: str) -> bool:
        """End an active call"""
        try:
            if not self.client:
                raise Exception("Twilio client not initialized")
            
            call = self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call ended: {call_sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end call: {e}")
            return False
    
    def generate_twiml_response(
        self,
        survey_data: Dict,
        current_question: int = 0,
        language: str = "en"
    ) -> str:
        """
        Generate TwiML response for survey flow
        
        Args:
            survey_data: Survey questions and configuration
            current_question: Current question index
            language: Language for the response
            
        Returns:
            TwiML XML string
        """
        try:
            response = VoiceResponse()
            
            # Get current question
            questions = survey_data.get("questions", [])
            if current_question >= len(questions):
                # Survey completed
                response.say(
                    self._get_completion_message(language),
                    voice=self._get_voice_for_language(language),
                    language=self._get_language_code(language)
                )
                response.hangup()
                return str(response)
            
            question = questions[current_question]
            question_text = question.get("question_translations", {}).get(language, question.get("question_text", ""))
            
            # Say the question
            response.say(
                question_text,
                voice=self._get_voice_for_language(language),
                language=self._get_language_code(language)
            )
            
            # Handle different question types
            question_type = question.get("question_type", "text")
            
            if question_type == "yes_no":
                # Yes/No question
                response.gather(
                    input='speech',
                    action=f'/api/v1/calls/gather?question_id={question["id"]}&next_question={current_question + 1}',
                    method='POST',
                    speech_timeout='auto',
                    language=self._get_language_code(language)
                )
                # Fallback if no input
                response.say(
                    self._get_no_input_message(language),
                    voice=self._get_voice_for_language(language),
                    language=self._get_language_code(language)
                )
                response.redirect(f'/api/v1/calls/gather?question_id={question["id"]}&next_question={current_question + 1}')
                
            elif question_type == "multiple_choice":
                # Multiple choice question
                options = question.get("options_translations", {}).get(language, question.get("options", []))
                options_text = ". ".join([f"{i+1}. {option}" for i, option in enumerate(options)])
                
                response.say(
                    f"{question_text}. Options: {options_text}",
                    voice=self._get_voice_for_language(language),
                    language=self._get_language_code(language)
                )
                
                response.gather(
                    input='dtmf speech',
                    action=f'/api/v1/calls/gather?question_id={question["id"]}&next_question={current_question + 1}',
                    method='POST',
                    speech_timeout='auto',
                    language=self._get_language_code(language)
                )
                
            else:
                # Text/Open-ended question
                response.gather(
                    input='speech',
                    action=f'/api/v1/calls/gather?question_id={question["id"]}&next_question={current_question + 1}',
                    method='POST',
                    speech_timeout='auto',
                    language=self._get_language_code(language)
                )
                # Fallback if no input
                response.say(
                    self._get_no_input_message(language),
                    voice=self._get_voice_for_language(language),
                    language=self._get_language_code(language)
                )
                response.redirect(f'/api/v1/calls/gather?question_id={question["id"]}&next_question={current_question + 1}')
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Failed to generate TwiML response: {e}")
            # Return basic error response
            response = VoiceResponse()
            response.say("Sorry, there was an error. Please try again later.", voice='alice')
            response.hangup()
            return str(response)
    
    def _get_voice_for_language(self, language: str) -> str:
        """Get appropriate voice for language"""
        voice_mapping = {
            "en": "alice",
            "hi": "alice",  # Hindi - use alice with language code
            "bn": "alice",  # Bengali
            "te": "alice",  # Telugu
            "mr": "alice",  # Marathi
            "ta": "alice",  # Tamil
            "gu": "alice",  # Gujarati
            "kn": "alice",  # Kannada
            "ml": "alice",  # Malayalam
            "pa": "alice",  # Punjabi
        }
        return voice_mapping.get(language, "alice")
    
    def _get_language_code(self, language: str) -> str:
        """Get Twilio language code"""
        language_mapping = {
            "en": "en-US",
            "hi": "hi-IN",
            "bn": "bn-IN",
            "te": "te-IN",
            "mr": "mr-IN",
            "ta": "ta-IN",
            "gu": "gu-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "pa": "pa-IN",
        }
        return language_mapping.get(language, "en-US")
    
    def _get_completion_message(self, language: str) -> str:
        """Get survey completion message"""
        messages = {
            "en": "Thank you for participating in our survey. Your responses have been recorded. Goodbye!",
            "hi": "हमारे सर्वेक्षण में भाग लेने के लिए धन्यवाद। आपके जवाब दर्ज कर लिए गए हैं। अलविदा!",
            "bn": "আমাদের জরিপে অংশগ্রহণের জন্য ধন্যবাদ। আপনার উত্তরগুলি রেকর্ড করা হয়েছে। বিদায়!",
            "te": "మా సర్వేలో పాల్గొన్నందుకు ధన్యవాదాలు. మీ సమాధానాలు రికార్డ్ చేయబడ్డాయి. వీడ్కోలు!",
            "mr": "आमच्या सर्वेक्षणात सहभाग घेतल्याबद्दल धन्यवाद. तुमची उत्तरे नोंदवली आहेत. निरोप!",
            "ta": "எங்கள் கணக்கெடுப்பில் பங்கேற்றதற்கு நன்றி. உங்கள் பதில்கள் பதிவு செய்யப்பட்டுள்ளன. பிரியாவிடை!",
            "gu": "આપણા સર્વેમાં ભાગ લેવા માટે આભાર. તમારા જવાબો રેકોર્ડ કરવામાં આવ્યા છે. આવજો!",
            "kn": "ನಮ್ಮ ಸಮೀಕ್ಷೆಯಲ್ಲಿ ಭಾಗವಹಿಸಿದ್ದಕ್ಕೆ ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ಉತ್ತರಗಳನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ. ವಿದಾಯ!",
            "ml": "ഞങ്ങളുടെ സർവേയിൽ പങ്കെടുത്തതിന് നന്ദി. നിങ്ങളുടെ ഉത്തരങ്ങൾ രേഖപ്പെടുത്തിയിരിക്കുന്നു. വിട!",
            "pa": "ਸਾਡੇ ਸਰਵੇਖਣ ਵਿੱਚ ਹਿੱਸਾ ਲੈਣ ਲਈ ਧੰਨਵਾਦ। ਤੁਹਾਡੇ ਜਵਾਬ ਦਰਜ ਕੀਤੇ ਗਏ ਹਨ। ਅਲਵਿਦਾ!",
        }
        return messages.get(language, messages["en"])
    
    def _get_no_input_message(self, language: str) -> str:
        """Get no input message"""
        messages = {
            "en": "I didn't hear your response. Please try again.",
            "hi": "मैंने आपका जवाब नहीं सुना। कृपया फिर से कोशिश करें।",
            "bn": "আমি আপনার উত্তর শুনতে পাইনি। অনুগ্রহ করে আবার চেষ্টা করুন।",
            "te": "నేను మీ సమాధానం వినలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
            "mr": "मी तुमचे उत्तर ऐकलं नाही. कृपया पुन्हा प्रयत्न करा.",
            "ta": "நான் உங்கள் பதிலைக் கேட்கவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
            "gu": "મેં તમારો જવાબ સાંભળ્યો નથી. કૃપા કરીને ફરીથી પ્રયાસ કરો.",
            "kn": "ನಾನು ನಿಮ್ಮ ಉತ್ತರವನ್ನು ಕೇಳಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
            "ml": "ഞാൻ നിങ്ങളുടെ ഉത്തരം കേട്ടില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
            "pa": "ਮੈਂ ਤੁਹਾਡਾ ਜਵਾਬ ਨਹੀਂ ਸੁਣਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        }
        return messages.get(language, messages["en"])
    
    async def get_call_recordings(self, call_sid: str) -> List[Dict]:
        """Get recordings for a call"""
        try:
            if not self.client:
                raise Exception("Twilio client not initialized")
            
            recordings = self.client.recordings.list(call_sid=call_sid)
            
            return [
                {
                    "recording_sid": recording.sid,
                    "duration": recording.duration,
                    "start_time": recording.start_time,
                    "end_time": recording.end_time,
                    "price": recording.price,
                    "price_unit": recording.price_unit,
                    "uri": recording.uri
                }
                for recording in recordings
            ]
            
        except Exception as e:
            logger.error(f"Failed to get call recordings: {e}")
            return []
    
    async def delete_recording(self, recording_sid: str) -> bool:
        """Delete a recording"""
        try:
            if not self.client:
                raise Exception("Twilio client not initialized")
            
            self.client.recordings(recording_sid).delete()
            logger.info(f"Recording deleted: {recording_sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete recording: {e}")
            return False

# Global instance
twilio_voice_service = TwilioVoiceService()
