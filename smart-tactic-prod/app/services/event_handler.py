"""
Event handling service for Smart Tactics application
Manages event creation, updates, and form generation
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.integrations.firestore_client import FirestoreClient
from app.integrations.sql_client import SQLClient
from app.integrations.gemini_llm import GeminiLLM
from app.services.autofill_engine import AutofillEngine
from app.utils.logger import get_logger
from app.models.event_model import EventModel

logger = get_logger(__name__)

class EventHandler:
    """Handles event processing and form generation"""
    
    def __init__(self):
        self.firestore_client = FirestoreClient()
        self.sql_client = SQLClient()
        self.gemini_llm = GeminiLLM()
        self.autofill_engine = AutofillEngine()
    
    def create_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event with AI-powered form generation"""
        try:
            # Generate unique event ID
            event_id = str(uuid.uuid4())
            
            # Create event model
            event = EventModel(
                event_id=event_id,
                event_type=payload.get('event_type'),
                title=payload.get('title'),
                description=payload.get('description'),
                metadata=payload.get('metadata', {}),
                created_at=datetime.utcnow(),
                status='created'
            )
            
            # Generate form fields using LLM
            form_fields = self._generate_form_fields(payload)
            event.form_fields = form_fields
            
            # Apply autofill if applicable
            autofill_result = self.autofill_engine.apply_autofill(event, payload)
            if autofill_result['success']:
                event.form_fields = autofill_result['form_fields']
                logger.info(f"Autofill applied to event {event_id}")
            
            # Store in Firestore
            firestore_result = self.firestore_client.store_event(event.to_dict())
            if not firestore_result['success']:
                raise Exception(f"Failed to store in Firestore: {firestore_result['error']}")
            
            # Store structured data in AlloyDB
            sql_result = self.sql_client.store_event_metadata(event.to_metadata_dict())
            if not sql_result['success']:
                logger.warning(f"Failed to store metadata in AlloyDB: {sql_result['error']}")
            
            logger.info(f"Event created successfully: {event_id}")
            return {
                'success': True,
                'event_id': event_id,
                'form_fields': event.form_fields,
                'autofill_applied': autofill_result['success']
            }
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_event(self, event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event"""
        try:
            # Retrieve existing event
            existing_event = self.firestore_client.get_event(event_id)
            if not existing_event['success']:
                return {
                    'success': False,
                    'error': f"Event not found: {event_id}"
                }
            
            # Update event data
            event_data = existing_event['data']
            event_data.update(payload)
            event_data['updated_at'] = datetime.utcnow()
            event_data['status'] = 'updated'
            
            # Regenerate form fields if needed
            if self._should_regenerate_form(payload):
                form_fields = self._generate_form_fields(event_data)
                event_data['form_fields'] = form_fields
            
            # Apply autofill updates
            autofill_result = self.autofill_engine.apply_autofill_updates(event_data, payload)
            if autofill_result['success']:
                event_data['form_fields'] = autofill_result['form_fields']
            
            # Update in Firestore
            update_result = self.firestore_client.update_event(event_id, event_data)
            if not update_result['success']:
                raise Exception(f"Failed to update in Firestore: {update_result['error']}")
            
            # Update metadata in AlloyDB
            self.sql_client.update_event_metadata(event_id, event_data)
            
            logger.info(f"Event updated successfully: {event_id}")
            return {
                'success': True,
                'event_id': event_id,
                'form_fields': event_data.get('form_fields'),
                'autofill_applied': autofill_result['success']
            }
            
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_layout(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update form layout based on event data"""
        try:
            event_id = payload.get('event_id')
            if not event_id:
                return {
                    'success': False,
                    'error': 'Event ID is required for layout update'
                }
            
            # Get current event
            event_result = self.firestore_client.get_event(event_id)
            if not event_result['success']:
                return {
                    'success': False,
                    'error': f"Event not found: {event_id}"
                }
            
            event_data = event_result['data']
            
            # Generate new layout using LLM
            layout_prompt = self._build_layout_prompt(event_data, payload)
            layout_result = self.gemini_llm.generate_layout(layout_prompt)
            
            if layout_result['success']:
                new_layout = layout_result['layout']
                
                # Update event with new layout
                event_data['layout'] = new_layout
                event_data['layout_updated_at'] = datetime.utcnow()
                
                # Store updated event
                update_result = self.firestore_client.update_event(event_id, event_data)
                if update_result['success']:
                    logger.info(f"Layout updated for event {event_id}")
                    return {
                        'success': True,
                        'event_id': event_id,
                        'layout': new_layout
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Failed to update event: {update_result['error']}"
                    }
            else:
                return {
                    'success': False,
                    'error': f"Failed to generate layout: {layout_result['error']}"
                }
                
        except Exception as e:
            logger.error(f"Error updating layout: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_form_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate form fields using LLM"""
        try:
            prompt = self._build_form_generation_prompt(payload)
            result = self.gemini_llm.generate_event_fields(prompt)
            
            if result['success']:
                return result['fields']
            else:
                logger.warning(f"LLM form generation failed: {result['error']}")
                return self._get_default_form_fields(payload)
                
        except Exception as e:
            logger.error(f"Error generating form fields: {str(e)}")
            return self._get_default_form_fields(payload)
    
    def _build_form_generation_prompt(self, payload: Dict[str, Any]) -> str:
        """Build prompt for form field generation"""
        event_type = payload.get('event_type', 'general')
        title = payload.get('title', '')
        description = payload.get('description', '')
        
        prompt = f"""
        Generate form fields for a {event_type} event with the following details:
        Title: {title}
        Description: {description}
        
        Please return a JSON object with form fields that would be appropriate for this event.
        Include field types, labels, validation rules, and any relevant options.
        """
        
        return prompt
    
    def _build_layout_prompt(self, event_data: Dict[str, Any], payload: Dict[str, Any]) -> str:
        """Build prompt for layout generation"""
        current_layout = event_data.get('layout', {})
        layout_requirements = payload.get('layout_requirements', {})
        
        prompt = f"""
        Update the form layout for event: {event_data.get('title', '')}
        Current layout: {current_layout}
        Requirements: {layout_requirements}
        
        Generate an improved layout that meets the requirements while maintaining usability.
        """
        
        return prompt
    
    def _should_regenerate_form(self, payload: Dict[str, Any]) -> bool:
        """Determine if form fields should be regenerated"""
        regenerate_triggers = ['event_type', 'title', 'description', 'category']
        return any(key in payload for key in regenerate_triggers)
    
    def _get_default_form_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get default form fields when LLM generation fails"""
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
                },
                {
                    'name': 'phone',
                    'type': 'tel',
                    'label': 'Phone Number',
                    'required': False
                }
            ]
        }
