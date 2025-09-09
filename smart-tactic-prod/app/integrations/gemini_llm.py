"""
Gemini LLM integration for AI-powered event processing
Handles form generation, layout updates, and data correction
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import Config
from app.utils.logger import get_logger
from app.integrations.langfuse_logger import LangfuseLogger

logger = get_logger(__name__)

class GeminiLLM:
    """Client for Gemini Pro API operations"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.GEMINI_API_KEY
        self.model_name = self.config.GEMINI_MODEL
        self.model = None
        self.langfuse_logger = LangfuseLogger()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            if not self.api_key:
                logger.warning("No Gemini API key configured")
                return
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Gemini model initialized: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            self.model = None
    
    def generate_event_fields(self, prompt: str) -> Dict[str, Any]:
        """Generate form fields for an event using LLM"""
        try:
            if not self.model:
                return {'success': False, 'error': 'Gemini model not initialized'}
            
            # Start Langfuse trace
            trace = self.langfuse_logger.start_trace(
                name="generate_event_fields",
                input={"prompt": prompt}
            )
            
            try:
                # Prepare the prompt
                full_prompt = self._build_form_generation_prompt(prompt)
                
                # Generate response
                response = self._generate_with_retry(full_prompt)
                
                if response:
                    # Parse the response
                    form_fields = self._parse_form_fields_response(response.text)
                    
                    # Log successful generation
                    self.langfuse_logger.end_trace(
                        trace,
                        output={"form_fields": form_fields},
                        status="success"
                    )
                    
                    logger.info("Event fields generated successfully")
                    return {
                        'success': True,
                        'fields': form_fields
                    }
                else:
                    raise Exception("No response from Gemini")
                    
            except Exception as e:
                # Log failed generation
                self.langfuse_logger.end_trace(
                    trace,
                    error=str(e),
                    status="error"
                )
                raise e
                
        except Exception as e:
            logger.error(f"Error generating event fields: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_layout(self, prompt: str) -> Dict[str, Any]:
        """Generate form layout using LLM"""
        try:
            if not self.model:
                return {'success': False, 'error': 'Gemini model not initialized'}
            
            # Start Langfuse trace
            trace = self.langfuse_logger.start_trace(
                name="generate_layout",
                input={"prompt": prompt}
            )
            
            try:
                # Prepare the prompt
                full_prompt = self._build_layout_generation_prompt(prompt)
                
                # Generate response
                response = self._generate_with_retry(full_prompt)
                
                if response:
                    # Parse the response
                    layout = self._parse_layout_response(response.text)
                    
                    # Log successful generation
                    self.langfuse_logger.end_trace(
                        trace,
                        output={"layout": layout},
                        status="success"
                    )
                    
                    logger.info("Layout generated successfully")
                    return {
                        'success': True,
                        'layout': layout
                    }
                else:
                    raise Exception("No response from Gemini")
                    
            except Exception as e:
                # Log failed generation
                self.langfuse_logger.end_trace(
                    trace,
                    error=str(e),
                    status="error"
                )
                raise e
                
        except Exception as e:
            logger.error(f"Error generating layout: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def correct_event_data(self, prompt: str) -> Dict[str, Any]:
        """Correct event data using LLM"""
        try:
            if not self.model:
                return {'success': False, 'error': 'Gemini model not initialized'}
            
            # Start Langfuse trace
            trace = self.langfuse_logger.start_trace(
                name="correct_event_data",
                input={"prompt": prompt}
            )
            
            try:
                # Prepare the prompt
                full_prompt = self._build_correction_prompt(prompt)
                
                # Generate response
                response = self._generate_with_retry(full_prompt)
                
                if response:
                    # Parse the response
                    corrected_data = self._parse_correction_response(response.text)
                    
                    # Log successful correction
                    self.langfuse_logger.end_trace(
                        trace,
                        output={"corrected_data": corrected_data},
                        status="success"
                    )
                    
                    logger.info("Event data corrected successfully")
                    return {
                        'success': True,
                        'corrected_data': corrected_data
                    }
                else:
                    raise Exception("No response from Gemini")
                    
            except Exception as e:
                # Log failed correction
                self.langfuse_logger.end_trace(
                    trace,
                    error=str(e),
                    status="error"
                )
                raise e
                
        except Exception as e:
            logger.error(f"Error correcting event data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_autofill_suggestions(self, prompt: str) -> Dict[str, Any]:
        """Generate autofill suggestions using LLM"""
        try:
            if not self.model:
                return {'success': False, 'error': 'Gemini model not initialized'}
            
            # Start Langfuse trace
            trace = self.langfuse_logger.start_trace(
                name="generate_autofill_suggestions",
                input={"prompt": prompt}
            )
            
            try:
                # Prepare the prompt
                full_prompt = self._build_autofill_prompt(prompt)
                
                # Generate response
                response = self._generate_with_retry(full_prompt)
                
                if response:
                    # Parse the response
                    suggestions = self._parse_autofill_response(response.text)
                    
                    # Log successful generation
                    self.langfuse_logger.end_trace(
                        trace,
                        output={"suggestions": suggestions},
                        status="success"
                    )
                    
                    logger.info("Autofill suggestions generated successfully")
                    return {
                        'success': True,
                        'suggestions': suggestions
                    }
                else:
                    raise Exception("No response from Gemini")
                    
            except Exception as e:
                # Log failed generation
                self.langfuse_logger.end_trace(
                    trace,
                    error=str(e),
                    status="error"
                )
                raise e
                
        except Exception as e:
            logger.error(f"Error generating autofill suggestions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[Any]:
        """Generate response with retry logic"""
        for attempt in range(max_retries):
            try:
                # Configure safety settings
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
                
                # Generate content
                response = self.model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=2048,
                    )
                )
                
                return response
                
            except Exception as e:
                logger.warning(f"Gemini generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
        
        return None
    
    def _build_form_generation_prompt(self, user_prompt: str) -> str:
        """Build prompt for form field generation"""
        system_prompt = """
        You are an expert form designer. Generate appropriate form fields for events based on the provided information.
        
        Return your response as a JSON object with the following structure:
        {
            "fields": [
                {
                    "name": "field_name",
                    "type": "field_type",
                    "label": "Field Label",
                    "required": true/false,
                    "placeholder": "Placeholder text",
                    "validation": {
                        "min_length": 0,
                        "max_length": 100,
                        "pattern": "regex_pattern"
                    },
                    "options": ["option1", "option2"] // for select fields
                }
            ]
        }
        
        Field types should be one of: text, email, tel, number, date, time, datetime, textarea, select, checkbox, radio
        
        Consider the event type and context when generating fields. Include relevant fields like:
        - Contact information (name, email, phone)
        - Event-specific fields based on type
        - Optional fields that might be useful
        
        User prompt:
        """
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _build_layout_generation_prompt(self, user_prompt: str) -> str:
        """Build prompt for layout generation"""
        system_prompt = """
        You are an expert UI/UX designer. Generate an improved form layout based on the provided information.
        
        Return your response as a JSON object with the following structure:
        {
            "layout": {
                "sections": [
                    {
                        "title": "Section Title",
                        "fields": ["field1", "field2"],
                        "columns": 1,
                        "order": 1
                    }
                ],
                "styling": {
                    "theme": "modern",
                    "spacing": "comfortable",
                    "alignment": "left"
                }
            }
        }
        
        Consider usability, accessibility, and visual hierarchy when designing the layout.
        
        User prompt:
        """
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _build_correction_prompt(self, user_prompt: str) -> str:
        """Build prompt for data correction"""
        system_prompt = """
        You are a data validation expert. Correct the provided event data to fix validation errors.
        
        Return your response as a JSON object with the corrected data. Preserve as much of the original data as possible while fixing the errors.
        
        Guidelines:
        - Fix obvious typos and formatting issues
        - Add missing required fields with reasonable defaults
        - Convert data types where appropriate
        - Remove invalid data rather than guessing
        - Maintain the original structure
        
        User prompt:
        """
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _build_autofill_prompt(self, user_prompt: str) -> str:
        """Build prompt for autofill suggestions"""
        system_prompt = """
        You are an expert at understanding context and providing relevant suggestions.
        
        Based on the event information provided, suggest appropriate values for the specified fields.
        
        Return your response as a JSON object with field names as keys and suggested values as values:
        {
            "field_name": "suggested_value",
            "another_field": "another_suggestion"
        }
        
        Make suggestions that are:
        - Contextually relevant to the event
        - Professional and appropriate
        - Specific to the event type and details
        
        User prompt:
        """
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _parse_form_fields_response(self, response_text: str) -> Dict[str, Any]:
        """Parse form fields from LLM response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Validate structure
                if 'fields' in parsed and isinstance(parsed['fields'], list):
                    return parsed
                else:
                    # Fallback: create basic structure
                    return {
                        'fields': [
                            {
                                'name': 'name',
                                'type': 'text',
                                'label': 'Name',
                                'required': True
                            },
                            {
                                'name': 'email',
                                'type': 'email',
                                'label': 'Email',
                                'required': True
                            }
                        ]
                    }
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse form fields response: {str(e)}")
            # Return default form fields
            return {
                'fields': [
                    {
                        'name': 'name',
                        'type': 'text',
                        'label': 'Name',
                        'required': True
                    },
                    {
                        'name': 'email',
                        'type': 'email',
                        'label': 'Email',
                        'required': True
                    }
                ]
            }
    
    def _parse_layout_response(self, response_text: str) -> Dict[str, Any]:
        """Parse layout from LLM response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Validate structure
                if 'layout' in parsed:
                    return parsed['layout']
                else:
                    return parsed
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse layout response: {str(e)}")
            # Return default layout
            return {
                'sections': [
                    {
                        'title': 'Event Information',
                        'fields': ['title', 'description', 'event_type'],
                        'columns': 1,
                        'order': 1
                    }
                ],
                'styling': {
                    'theme': 'modern',
                    'spacing': 'comfortable',
                    'alignment': 'left'
                }
            }
    
    def _parse_correction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse corrected data from LLM response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse correction response: {str(e)}")
            return {}
    
    def _parse_autofill_response(self, response_text: str) -> Dict[str, Any]:
        """Parse autofill suggestions from LLM response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"Failed to parse autofill response: {str(e)}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check Gemini API health"""
        try:
            if not self.model:
                return {'success': False, 'error': 'Gemini model not initialized'}
            
            # Test with a simple prompt
            test_prompt = "Say 'Hello, I am working correctly.'"
            response = self._generate_with_retry(test_prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'status': 'healthy',
                    'model': self.model_name
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from Gemini API'
                }
                
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'unhealthy'
            }
