"""
Autofill engine for intelligent form field population
Uses rule-based logic and AI to auto-populate form fields
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.integrations.firestore_client import FirestoreClient
from app.integrations.sql_client import SQLClient
from app.integrations.gemini_llm import GeminiLLM
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AutofillEngine:
    """Handles intelligent autofill of form fields based on context and rules"""
    
    def __init__(self):
        self.firestore_client = FirestoreClient()
        self.sql_client = SQLClient()
        self.gemini_llm = GeminiLLM()
        self.autofill_rules = self._load_autofill_rules()
        self.cache = {}  # Simple in-memory cache for autofill data
    
    def apply_autofill(self, event: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply autofill to event form fields"""
        try:
            logger.info(f"Applying autofill to event: {event.event_id}")
            
            # Get current form fields
            form_fields = getattr(event, 'form_fields', {})
            if not form_fields:
                return {'success': False, 'error': 'No form fields to autofill'}
            
            # Apply autofill rules
            autofilled_fields = self._apply_autofill_rules(form_fields, payload)
            
            # Apply AI-powered autofill
            ai_autofilled = self._apply_ai_autofill(autofilled_fields, payload)
            
            # Apply cache-based autofill
            cache_autofilled = self._apply_cache_autofill(ai_autofilled, payload)
            
            # Update cache with new data
            self._update_autofill_cache(payload, cache_autofilled)
            
            logger.info(f"Autofill applied successfully to {len(cache_autofilled.get('fields', []))} fields")
            
            return {
                'success': True,
                'form_fields': cache_autofilled,
                'autofill_applied': True
            }
            
        except Exception as e:
            logger.error(f"Error applying autofill: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_autofill_updates(self, event_data: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply autofill updates to existing event data"""
        try:
            form_fields = event_data.get('form_fields', {})
            if not form_fields:
                return {'success': False, 'error': 'No form fields to update'}
            
            # Apply incremental autofill based on payload changes
            updated_fields = self._apply_incremental_autofill(form_fields, payload)
            
            return {
                'success': True,
                'form_fields': updated_fields,
                'autofill_applied': True
            }
            
        except Exception as e:
            logger.error(f"Error applying autofill updates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _apply_autofill_rules(self, form_fields: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rule-based autofill logic"""
        try:
            autofilled_fields = form_fields.copy()
            fields = autofilled_fields.get('fields', [])
            
            for field in fields:
                field_name = field.get('name', '')
                field_type = field.get('type', '')
                
                # Apply rules based on field name and type
                if self._should_autofill_field(field_name, field_type, payload):
                    autofill_value = self._get_autofill_value(field_name, field_type, payload)
                    if autofill_value is not None:
                        field['value'] = autofill_value
                        field['autofilled'] = True
                        field['autofill_source'] = 'rules'
            
            return autofilled_fields
            
        except Exception as e:
            logger.error(f"Error applying autofill rules: {str(e)}")
            return form_fields
    
    def _apply_ai_autofill(self, form_fields: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI-powered autofill using LLM"""
        try:
            # Identify fields that could benefit from AI autofill
            ai_candidates = self._identify_ai_autofill_candidates(form_fields, payload)
            
            if not ai_candidates:
                return form_fields
            
            # Generate autofill suggestions using LLM
            autofill_prompt = self._build_autofill_prompt(ai_candidates, payload)
            llm_result = self.gemini_llm.generate_autofill_suggestions(autofill_prompt)
            
            if llm_result['success']:
                suggestions = llm_result['suggestions']
                return self._apply_ai_suggestions(form_fields, suggestions)
            else:
                logger.warning(f"AI autofill failed: {llm_result['error']}")
                return form_fields
                
        except Exception as e:
            logger.error(f"Error applying AI autofill: {str(e)}")
            return form_fields
    
    def _apply_cache_autofill(self, form_fields: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cache-based autofill from previous similar events"""
        try:
            # Look for similar events in cache
            similar_events = self._find_similar_events(payload)
            
            if similar_events:
                # Extract common field values
                common_values = self._extract_common_values(similar_events)
                
                # Apply common values to form fields
                return self._apply_common_values(form_fields, common_values)
            
            return form_fields
            
        except Exception as e:
            logger.error(f"Error applying cache autofill: {str(e)}")
            return form_fields
    
    def _apply_incremental_autofill(self, form_fields: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply incremental autofill based on payload changes"""
        try:
            updated_fields = form_fields.copy()
            fields = updated_fields.get('fields', [])
            
            # Check for changes that might trigger autofill
            for change_key, change_value in payload.items():
                if self._is_autofill_trigger(change_key, change_value):
                    # Find related fields that could be autofilled
                    related_fields = self._find_related_fields(change_key, fields)
                    
                    for field in related_fields:
                        if not field.get('value') or field.get('autofilled'):
                            autofill_value = self._get_related_autofill_value(
                                change_key, change_value, field['name']
                            )
                            if autofill_value is not None:
                                field['value'] = autofill_value
                                field['autofilled'] = True
                                field['autofill_source'] = 'incremental'
            
            return updated_fields
            
        except Exception as e:
            logger.error(f"Error applying incremental autofill: {str(e)}")
            return form_fields
    
    def _should_autofill_field(self, field_name: str, field_type: str, payload: Dict[str, Any]) -> bool:
        """Determine if a field should be autofilled"""
        # Check if field already has a value
        if field_name in payload and payload[field_name]:
            return False
        
        # Check autofill rules
        for rule in self.autofill_rules:
            if self._rule_matches_field(rule, field_name, field_type):
                return True
        
        return False
    
    def _get_autofill_value(self, field_name: str, field_type: str, payload: Dict[str, Any]) -> Any:
        """Get autofill value for a field"""
        # Check rules first
        for rule in self.autofill_rules:
            if self._rule_matches_field(rule, field_name, field_type):
                return self._evaluate_rule(rule, payload)
        
        # Check for common patterns
        if field_name == 'email' and 'contact_email' in payload:
            return payload['contact_email']
        elif field_name == 'phone' and 'contact_phone' in payload:
            return payload['contact_phone']
        elif field_name == 'venue' and 'location' in payload:
            return payload['location']
        
        return None
    
    def _identify_ai_autofill_candidates(self, form_fields: Dict[str, Any], payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify fields that could benefit from AI autofill"""
        candidates = []
        fields = form_fields.get('fields', [])
        
        for field in fields:
            field_name = field.get('name', '')
            field_type = field.get('type', '')
            
            # Look for fields that are empty and could benefit from AI
            if (not field.get('value') and 
                field_type in ['text', 'textarea'] and 
                field_name in ['description', 'summary', 'notes', 'details']):
                candidates.append(field)
        
        return candidates
    
    def _build_autofill_prompt(self, candidates: List[Dict[str, Any]], payload: Dict[str, Any]) -> str:
        """Build prompt for AI autofill"""
        candidate_info = []
        for candidate in candidates:
            candidate_info.append(f"- {candidate['name']}: {candidate.get('label', '')}")
        
        prompt = f"""
        Based on the following event information, provide autofill suggestions for these fields:
        
        Event Information:
        Title: {payload.get('title', '')}
        Type: {payload.get('event_type', '')}
        Description: {payload.get('description', '')}
        
        Fields to autofill:
        {chr(10).join(candidate_info)}
        
        Please provide appropriate values for each field based on the event context.
        Return as JSON with field names as keys and suggested values as values.
        """
        
        return prompt
    
    def _apply_ai_suggestions(self, form_fields: Dict[str, Any], suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI-generated suggestions to form fields"""
        updated_fields = form_fields.copy()
        fields = updated_fields.get('fields', [])
        
        for field in fields:
            field_name = field.get('name', '')
            if field_name in suggestions and not field.get('value'):
                field['value'] = suggestions[field_name]
                field['autofilled'] = True
                field['autofill_source'] = 'ai'
        
        return updated_fields
    
    def _find_similar_events(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar events in cache for autofill reference"""
        try:
            event_type = payload.get('event_type', '')
            similar_events = []
            
            # Search cache for similar events
            for cached_event in self.cache.values():
                if (cached_event.get('event_type') == event_type and 
                    cached_event.get('form_fields')):
                    similar_events.append(cached_event)
            
            # Limit to most recent 5 similar events
            return similar_events[-5:]
            
        except Exception as e:
            logger.error(f"Error finding similar events: {str(e)}")
            return []
    
    def _extract_common_values(self, similar_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common field values from similar events"""
        common_values = {}
        
        if not similar_events:
            return common_values
        
        # Get all field names from similar events
        all_fields = set()
        for event in similar_events:
            form_fields = event.get('form_fields', {}).get('fields', [])
            for field in form_fields:
                all_fields.add(field.get('name', ''))
        
        # Find common values
        for field_name in all_fields:
            values = []
            for event in similar_events:
                form_fields = event.get('form_fields', {}).get('fields', [])
                for field in form_fields:
                    if field.get('name') == field_name and field.get('value'):
                        values.append(field['value'])
            
            # If most events have the same value, use it as common value
            if values:
                most_common = max(set(values), key=values.count)
                if values.count(most_common) >= len(values) * 0.6:  # 60% threshold
                    common_values[field_name] = most_common
        
        return common_values
    
    def _apply_common_values(self, form_fields: Dict[str, Any], common_values: Dict[str, Any]) -> Dict[str, Any]:
        """Apply common values to form fields"""
        updated_fields = form_fields.copy()
        fields = updated_fields.get('fields', [])
        
        for field in fields:
            field_name = field.get('name', '')
            if field_name in common_values and not field.get('value'):
                field['value'] = common_values[field_name]
                field['autofilled'] = True
                field['autofill_source'] = 'cache'
        
        return updated_fields
    
    def _is_autofill_trigger(self, change_key: str, change_value: Any) -> bool:
        """Check if a change should trigger autofill"""
        triggers = ['event_type', 'title', 'category', 'venue']
        return change_key in triggers and change_value
    
    def _find_related_fields(self, trigger_key: str, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find fields related to a trigger change"""
        related_fields = []
        
        # Define relationships
        relationships = {
            'event_type': ['description', 'requirements', 'materials'],
            'title': ['description', 'summary'],
            'venue': ['address', 'capacity', 'amenities'],
            'category': ['tags', 'keywords']
        }
        
        related_field_names = relationships.get(trigger_key, [])
        
        for field in fields:
            if field.get('name') in related_field_names:
                related_fields.append(field)
        
        return related_fields
    
    def _get_related_autofill_value(self, trigger_key: str, trigger_value: Any, field_name: str) -> Any:
        """Get autofill value for a field based on a related trigger"""
        # This would typically use a more sophisticated mapping
        # For now, return some basic defaults
        defaults = {
            'description': f"Description for {trigger_value}",
            'summary': f"Summary of {trigger_value}",
            'address': "Default address",
            'capacity': 100,
            'tags': [trigger_value]
        }
        
        return defaults.get(field_name)
    
    def _update_autofill_cache(self, payload: Dict[str, Any], form_fields: Dict[str, Any]) -> None:
        """Update autofill cache with new data"""
        try:
            cache_key = f"{payload.get('event_type', 'general')}_{payload.get('title', '')}"
            self.cache[cache_key] = {
                'payload': payload,
                'form_fields': form_fields,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Limit cache size
            if len(self.cache) > 100:
                # Remove oldest entries
                oldest_keys = sorted(self.cache.keys())[:20]
                for key in oldest_keys:
                    del self.cache[key]
                    
        except Exception as e:
            logger.error(f"Error updating autofill cache: {str(e)}")
    
    def _load_autofill_rules(self) -> List[Dict[str, Any]]:
        """Load autofill rules from database or configuration"""
        # This would typically load from a database
        return [
            {
                'field_name': 'email',
                'field_type': 'email',
                'condition': 'contact_email_exists',
                'action': 'copy_from_contact_email'
            },
            {
                'field_name': 'phone',
                'field_type': 'tel',
                'condition': 'contact_phone_exists',
                'action': 'copy_from_contact_phone'
            },
            {
                'field_name': 'venue',
                'field_type': 'text',
                'condition': 'location_exists',
                'action': 'copy_from_location'
            }
        ]
    
    def _rule_matches_field(self, rule: Dict[str, Any], field_name: str, field_type: str) -> bool:
        """Check if a rule matches a field"""
        return (rule.get('field_name') == field_name and 
                rule.get('field_type') == field_type)
    
    def _evaluate_rule(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> Any:
        """Evaluate an autofill rule"""
        action = rule.get('action', '')
        
        if action == 'copy_from_contact_email':
            return payload.get('contact_email')
        elif action == 'copy_from_contact_phone':
            return payload.get('contact_phone')
        elif action == 'copy_from_location':
            return payload.get('location')
        
        return None
