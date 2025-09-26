from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import atexit

from chatbot_api import chatbot_api
from config import config
from dependency_injection import container
from utils.logger import logger

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configure CORS
    if config.app.cors_enabled:
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    
    # Configure rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{config.app.rate_limit_per_minute} per minute"]
    )
    limiter.init_app(app)
    
    # Register blueprints
    app.register_blueprint(chatbot_api)
    
    # Global error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {get_remote_address()}")
        return {
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'error_code': 'RATE_LIMIT_EXCEEDED'
        }, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'error_code': 'INTERNAL_ERROR'
        }, 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'chat_service'}
    
    # Cleanup on shutdown
    def cleanup():
        container.cleanup()
    
    atexit.register(cleanup)
    
    logger.info(f"Flask app created with config: debug={config.app.debug}, port={config.app.port}")
    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting chat service application")
    app.run(
        debug=config.app.debug,
        host=config.app.host,
        port=config.app.port
    )
