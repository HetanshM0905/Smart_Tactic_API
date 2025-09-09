"""
Event management API routes
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.event_handler import EventHandler
from app.services.fallback_engine import FallbackEngine
from app.utils.validators import validate_event_payload
from app.utils.logger import get_logger

logger = get_logger(__name__)
event_bp = Blueprint('events', __name__)

@event_bp.route('/create', methods=['POST'])
def create_event():
    """Create a new event with AI-powered form generation"""
    try:
        # Validate request payload
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        # Validate event schema
        validation_result = validate_event_payload(payload)
        if not validation_result['valid']:
            logger.warning(f"Event validation failed: {validation_result['errors']}")
            
            # Trigger fallback engine for invalid events
            fallback_engine = FallbackEngine()
            fallback_result = fallback_engine.handle_invalid_event(payload, validation_result['errors'])
            
            if fallback_result['success']:
                payload = fallback_result['corrected_payload']
                logger.info("Event corrected by fallback engine")
            else:
                return jsonify({
                    'error': 'Event validation failed',
                    'details': validation_result['errors'],
                    'fallback_failed': True
                }), 400
        
        # Process event through event handler
        event_handler = EventHandler()
        result = event_handler.create_event(payload)
        
        if result['success']:
            logger.info(f"Event created successfully: {result.get('event_id')}")
            return jsonify(result), 201
        else:
            logger.error(f"Event creation failed: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in create_event: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/update/<event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        # Validate event schema
        validation_result = validate_event_payload(payload)
        if not validation_result['valid']:
            logger.warning(f"Event update validation failed: {validation_result['errors']}")
            
            # Trigger fallback engine
            fallback_engine = FallbackEngine()
            fallback_result = fallback_engine.handle_invalid_event(payload, validation_result['errors'])
            
            if fallback_result['success']:
                payload = fallback_result['corrected_payload']
                logger.info("Event update corrected by fallback engine")
            else:
                return jsonify({
                    'error': 'Event validation failed',
                    'details': validation_result['errors']
                }), 400
        
        # Process event update
        event_handler = EventHandler()
        result = event_handler.update_event(event_id, payload)
        
        if result['success']:
            logger.info(f"Event updated successfully: {event_id}")
            return jsonify(result), 200
        else:
            logger.error(f"Event update failed: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in update_event: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/layout/update', methods=['POST'])
def update_layout():
    """Update form layout based on event data"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        event_handler = EventHandler()
        result = event_handler.update_layout(payload)
        
        if result['success']:
            logger.info("Layout updated successfully")
            return jsonify(result), 200
        else:
            logger.error(f"Layout update failed: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in update_layout: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/fallback/trigger', methods=['POST'])
def trigger_fallback():
    """Manually trigger fallback engine for event processing"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        fallback_engine = FallbackEngine()
        result = fallback_engine.process_event(payload)
        
        if result['success']:
            logger.info("Fallback engine processed event successfully")
            return jsonify(result), 200
        else:
            logger.error(f"Fallback engine failed: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in trigger_fallback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
