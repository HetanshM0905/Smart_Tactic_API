from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum


class ActionType(str, Enum):
    """Available action types for suggested buttons"""
    UPDATE = "update"
    CHAT = "chat"


class SuggestedButton(BaseModel):
    """Model for suggested action buttons"""
    title: str = Field(..., min_length=1, max_length=100)
    action: ActionType
    field_data: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        use_enum_values = True


class ChatRequest(BaseModel):
    """Request model for chat API"""
    session_id: str = Field(default="default", min_length=1, max_length=100)
    question: str = Field(..., min_length=1, max_length=1000)
    workflow_id: str = Field(default="workflow1", min_length=1, max_length=50)
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat API"""
    response: str
    suggested_buttons: List[SuggestedButton] = Field(default_factory=list)
    session_id: str
    
    class Config:
        json_encoders = {
            SuggestedButton: lambda v: v.dict()
        }


class GeminiResponse(BaseModel):
    """Model for Gemini LLM response"""
    markdown: str
    field_data: Dict[str, Any] = Field(default_factory=dict)
    suggested_buttons: List[SuggestedButton] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """Model for individual chat messages"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = None


class ChatHistory(BaseModel):
    """Model for chat history"""
    session_id: str
    history: List[ChatMessage] = Field(default_factory=list)


class WorkflowSchema(BaseModel):
    """Model for workflow/form schema"""
    id: str
    name: str
    form_schema: Dict[str, Any] = Field(default_factory=dict)
    options : Dict[str, Any] = Field(default_factory=dict)
    schema : Dict[str, Any] = Field(default_factory=dict)


class PromptTemplate(BaseModel):
    """Model for prompt templates"""
    id: str
    text: str
    variables: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
