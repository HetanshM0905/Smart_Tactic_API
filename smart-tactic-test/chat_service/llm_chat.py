import os
import google.generativeai as genai
from pydantic import BaseModel
from typing import List

class SuggestedButton(BaseModel):
    title: str
    id: str
    action: str

class GeminiResponse(BaseModel):
    markdown: str
    field_data: int
    suggested_buttons: List[SuggestedButton]

class LLMChat:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY not set in environment or passed to LLMChat')
        genai.configure(api_key=self.api_key)
        # Use the correct model name for text generation
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def get_response(self, prompt, chat_history=None, **kwargs):
        try:
            response = self.model.generate_content(prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "markdown": {"type": "string"},
                            "field_data": {"type": "integer"},
                            "suggested_buttons": {"type": "array", 
                            "items": {"type": "object", 
                            "properties": {"title": {"type": "string"}, "id": {"type": "string"}, "action": {"type": "string"}}, "required": ["title", "id", "action"]
                            }
                            }
                        },
                        "required": ["markdown", "field_data", "suggested_buttons"]
                    }})
            # If the response is an object, get the text attribute
            text = response.candidates[0].content.parts[0].text
            response = GeminiResponse.parse_raw(text)
            print(f"LLM Raw Response: {response}")
            return response
        except Exception as e:
            return {'response': f'LLM Error: {str(e)}', 'field_data': {}, 'suggested_buttons': []}
            # If the response is an object, get the text attribute
            if hasattr(response, 'text'):
                return {'response': response.text, 'field_data': {}, 'suggested_buttons': []}
            return response
        except Exception as e:
            return {'response': f'LLM Error: {str(e)}', 'field_data': {}, 'suggested_buttons': []}
