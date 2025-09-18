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
