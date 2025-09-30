import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from models.schemas import GeminiResponse, SuggestedButton
from exceptions import LLMException
from utils.logger import logger
from config import config


class LLMService(ABC):
    """Abstract LLM service interface"""
    
    @abstractmethod
    def get_response(self, prompt: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> GeminiResponse:
        """Get response from LLM"""
        pass


class GeminiLLMService(LLMService):
    """Google Gemini LLM service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.llm.api_key
        if not self.api_key:
            raise LLMException('GEMINI_API_KEY not configured')
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(config.llm.model_name)
            logger.info(f"Initialized Gemini LLM service with model: {config.llm.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM service: {e}")
            raise LLMException(f"Failed to initialize Gemini LLM service: {e}")
    
    def get_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None, chat_history: Optional[List[Dict[str, Any]]] = None) -> GeminiResponse:
        """Get response from Gemini LLM"""
        try:
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "markdown": {"type": "string"},
                            "suggested_buttons": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "action": {"type": "string", "enum": ["update", "chat"]},
                                        "field_data": {
                                            "type": "object",
                                            "properties": schema

                                            
                                        }
                                    },
                                    "required": ["title", "action"]
                                }
                            }
                        },
                        "required": ["markdown", "suggested_buttons"]
                    },
                    "max_output_tokens": config.llm.max_tokens,
                    "temperature": config.llm.temperature
                }
            )
            
            # Extract text from response
            text = response.candidates[0].content.parts[0].text
            logger.debug(f"Raw LLM response: {text}")
            
            # Parse JSON response
            response_data = json.loads(text)
            
            # Convert to GeminiResponse model
            gemini_response = GeminiResponse(
                markdown=response_data.get('markdown', ''),
                suggested_buttons=[
                    SuggestedButton(**button) 
                    for button in response_data.get('suggested_buttons', [])
                ]
            )
            
            logger.info("Successfully generated LLM response")
            return gemini_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            raise LLMException(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise LLMException(f"LLM request failed: {e}")


class MockLLMService(LLMService):
    """Mock LLM service for testing"""
    
    def get_response(self, prompt: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> GeminiResponse:
        """Return mock response"""
        logger.info("Using mock LLM service")
        
        return GeminiResponse(
            markdown="I can help with that. Based on the information I have, the event is named 'Innovate AI Summit 2024'. Is that correct?",
            suggested_buttons=[
                SuggestedButton(title="Yes, that's correct", action="update", field_data={"f1": "Innovate AI Summit 2024"}),
                SuggestedButton(title="No, I want to change it", action="chat", field_data=None)
            ]
        )
