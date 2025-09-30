
"""
Configuration management for Smart Tactics application
Supports multiple environments with secure secret handling
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Database settings
    FIRESTORE_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    ALLOYDB_HOST = os.environ.get('ALLOYDB_HOST')
    ALLOYDB_PORT = os.environ.get('ALLOYDB_PORT', '5432')
    ALLOYDB_DATABASE = os.environ.get('ALLOYDB_DATABASE')
    ALLOYDB_USER = os.environ.get('ALLOYDB_USER')
    ALLOYDB_PASSWORD = os.environ.get('ALLOYDB_PASSWORD')
    
    # LLM settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
    
    # Monitoring and logging
    LANGFUSE_PUBLIC_KEY = os.environ.get('LANGFUSE_PUBLIC_KEY')
    LANGFUSE_SECRET_KEY = os.environ.get('LANGFUSE_SECRET_KEY')
    LANGFUSE_HOST = os.environ.get('LANGFUSE_HOST', 'https://cloud.langfuse.com')
    
    # Google Cloud settings
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
    
    # Retry settings
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.environ.get('RETRY_DELAY', '1'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with more secure settings for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    ALLOYDB_DATABASE = ':memory:'

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)
