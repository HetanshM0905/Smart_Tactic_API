"""
Validation utilities for event data and API requests
Provides comprehensive validation with detailed error reporting
"""

import re
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    """Custom validation error with detailed information"""
    
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self, valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str, field: str = None, code: str = None):
        """Add a validation error"""
        error_info = {
            'message': message,
            'field': field,
            'code': code
        }
        self.errors.append(error_info)
        self.valid = False
    
    def add_warning(self, message: str, field: str = None):
        """Add a validation warning"""
        warning_info = {
            'message': message,
            'field': field
        }
        self.warnings.append(warning_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings
        }

def validate_event_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate event payload with comprehensive checks"""
    result = ValidationResult()
    
    try:
        # Check if payload is a dictionary
        if not isinstance(payload, dict):
            result.add_error("Payload must be a JSON object", code="INVALID_TYPE")
            return result.to_dict()
        
        # Validate required fields
        _validate_required_fields(payload, result)
        
        # Validate field types and formats
        _validate_field_types(payload, result)
        
        # Validate field values
        _validate_field_values(payload, result)
        
        # Validate business rules
        _validate_business_rules(payload, result)
        
        # Log validation result
        if result.valid:
            logger.info(f"Event payload validation passed: {payload.get('title', 'Unknown')}")
        else:
            logger.warning(f"Event payload validation failed with {len(result.errors)} errors")
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        result.add_error(f"Validation error: {str(e)}", code="VALIDATION_ERROR")
        return result.to_dict()

def _validate_required_fields(payload: Dict[str, Any], result: ValidationResult):
    """Validate required fields are present"""
    required_fields = ['title', 'event_type']
    
    for field in required_fields:
        if field not in payload or not payload[field]:
            result.add_error(f"Missing required field: {field}", field=field, code="MISSING_REQUIRED")

def _validate_field_types(payload: Dict[str, Any], result: ValidationResult):
    """Validate field types"""
    field_type_validators = {
        'title': (str, "Title must be a string"),
        'description': (str, "Description must be a string"),
        'event_type': (str, "Event type must be a string"),
        'status': (str, "Status must be a string"),
        'capacity': (int, "Capacity must be an integer"),
        'duration': (int, "Duration must be an integer"),
        'price': (Union[int, float], "Price must be a number"),
        'date': (Union[str, datetime, date], "Date must be a valid date"),
        'metadata': (dict, "Metadata must be an object"),
        'form_fields': (dict, "Form fields must be an object"),
        'layout': (dict, "Layout must be an object")
    }
    
    for field, (expected_type, error_message) in field_type_validators.items():
        if field in payload:
            value = payload[field]
            if not isinstance(value, expected_type):
                result.add_error(error_message, field=field, code="INVALID_TYPE")

def _validate_field_values(payload: Dict[str, Any], result: ValidationResult):
    """Validate field values and formats"""
    
    # Validate title
    if 'title' in payload:
        title = payload['title']
        if isinstance(title, str):
            if len(title.strip()) < 3:
                result.add_error("Title must be at least 3 characters long", field='title', code="TOO_SHORT")
            elif len(title) > 200:
                result.add_error("Title must be less than 200 characters", field='title', code="TOO_LONG")
    
    # Validate description
    if 'description' in payload:
        description = payload['description']
        if isinstance(description, str) and len(description) > 2000:
            result.add_error("Description must be less than 2000 characters", field='description', code="TOO_LONG")
    
    # Validate event type
    if 'event_type' in payload:
        event_type = payload['event_type']
        if isinstance(event_type, str):
            valid_types = ['conference', 'workshop', 'meeting', 'seminar', 'webinar', 'general']
            if event_type not in valid_types:
                result.add_warning(f"Unknown event type: {event_type}. Valid types: {', '.join(valid_types)}", field='event_type')
    
    # Validate status
    if 'status' in payload:
        status = payload['status']
        if isinstance(status, str):
            valid_statuses = ['draft', 'published', 'cancelled', 'completed']
            if status not in valid_statuses:
                result.add_error(f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}", field='status', code="INVALID_VALUE")
    
    # Validate capacity
    if 'capacity' in payload:
        capacity = payload['capacity']
        if isinstance(capacity, int):
            if capacity < 1:
                result.add_error("Capacity must be at least 1", field='capacity', code="INVALID_VALUE")
            elif capacity > 10000:
                result.add_error("Capacity must be less than 10,000", field='capacity', code="INVALID_VALUE")
    
    # Validate duration
    if 'duration' in payload:
        duration = payload['duration']
        if isinstance(duration, int):
            if duration < 0:
                result.add_error("Duration must be non-negative", field='duration', code="INVALID_VALUE")
            elif duration > 24:
                result.add_warning("Duration is unusually long (>24 hours)", field='duration')
    
    # Validate price
    if 'price' in payload:
        price = payload['price']
        if isinstance(price, (int, float)):
            if price < 0:
                result.add_error("Price must be non-negative", field='price', code="INVALID_VALUE")
    
    # Validate email
    if 'email' in payload:
        email = payload['email']
        if isinstance(email, str) and email:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                result.add_error(f"Invalid email format: {str(e)}", field='email', code="INVALID_FORMAT")
    
    # Validate phone
    if 'phone' in payload:
        phone = payload['phone']
        if isinstance(phone, str) and phone:
            phone_pattern = re.compile(r'^[\+]?[1-9][\d]{0,15}$')
            if not phone_pattern.match(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                result.add_error("Invalid phone number format", field='phone', code="INVALID_FORMAT")
    
    # Validate date
    if 'date' in payload:
        date_value = payload['date']
        if isinstance(date_value, str):
            try:
                datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                result.add_error("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)", field='date', code="INVALID_FORMAT")
        elif isinstance(date_value, (datetime, date)):
            if isinstance(date_value, datetime) and date_value < datetime.now():
                result.add_warning("Event date is in the past", field='date')

def _validate_business_rules(payload: Dict[str, Any], result: ValidationResult):
    """Validate business rules and constraints"""
    
    # Rule: Conference events should have capacity
    if payload.get('event_type') == 'conference':
        if 'capacity' not in payload or not payload['capacity']:
            result.add_warning("Conference events typically require a capacity", field='capacity')
    
    # Rule: Workshop events should have duration
    if payload.get('event_type') == 'workshop':
        if 'duration' not in payload or not payload['duration']:
            result.add_warning("Workshop events typically require a duration", field='duration')
    
    # Rule: Paid events should have price
    if payload.get('status') == 'published' and payload.get('event_type') in ['conference', 'workshop']:
        if 'price' not in payload or payload['price'] is None:
            result.add_warning("Published events typically require a price", field='price')
    
    # Rule: Check for required contact information
    if payload.get('status') == 'published':
        has_contact = any(field in payload for field in ['email', 'phone', 'contact_email', 'contact_phone'])
        if not has_contact:
            result.add_warning("Published events should have contact information", field='contact')
    
    # Rule: Validate metadata structure
    if 'metadata' in payload and isinstance(payload['metadata'], dict):
        metadata = payload['metadata']
        if len(metadata) > 50:
            result.add_warning("Metadata has many fields, consider simplifying", field='metadata')
        
        # Check for sensitive information in metadata
        sensitive_keys = ['password', 'secret', 'key', 'token', 'ssn', 'credit_card']
        for key in metadata.keys():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                result.add_error(f"Sensitive information detected in metadata: {key}", field='metadata', code="SENSITIVE_DATA")

def validate_form_fields(form_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Validate form fields structure"""
    result = ValidationResult()
    
    try:
        if not isinstance(form_fields, dict):
            result.add_error("Form fields must be an object", code="INVALID_TYPE")
            return result.to_dict()
        
        if 'fields' not in form_fields:
            result.add_error("Form fields must contain a 'fields' array", code="MISSING_FIELDS")
            return result.to_dict()
        
        fields = form_fields['fields']
        if not isinstance(fields, list):
            result.add_error("Fields must be an array", field='fields', code="INVALID_TYPE")
            return result.to_dict()
        
        # Validate each field
        for i, field in enumerate(fields):
            _validate_single_field(field, i, result)
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error validating form fields: {str(e)}")
        result.add_error(f"Form fields validation error: {str(e)}", code="VALIDATION_ERROR")
        return result.to_dict()

