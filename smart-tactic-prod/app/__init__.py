"""
Smart Tactics AI Backend Application
Production-ready Flask app with modular architecture
"""

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.utils.logger import setup_logging
from app.routes import register_blueprints

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app
