"""
AI Clarification Service for Survey Responses

This module handles AI-powered clarification of ambiguous survey responses
using Google Gemini or OpenAI GPT models.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIClarificationService:
    """Service for AI-powered response clarification"""
    
    def __init__(self):
        self.google_ai_key = settings.GOOGLE_AI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        
        # Initialize Google AI
        if self.google_ai_key:
            genai.configure(api_key=self.google_ai_key)
            self.google_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize OpenAI
        if self.openai_key:
            openai.api_key = self.openai_key
    
    async def clarify_response(
        self,
        response_text: str,
        question_text: str,
        question_type: str,
        language: str = "en",
        context: Optional[Dict] = None
    ) -> Tuple[str, float, Dict]:
        """
        Clarify an ambiguous response using AI
        
        Args:
            response_text: The original response text
            question_text: The question that was asked
            question_type: Type of question (text, multiple_choice, yes_no, etc.)
            language: Language of the response
            context: Additional context about the survey/respondent
            
        Returns:
            Tuple of (clarified_text, confidence_score, insights)
        """
        try:
            # Try Google AI first, fallback to OpenAI
            if self.google_ai_key:
                return await self._clarify_with_google_ai(
                    response_text, question_text, question_type, language, context
                )
            elif self.openai_key:
                return await self._clarify_with_openai(
                    response_text, question_text, question_type, language, context
                )
            else:
                logger.warning("No AI API keys configured")
                return response_text, 0.5, {"error": "No AI service available"}
                
        except Exception as e:
            logger.error(f"AI clarification failed: {e}")
            return response_text, 0.0, {"error": str(e)}
    
    async def _clarify_with_google_ai(
        self,
        response_text: str,
        question_text: str,
        question_type: str,
        language: str,
        context: Optional[Dict]
    ) -> Tuple[str, float, Dict]:
        """Clarify response using Google Gemini"""
        
        prompt = self._build_clarification_prompt(
            response_text, question_text, question_type, language, context
        )
        
        try:
            response = await self.google_model.generate_content_async(prompt)
            
            # Parse the response
            clarified_text = response.text.strip()
            
            # Extract confidence and insights (this would need more sophisticated parsing)
            confidence = 0.8  # Default confidence
            insights = {
                "clarification_method": "google_gemini",
                "original_response": response_text,
                "clarified_response": clarified_text,
                "language_detected": language
            }
            
            return clarified_text, confidence, insights
            
        except Exception as e:
            logger.error(f"Google AI clarification failed: {e}")
            raise
    
    async def _clarify_with_openai(
        self,
        response_text: str,
        question_text: str,
        question_type: str,
        language: str,
        context: Optional[Dict]
    ) -> Tuple[str, float, Dict]:
        """Clarify response using OpenAI GPT"""
        
        prompt = self._build_clarification_prompt(
            response_text, question_text, question_type, language, context
        )
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that helps clarify survey responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            clarified_text = response.choices[0].message.content.strip()
            
            # Extract confidence and insights
            confidence = 0.8  # Default confidence
            insights = {
                "clarification_method": "openai_gpt",
                "original_response": response_text,
                "clarified_response": clarified_text,
                "language_detected": language,
                "model_used": "gpt-3.5-turbo"
            }
            
            return clarified_text, confidence, insights
            
        except Exception as e:
            logger.error(f"OpenAI clarification failed: {e}")
            raise
    
    def _build_clarification_prompt(
        self,
        response_text: str,
        question_text: str,
        question_type: str,
        language: str,
        context: Optional[Dict]
    ) -> str:
        """Build the clarification prompt"""
        
        language_names = {
            "en": "English",
            "hi": "Hindi",
            "bn": "Bengali",
            "te": "Telugu",
            "mr": "Marathi",
            "ta": "Tamil",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi"
        }
        
        language_name = language_names.get(language, "English")
        
        prompt = f"""
        You are an AI assistant helping to clarify survey responses. Please analyze the following:

        Question: {question_text}
        Question Type: {question_type}
        Language: {language_name}
        Original Response: "{response_text}"

        Context: {context or "No additional context provided"}

        Please provide:
        1. A clarified version of the response that is clear, complete, and directly answers the question
        2. If the response is already clear and complete, return it as-is
        3. If the response is ambiguous, unclear, or incomplete, provide a reasonable interpretation
        4. Maintain the original language and cultural context
        5. For multiple choice questions, identify the best matching option
        6. For yes/no questions, provide a clear yes or no answer

        Return only the clarified response text, nothing else.
        """
        
        return prompt
    
    async def generate_insights(
        self,
        responses: List[Dict],
        survey_context: Dict
    ) -> Dict:
        """
        Generate insights from a collection of responses
        
        Args:
            responses: List of response dictionaries
            survey_context: Context about the survey
            
        Returns:
            Dictionary containing insights and analysis
        """
        try:
            if self.google_ai_key:
                return await self._generate_insights_with_google_ai(responses, survey_context)
            elif self.openai_key:
                return await self._generate_insights_with_openai(responses, survey_context)
            else:
                return {"error": "No AI service available for insights"}
                
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {"error": str(e)}
    
    async def _generate_insights_with_google_ai(
        self,
        responses: List[Dict],
        survey_context: Dict
    ) -> Dict:
        """Generate insights using Google Gemini"""
        
        # Prepare response data for analysis
        response_summary = []
        for resp in responses:
            response_summary.append({
                "question": resp.get("question_text", ""),
                "response": resp.get("processed_response", resp.get("transcribed_text", "")),
                "language": resp.get("response_language", "en")
            })
        
        prompt = f"""
        Analyze the following survey responses and provide insights:

        Survey Context: {survey_context}
        
        Responses:
        {response_summary}

        Please provide:
        1. Key themes and patterns
        2. Common responses and outliers
        3. Language distribution analysis
        4. Response quality assessment
        5. Recommendations for survey improvement

        Format the response as a JSON object with the following structure:
        {{
            "themes": ["theme1", "theme2"],
            "patterns": ["pattern1", "pattern2"],
            "language_distribution": {{"en": 50, "hi": 30}},
            "response_quality": "good/medium/poor",
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        try:
            response = await self.google_model.generate_content_async(prompt)
            # Parse JSON response (in a real implementation, you'd need proper JSON parsing)
            return {
                "insights_method": "google_gemini",
                "raw_insights": response.text,
                "response_count": len(responses)
            }
            
        except Exception as e:
            logger.error(f"Google AI insights generation failed: {e}")
            raise
    
    async def _generate_insights_with_openai(
        self,
        responses: List[Dict],
        survey_context: Dict
    ) -> Dict:
        """Generate insights using OpenAI GPT"""
        
        response_summary = []
        for resp in responses:
            response_summary.append({
                "question": resp.get("question_text", ""),
                "response": resp.get("processed_response", resp.get("transcribed_text", "")),
                "language": resp.get("response_language", "en")
            })
        
        prompt = f"""
        Analyze the following survey responses and provide insights:

        Survey Context: {survey_context}
        
        Responses:
        {response_summary}

        Please provide:
        1. Key themes and patterns
        2. Common responses and outliers
        3. Language distribution analysis
        4. Response quality assessment
        5. Recommendations for survey improvement

        Format the response as a JSON object.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI analyst specializing in survey data analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "insights_method": "openai_gpt",
                "raw_insights": response.choices[0].message.content,
                "response_count": len(responses),
                "model_used": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            logger.error(f"OpenAI insights generation failed: {e}")
            raise

# Global instance
ai_clarification_service = AIClarificationService()
