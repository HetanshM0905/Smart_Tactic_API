from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from models.schemas import ChatHistory, WorkflowSchema, PromptTemplate

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface"""
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    def update(self, id: str, entity: T) -> Optional[T]:
        """Update existing entity"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[T]:
        """List all entities"""
        pass


class ChatRepository(BaseRepository[ChatHistory]):
    """Repository interface for chat operations"""
    
    @abstractmethod
    def get_chat_history(self, session_id: str) -> Optional[ChatHistory]:
        """Get chat history by session ID"""
        pass
    
    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str) -> None:
        """Save a message to chat history"""
        pass
    
    @abstractmethod
    def save_form_object(self, session_id: str, form_object: Dict[str, Any]) -> None:
        """Save form object to session"""
        pass


class WorkflowRepository(BaseRepository[WorkflowSchema]):
    """Repository interface for workflow operations"""
    
    @abstractmethod
    def get_form_options(self, workflow_id: str) -> Optional[WorkflowSchema]:
        """Get workflow/form schema by ID"""
        pass


class PromptRepository(BaseRepository[PromptTemplate]):
    """Repository interface for prompt operations"""
    
    @abstractmethod
    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Get prompt template by ID"""
        pass


class DataRepository(BaseRepository[Dict[str, Any]]):
    """Repository interface for data operations"""
    
    @abstractmethod
    def get_suggested_data(self, id: str) -> Optional[Dict[str, Any]]:
        """Get suggested data by ID"""
        pass
