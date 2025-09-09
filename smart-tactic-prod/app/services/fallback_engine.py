"""
Fallback engine for handling validation failures and error recovery
Provides intelligent fallback mechanisms when primary processing fails
"""

import json
from typing import Dict, Any, List, Optional
from app.integrations.gemini_llm import GeminiLLM
from app.integrations.sql_client import SQLClient
from app.utils.logger import get_logger
from app.utils.validators import ValidationResult

logger = get_logger(__name__)

class FallbackEngine:
    """Handles fallback logic for failed validations and processing errors"""
    
    def __init__(self):
        self.gemini_llm = GeminiLLM()
        self.sql_client = SQLClient()
        self.fallback_rules = self._load_fallback_rules()
    
    def handle_invalid_event(self, payload: Dict[str, Any], validation_errors: List[str]) -> Dict[str, Any]:
        """Handle events that failed validation"""
        try:
            logger.info(f"Handling invalid event with {len(validation_errors)} errors")
            
            # Try to correct the payload using LLM
            correction_result = self._attempt_llm_correction(payload, validation_errors)
            if correction_result['success']:
                return {
                    'success': True,
                    'corrected_payload': correction_result['corrected_payload'],
                    'correction_method': 'llm',
                    'original_errors': validation_errors
                }
            
            # Try rule-based correction
            rule_correction = self._attempt_rule_based_correction(payload, validation_errors)
            if rule_correction['success']:
                return {
                    'success': True,
                    'corrected_payload': rule_correction['corrected_payload'],
                    'correction_method': 'rules',
                    'original_errors': validation_errors
                }
            
            # Try template-based correction
            template_correction = self._attempt_template_correction(payload, validation_errors)
            if template_correction['success']:
                return {
                    'success': True,
                    'corrected_payload': template_correction['corrected_payload'],
                    'correction_method': 'template',
                    'original_errors': validation_errors
                }
            
            # All correction methods failed
            logger.error(f"All fallback correction methods failed for event")
            return {
                'success': False,
                'error': 'Unable to correct validation errors',
                'original_errors': validation_errors
            }
            
        except Exception as e:
            logger.error(f"Error in fallback engine: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_errors': validation_errors
            }
    
    def process_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process event through fallback engine with full error handling"""
        try:
            # Log the fallback processing attempt
            self._log_fallback_attempt(payload)
            
            # Apply fallback rules
            processed_payload = self._apply_fallback_rules(payload)
            
            # Validate the processed payload
            validation_result = self._validate_processed_payload(processed_payload)
            
            if validation_result['valid']:
                # Store fallback result
                self._store_fallback_result(payload, processed_payload, 'success')
                
                return {
                    'success': True,
                    'processed_payload': processed_payload,
                    'fallback_applied': True
                }
            else:
                # Try additional fallback strategies
                additional_correction = self._apply_additional_fallback_strategies(
                    processed_payload, validation_result['errors']
                )
                
                if additional_correction['success']:
                    self._store_fallback_result(payload, additional_correction['payload'], 'success')
                    return {
                        'success': True,
                        'processed_payload': additional_correction['payload'],
                        'fallback_applied': True
                    }
                else:
                    self._store_fallback_result(payload, processed_payload, 'failed')
                    return {
                        'success': False,
                        'error': 'Fallback processing failed',
                        'validation_errors': validation_result['errors']
                    }
                    
        except Exception as e:
            logger.error(f"Error in fallback processing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _attempt_llm_correction(self, payload: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Attempt to correct payload using LLM"""
        try:
            correction_prompt = self._build_correction_prompt(payload, errors)
            result = self.gemini_llm.correct_event_data(correction_prompt)
            
            if result['success']:
                return {
                    'success': True,
                    'corrected_payload': result['corrected_data']
                }
            else:
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            logger.error(f"LLM correction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _attempt_rule_based_correction(self, payload: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Attempt rule-based correction using predefined rules"""
        try:
            corrected_payload = payload.copy()
            
            for error in errors:
                if 'missing required field' in error.lower():
                    field_name = self._extract_field_name_from_error(error)
                    if field_name:
                        corrected_payload[field_name] = self._get_default_value_for_field(field_name)
                
                elif 'invalid format' in error.lower():
                    field_name = self._extract_field_name_from_error(error)
                    if field_name and field_name in corrected_payload:
                        corrected_payload[field_name] = self._fix_field_format(
                            corrected_payload[field_name], field_name
                        )
                
                elif 'invalid value' in error.lower():
                    field_name = self._extract_field_name_from_error(error)
                    if field_name and field_name in corrected_payload:
                        corrected_payload[field_name] = self._get_valid_value_for_field(field_name)
            
            return {
                'success': True,
                'corrected_payload': corrected_payload
            }
            
        except Exception as e:
            logger.error(f"Rule-based correction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _attempt_template_correction(self, payload: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Attempt correction using event templates"""
        try:
            event_type = payload.get('event_type', 'general')
            template = self._get_event_template(event_type)
            
            if template:
                corrected_payload = template.copy()
                corrected_payload.update(payload)  # Preserve original data where possible
                
                return {
                    'success': True,
                    'corrected_payload': corrected_payload
                }
            else:
                return {'success': False, 'error': 'No template found'}
                
        except Exception as e:
            logger.error(f"Template correction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _build_correction_prompt(self, payload: Dict[str, Any], errors: List[str]) -> str:
        """Build prompt for LLM correction"""
        errors_text = '\n'.join(errors)
        
        prompt = f"""
        The following event data failed validation with these errors:
        {errors_text}
        
        Original payload:
        {json.dumps(payload, indent=2)}
        
        Please correct the payload to fix the validation errors while preserving as much of the original data as possible.
        Return only the corrected JSON payload.
        """
        
        return prompt
    
    def _apply_fallback_rules(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply predefined fallback rules to the payload"""
        processed_payload = payload.copy()
        
        for rule in self.fallback_rules:
            if self._rule_applies(rule, processed_payload):
                processed_payload = self._apply_rule(rule, processed_payload)
        
        return processed_payload
    
    def _apply_additional_fallback_strategies(self, payload: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Apply additional fallback strategies for complex cases"""
        try:
            # Strategy 1: Field mapping correction
            mapped_payload = self._apply_field_mapping(payload)
            
            # Strategy 2: Data type conversion
            converted_payload = self._apply_data_type_conversion(mapped_payload)
            
            # Strategy 3: Default value injection
            final_payload = self._inject_default_values(converted_payload)
            
            return {
                'success': True,
                'payload': final_payload
            }
            
        except Exception as e:
            logger.error(f"Additional fallback strategies failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _load_fallback_rules(self) -> List[Dict[str, Any]]:
        """Load fallback rules from database or configuration"""
        # This would typically load from a database or config file
        return [
            {
                'condition': 'missing_title',
                'action': 'set_default_title',
                'value': 'Untitled Event'
            },
            {
                'condition': 'missing_event_type',
                'action': 'set_default_type',
                'value': 'general'
            },
            {
                'condition': 'invalid_email',
                'action': 'remove_invalid_email',
                'value': None
            }
        ]
    
    def _rule_applies(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Check if a fallback rule applies to the payload"""
        condition = rule['condition']
        
        if condition == 'missing_title':
            return not payload.get('title')
        elif condition == 'missing_event_type':
            return not payload.get('event_type')
        elif condition == 'invalid_email':
            email = payload.get('email', '')
            return email and '@' not in email
        
        return False
    
    def _apply_rule(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a fallback rule to the payload"""
        action = rule['action']
        value = rule['value']
        
        if action == 'set_default_title':
            payload['title'] = value
        elif action == 'set_default_type':
            payload['event_type'] = value
        elif action == 'remove_invalid_email':
            payload.pop('email', None)
        
        return payload
    
    def _extract_field_name_from_error(self, error: str) -> Optional[str]:
        """Extract field name from validation error message"""
        # Simple extraction logic - could be enhanced with regex
        if 'field' in error.lower():
            parts = error.split()
            for i, part in enumerate(parts):
                if part.lower() == 'field' and i + 1 < len(parts):
                    return parts[i + 1].strip('"\'')
        return None
    
    def _get_default_value_for_field(self, field_name: str) -> Any:
        """Get default value for a field"""
        defaults = {
            'title': 'Untitled Event',
            'description': '',
            'event_type': 'general',
            'email': '',
            'phone': '',
            'date': None
        }
        return defaults.get(field_name, '')
    
    def _fix_field_format(self, value: Any, field_name: str) -> Any:
        """Fix field format based on field type"""
        if field_name == 'email' and isinstance(value, str):
            # Basic email format fix
            return value.strip().lower()
        elif field_name == 'phone' and isinstance(value, str):
            # Basic phone format fix
            return ''.join(filter(str.isdigit, value))
        
        return value
    
    def _get_valid_value_for_field(self, field_name: str) -> Any:
        """Get a valid value for a field"""
        return self._get_default_value_for_field(field_name)
    
    def _get_event_template(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get event template for a specific type"""
        templates = {
            'conference': {
                'event_type': 'conference',
                'title': '',
                'description': '',
                'venue': '',
                'date': None,
                'capacity': 100
            },
            'workshop': {
                'event_type': 'workshop',
                'title': '',
                'description': '',
                'instructor': '',
                'duration': 2,
                'materials': []
            },
            'meeting': {
                'event_type': 'meeting',
                'title': '',
                'description': '',
                'agenda': [],
                'attendees': []
            }
        }
        return templates.get(event_type)
    
    def _apply_field_mapping(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field name mapping for common variations"""
        field_mappings = {
            'name': 'title',
            'event_name': 'title',
            'type': 'event_type',
            'desc': 'description',
            'details': 'description'
        }
        
        mapped_payload = payload.copy()
        for old_name, new_name in field_mappings.items():
            if old_name in mapped_payload and new_name not in mapped_payload:
                mapped_payload[new_name] = mapped_payload.pop(old_name)
        
        return mapped_payload
    
    def _apply_data_type_conversion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data type conversions"""
        converted_payload = payload.copy()
        
        # Convert string numbers to integers where appropriate
        numeric_fields = ['capacity', 'duration', 'price']
        for field in numeric_fields:
            if field in converted_payload and isinstance(converted_payload[field], str):
                try:
                    converted_payload[field] = int(converted_payload[field])
                except ValueError:
                    pass
        
        return converted_payload
    
    def _inject_default_values(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inject default values for missing required fields"""
        required_fields = {
            'title': 'Untitled Event',
            'event_type': 'general',
            'description': '',
            'status': 'draft'
        }
        
        for field, default_value in required_fields.items():
            if field not in payload or not payload[field]:
                payload[field] = default_value
        
        return payload
    
    def _validate_processed_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the processed payload"""
        # This would use the same validation logic as the main validator
        # For now, return a simple validation
        required_fields = ['title', 'event_type']
        errors = []
        
        for field in required_fields:
            if field not in payload or not payload[field]:
                errors.append(f"Missing required field: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _log_fallback_attempt(self, payload: Dict[str, Any]) -> None:
        """Log fallback processing attempt"""
        logger.info(f"Fallback engine processing event: {payload.get('title', 'Unknown')}")
    
    def _store_fallback_result(self, original_payload: Dict[str, Any], 
                             processed_payload: Dict[str, Any], 
                             status: str) -> None:
        """Store fallback processing result"""
        try:
            result_data = {
                'original_payload': original_payload,
                'processed_payload': processed_payload,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store in database for analysis
            self.sql_client.store_fallback_result(result_data)
            
        except Exception as e:
            logger.error(f"Failed to store fallback result: {str(e)}")
