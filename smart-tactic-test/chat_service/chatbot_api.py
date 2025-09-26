from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from models.schemas import ChatRequest, ChatResponse
from dependency_injection import container
from exceptions import ValidationException, ChatServiceException
from utils.logger import logger
import asyncio

chatbot_api = Blueprint('chatbot_api', __name__)

@chatbot_api.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """AI chat endpoint with proper error handling and validation"""
    try:
    # Get async chat service from DI container
        chat_service = container.get('chat_service')
        
        # Validate request data
        data = request.get_json()
        if not data:
            raise ValidationException("Request body is required")
        
        # Create and validate request model
        try:
            chat_request = ChatRequest(**data)
        except ValidationError as e:
            raise ValidationException(f"Invalid request data: {e}")
        
    # Process chat request asynchronously
        # response = asyncio.run(async_chat_service.process_chat(chat_request))
        response = chat_service.process_chat(chat_request)
        # Return response
        return jsonify(response.dict())
        
    except ValidationException as e:
        logger.warning(f"Validation error: {e.message}")
        return jsonify({
            'error': 'Validation Error',
            'message': e.message,
            'error_code': e.error_code or 'VALIDATION_ERROR'
        }), 400
        
    except ChatServiceException as e:
        logger.error(f"Chat service error: {e.message}")
        return jsonify({
            'error': 'Service Error',
            'message': e.message,
            'error_code': e.error_code or 'SERVICE_ERROR'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@chatbot_api.route('/api/chat-history/<session_id>/<section>', methods=['GET'])
def get_chat_history(session_id, section):
    """Get chat history for a specific session and section"""
    try:
        # Get session repository from DI container
        session_repo = container.get('session_repo')
        
        # Validate input parameters
        if not session_id or not session_id.strip():
            raise ValidationException("Session ID is required")
        
        if not section or not section.strip():
            raise ValidationException("Section is required")
        
        # Get the user session
        user_session = session_repo.get_session(session_id.strip())
        
        if not user_session:
            return jsonify({
                'session_id': session_id,
                'section': section,
                'chat_history': [],
                'message': 'Session not found'
            }), 404
        
        # Get chat history for the specific section
        section_history = user_session.history_by_section.get(section.strip(), [])
        
        # Convert ChatMessage objects to dictionaries for JSON serialization
        chat_history = [message.dict() for message in section_history]
        
        logger.info(f"Retrieved chat history for session {session_id}, section {section}: {len(chat_history)} messages")
        
        return jsonify({
            'session_id': session_id,
            'section': section,
            'chat_history': chat_history,
            'message_count': len(chat_history),
            'state': user_session.state
        }), 200
        
    except ValidationException as e:
        logger.warning(f"Validation error in get_chat_history: {e.message}")
        return jsonify({
            'error': 'Validation Error',
            'message': e.message,
            'error_code': e.error_code or 'VALIDATION_ERROR'
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in get_chat_history: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred while retrieving chat history',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@chatbot_api.route('/api/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    """Get complete session information including all sections and state"""
    try:
        # Get session repository from DI container
        session_repo = container.get('session_repo')
        
        # Validate input parameters
        if not session_id or not session_id.strip():
            raise ValidationException("Session ID is required")
        
        # Get the user session
        user_session = session_repo.get_session(session_id.strip())
        
        if not user_session:
            return jsonify({
                'session_id': session_id,
                'message': 'Session not found'
            }), 404
        
        # Convert the entire session to a dictionary
        session_data = user_session.dict()
        
        # Add some metadata
        sections = list(session_data['history_by_section'].keys())
        total_messages = sum(len(messages) for messages in session_data['history_by_section'].values())
        
        logger.info(f"Retrieved complete session info for {session_id}: {len(sections)} sections, {total_messages} total messages")
        
        return jsonify({
            'session_id': session_id,
            'sections': sections,
            'total_messages': total_messages,
            'session_data': session_data
        }), 200
        
    except ValidationException as e:
        logger.warning(f"Validation error in get_session_info: {e.message}")
        return jsonify({
            'error': 'Validation Error',
            'message': e.message,
            'error_code': e.error_code or 'VALIDATION_ERROR'
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in get_session_info: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred while retrieving session info',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@chatbot_api.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'error_code': 'NOT_FOUND'
    }), 404

@chatbot_api.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The requested method is not allowed for this resource',
        'error_code': 'METHOD_NOT_ALLOWED'
    }), 405
