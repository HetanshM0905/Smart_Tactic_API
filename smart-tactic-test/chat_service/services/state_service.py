from typing import Dict, Any, Optional
import json
from datetime import datetime

from repositories.base import SessionRepository
from exceptions import ValidationException, DatabaseException
from utils.logger import logger


class StateService:
    """Service for managing form state operations"""
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
        logger.info("StateService initialized")
    
    def get_state(self, session_id: str) -> Dict[str, Any]:
        """Get current state for a session from the user session."""
        try:
            user_session = self.session_repo.get_session(session_id)
            if user_session:
                return user_session.state
            return {}
        except Exception as e:
            logger.error(f"Failed to get state for session {session_id}: {e}")
            return {}
    
    def update_state(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update state with new field values and save it to the user session."""
        try:
            current_state = self.get_state(session_id)
            updated_state = {**current_state, **updates}

            self.session_repo.save_state(session_id, updated_state)

            logger.info(f"Updated state for session {session_id}: {list(updates.keys())}")
            return updated_state
        except Exception as e:
            logger.error(f"Failed to update state for session {session_id}: {e}")
            raise DatabaseException(f"Failed to update state: {e}")
    
    def clear_state(self, session_id: str) -> bool:
        """Clear the state for a given session."""
        try:
            self.session_repo.save_state(session_id, {})
            logger.info(f"Cleared state for session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear state for session {session_id}: {e}")
            return False
    
    def validate_field_update(self, field_id: str, value: Any, schema: Dict[str, Any]) -> bool:
        """Validate field update against schema"""
        try:
            if field_id not in schema:
                logger.warning(f"Field {field_id} not found in schema")
                return True  # Allow unknown fields for flexibility
            
            field_schema = schema[field_id]
            field_type = field_schema.get('type', 'string')
            
            # Basic type validation
            if field_type == 'string' and not isinstance(value, str):
                return False
            elif field_type == 'number' and not isinstance(value, (int, float)):
                return False
            elif field_type == 'boolean' and not isinstance(value, bool):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Field validation error: {e}")
            return False
    
    def get_form_completion_status(self, session_id: str, required_fields: list) -> Dict[str, Any]:
        """Get form completion status"""
        try:
            current_state = self.get_state(session_id)
            
            completed_fields = []
            missing_fields = []
            
            for field in required_fields:
                if field in current_state and current_state[field]:
                    completed_fields.append(field)
                else:
                    missing_fields.append(field)
            
            completion_percentage = (len(completed_fields) / len(required_fields)) * 100 if required_fields else 100
            
            return {
                'completed_fields': completed_fields,
                'missing_fields': missing_fields,
                'completion_percentage': round(completion_percentage, 2),
                'is_complete': len(missing_fields) == 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get completion status: {e}")
            return {
                'completed_fields': [],
                'missing_fields': required_fields,
                'completion_percentage': 0,
                'is_complete': False
            }