def _validate_single_field(field: Dict[str, Any], index: int, result: ValidationResult):
    """Validate a single form field"""
    field_prefix = f"fields[{index}]"
    
    # Required field properties
    required_props = ['name', 'type', 'label']
    for prop in required_props:
        if prop not in field:
            result.add_error(f"Field missing required property: {prop}", field=f"{field_prefix}.{prop}", code="MISSING_REQUIRED")
    
    # Validate field name
    if 'name' in field:
        name = field['name']
        if not isinstance(name, str) or not name.strip():
            result.add_error("Field name must be a non-empty string", field=f"{field_prefix}.name", code="INVALID_VALUE")
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            result.add_error("Field name must start with letter or underscore and contain only letters, numbers, and underscores", field=f"{field_prefix}.name", code="INVALID_FORMAT")
    
    # Validate field type
    if 'type' in field:
        field_type = field['type']
        valid_types = ['text', 'email', 'tel', 'number', 'date', 'time', 'datetime', 'textarea', 'select', 'checkbox', 'radio']
        if field_type not in valid_types:
            result.add_error(f"Invalid field type: {field_type}. Valid types: {', '.join(valid_types)}", field=f"{field_prefix}.type", code="INVALID_VALUE")
    
    # Validate label
    if 'label' in field:
        label = field['label']
        if not isinstance(label, str) or not label.strip():
            result.add_error("Field label must be a non-empty string", field=f"{field_prefix}.label", code="INVALID_VALUE")
    
    # Validate required property
    if 'required' in field:
        required = field['required']
        if not isinstance(required, bool):
            result.add_error("Field required property must be a boolean", field=f"{field_prefix}.required", code="INVALID_TYPE")
    
    # Validate options for select/radio fields
    if field.get('type') in ['select', 'radio']:
        if 'options' not in field:
            result.add_error(f"Field type '{field['type']}' requires options", field=f"{field_prefix}.options", code="MISSING_REQUIRED")
        elif not isinstance(field['options'], list) or len(field['options']) == 0:
            result.add_error("Field options must be a non-empty array", field=f"{field_prefix}.options", code="INVALID_VALUE")

