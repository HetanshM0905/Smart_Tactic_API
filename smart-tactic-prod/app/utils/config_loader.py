"""
Configuration loader utilities
Handles environment-specific configuration loading and validation
"""

import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    """Utility class for loading and validating configuration"""
    
    def __init__(self):
        self.config_cache = {}
        self.loaded_env_files = []
    
    def load_environment_config(self, env_file: str = '.env') -> Dict[str, Any]:
        """Load configuration from environment variables and .env file"""
        try:
            # Load .env file if it exists
            if os.path.exists(env_file):
                load_dotenv(env_file)
                self.loaded_env_files.append(env_file)
                logger.info(f"Loaded environment file: {env_file}")
            
            # Load configuration from environment variables
            config = {
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
                'SECRET_KEY': os.environ.get('SECRET_KEY'),
                'CORS_ORIGINS': self._parse_cors_origins(),
                
                # Database configuration
                'FIRESTORE_PROJECT_ID': os.environ.get('GOOGLE_CLOUD_PROJECT'),
                'ALLOYDB_HOST': os.environ.get('ALLOYDB_HOST'),
                'ALLOYDB_PORT': os.environ.get('ALLOYDB_PORT', '5432'),
                'ALLOYDB_DATABASE': os.environ.get('ALLOYDB_DATABASE'),
                'ALLOYDB_USER': os.environ.get('ALLOYDB_USER'),
                'ALLOYDB_PASSWORD': os.environ.get('ALLOYDB_PASSWORD'),
                
                # LLM configuration
                'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY'),
                'GEMINI_MODEL': os.environ.get('GEMINI_MODEL', 'gemini-pro'),
                
                # Monitoring configuration
                'LANGFUSE_PUBLIC_KEY': os.environ.get('LANGFUSE_PUBLIC_KEY'),
                'LANGFUSE_SECRET_KEY': os.environ.get('LANGFUSE_SECRET_KEY'),
                'LANGFUSE_HOST': os.environ.get('LANGFUSE_HOST', 'https://cloud.langfuse.com'),
                
                # Google Cloud configuration
                'GOOGLE_APPLICATION_CREDENTIALS': os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
                
                # Application configuration
                'MAX_CONTENT_LENGTH': int(os.environ.get('MAX_CONTENT_LENGTH', '16777216')),  # 16MB
                'REQUEST_TIMEOUT': int(os.environ.get('REQUEST_TIMEOUT', '30')),
                'MAX_RETRIES': int(os.environ.get('MAX_RETRIES', '3')),
                'RETRY_DELAY': int(os.environ.get('RETRY_DELAY', '1')),
                
                # Logging configuration
                'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
                'ENABLE_STRUCTURED_LOGGING': os.environ.get('ENABLE_STRUCTURED_LOGGING', 'true').lower() == 'true',
                
                # Security configuration
                'ENABLE_RATE_LIMITING': os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true',
                'RATE_LIMIT_PER_MINUTE': int(os.environ.get('RATE_LIMIT_PER_MINUTE', '100')),
                
                # Feature flags
                'ENABLE_AUTOFILL': os.environ.get('ENABLE_AUTOFILL', 'true').lower() == 'true',
                'ENABLE_FALLBACK': os.environ.get('ENABLE_FALLBACK', 'true').lower() == 'true',
                'ENABLE_LLM_GENERATION': os.environ.get('ENABLE_LLM_GENERATION', 'true').lower() == 'true',
            }
            
            # Cache the configuration
            self.config_cache = config
            
            logger.info("Environment configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error loading environment configuration: {str(e)}")
            raise
    
    def load_json_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Configuration file not found: {config_file}")
                return {}
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded JSON configuration from: {config_file}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {config_file}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON configuration from {config_file}: {str(e)}")
            raise
    
    def validate_config(self, config: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
        """Validate configuration and return validation result"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Default required fields
            if required_fields is None:
                required_fields = ['SECRET_KEY']
            
            # Check required fields
            for field in required_fields:
                if field not in config or not config[field]:
                    validation_result['errors'].append(f"Missing required configuration: {field}")
                    validation_result['valid'] = False
            
            # Environment-specific validation
            env = config.get('FLASK_ENV', 'development')
            
            if env == 'production':
                # Production-specific validations
                prod_required = ['SECRET_KEY', 'FIRESTORE_PROJECT_ID', 'GEMINI_API_KEY']
                for field in prod_required:
                    if field not in config or not config[field]:
                        validation_result['errors'].append(f"Production requires: {field}")
                        validation_result['valid'] = False
                
                # Check for secure secret key
                secret_key = config.get('SECRET_KEY', '')
                if secret_key == 'dev-secret-key-change-in-production':
                    validation_result['errors'].append("Production must use a secure SECRET_KEY")
                    validation_result['valid'] = False
            
            # Validate database configuration
            if config.get('ALLOYDB_HOST') and not config.get('ALLOYDB_DATABASE'):
                validation_result['warnings'].append("AlloyDB host specified but no database name")
            
            # Validate LLM configuration
            if config.get('GEMINI_API_KEY') and not config.get('GEMINI_MODEL'):
                validation_result['warnings'].append("Gemini API key specified but no model name")
            
            # Validate monitoring configuration
            langfuse_key = config.get('LANGFUSE_PUBLIC_KEY')
            langfuse_secret = config.get('LANGFUSE_SECRET_KEY')
            if (langfuse_key and not langfuse_secret) or (langfuse_secret and not langfuse_key):
                validation_result['warnings'].append("Langfuse requires both public and secret keys")
            
            # Validate numeric configurations
            numeric_fields = ['MAX_CONTENT_LENGTH', 'REQUEST_TIMEOUT', 'MAX_RETRIES', 'RETRY_DELAY']
            for field in numeric_fields:
                if field in config:
                    try:
                        int(config[field])
                    except (ValueError, TypeError):
                        validation_result['errors'].append(f"Invalid numeric value for {field}")
                        validation_result['valid'] = False
            
            logger.info(f"Configuration validation completed: {'valid' if validation_result['valid'] else 'invalid'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating configuration: {str(e)}")
            validation_result['valid'] = False
            validation_result['errors'].append(f"Configuration validation error: {str(e)}")
            return validation_result
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default"""
        return self.config_cache.get(key, default)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration cache"""
        self.config_cache.update(updates)
        logger.info(f"Configuration updated with {len(updates)} values")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration"""
        return {
            'firestore': {
                'project_id': self.get_config_value('FIRESTORE_PROJECT_ID'),
                'credentials_path': self.get_config_value('GOOGLE_APPLICATION_CREDENTIALS')
            },
            'alloydb': {
                'host': self.get_config_value('ALLOYDB_HOST'),
                'port': self.get_config_value('ALLOYDB_PORT', '5432'),
                'database': self.get_config_value('ALLOYDB_DATABASE'),
                'user': self.get_config_value('ALLOYDB_USER'),
                'password': self.get_config_value('ALLOYDB_PASSWORD')
            }
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration"""
        return {
            'gemini': {
                'api_key': self.get_config_value('GEMINI_API_KEY'),
                'model': self.get_config_value('GEMINI_MODEL', 'gemini-pro')
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring-specific configuration"""
        return {
            'langfuse': {
                'public_key': self.get_config_value('LANGFUSE_PUBLIC_KEY'),
                'secret_key': self.get_config_value('LANGFUSE_SECRET_KEY'),
                'host': self.get_config_value('LANGFUSE_HOST', 'https://cloud.langfuse.com')
            },
            'logging': {
                'level': self.get_config_value('LOG_LEVEL', 'INFO'),
                'structured': self.get_config_value('ENABLE_STRUCTURED_LOGGING', True)
            }
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration"""
        return {
            'rate_limiting': {
                'enabled': self.get_config_value('ENABLE_RATE_LIMITING', True),
                'per_minute': self.get_config_value('RATE_LIMIT_PER_MINUTE', 100)
            },
            'cors': {
                'origins': self.get_config_value('CORS_ORIGINS', ['*'])
            }
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration"""
        return {
            'autofill': self.get_config_value('ENABLE_AUTOFILL', True),
            'fallback': self.get_config_value('ENABLE_FALLBACK', True),
            'llm_generation': self.get_config_value('ENABLE_LLM_GENERATION', True)
        }
    
    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable"""
        origins_str = os.environ.get('CORS_ORIGINS', '*')
        if origins_str == '*':
            return ['*']
        return [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    
    def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from environment"""
        self.config_cache.clear()
        return self.load_environment_config()
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration (optionally including secrets)"""
        config = self.config_cache.copy()
        
        if not include_secrets:
            # Remove sensitive fields
            sensitive_fields = [
                'SECRET_KEY', 'GEMINI_API_KEY', 'LANGFUSE_SECRET_KEY',
                'ALLOYDB_PASSWORD', 'GOOGLE_APPLICATION_CREDENTIALS'
            ]
            for field in sensitive_fields:
                if field in config:
                    config[field] = '***REDACTED***'
        
        return config

# Global config loader instance
config_loader = ConfigLoader()