def validate_api_request(request_data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
    """Validate API request data"""
    result = ValidationResult()
    
    try:
        if not isinstance(request_data, dict):
            result.add_error("Request data must be a JSON object", code="INVALID_TYPE")
            return result.to_dict()
        
        # Validate required fields
        if required_fields:
            for field in required_fields:
                if field not in request_data:
                    result.add_error(f"Missing required field: {field}", field=field, code="MISSING_REQUIRED")
        
        # Check for unexpected fields (optional security check)
        allowed_fields = set(required_fields or [])
        allowed_fields.update(['title', 'description', 'event_type', 'status', 'capacity', 'duration', 'price', 'date', 'email', 'phone', 'metadata', 'form_fields', 'layout'])
        
        unexpected_fields = set(request_data.keys()) - allowed_fields
        if unexpected_fields:
            result.add_warning(f"Unexpected fields detected: {', '.join(unexpected_fields)}", field='request')
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error validating API request: {str(e)}")
        result.add_error(f"Request validation error: {str(e)}", code="VALIDATION_ERROR")
        return result.to_dict()

def sanitize_input(data: Any) -> Any:
    """Sanitize input data to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', data)
        return sanitized.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data against a JSON schema (simplified implementation)"""
    result = ValidationResult()
    
    try:
        # This is a simplified schema validation
        # In production, you might want to use a library like jsonschema
        
        if 'type' in schema:
            expected_type = schema['type']
            if expected_type == 'object' and not isinstance(data, dict):
                result.add_error(f"Expected object, got {type(data).__name__}", code="TYPE_MISMATCH")
            elif expected_type == 'array' and not isinstance(data, list):
                result.add_error(f"Expected array, got {type(data).__name__}", code="TYPE_MISMATCH")
            elif expected_type == 'string' and not isinstance(data, str):
                result.add_error(f"Expected string, got {type(data).__name__}", code="TYPE_MISMATCH")
        
        if 'required' in schema and isinstance(data, dict):
            for field in schema['required']:
                if field not in data:
                    result.add_error(f"Missing required field: {field}", field=field, code="MISSING_REQUIRED")
        
        if 'properties' in schema and isinstance(data, dict):
            for field, field_schema in schema['properties'].items():
                if field in data:
                    field_result = validate_json_schema(data[field], field_schema)
                    if not field_result['valid']:
                        for error in field_result['errors']:
                            error['field'] = f"{field}.{error.get('field', '')}"
                            result.errors.append(error)
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error validating JSON schema: {str(e)}")
        result.add_error(f"Schema validation error: {str(e)}", code="VALIDATION_ERROR")
        return result.to_dict()
