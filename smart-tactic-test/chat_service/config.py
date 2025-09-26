import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    db_path: str
    backup_enabled: bool = True
    backup_interval: int = 3600  # seconds


@dataclass
class LLMConfig:
    """LLM configuration settings"""
    api_key: str
    model_name: str = "gemini-1.5-pro-latest"
    max_tokens: int = 8192
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class LangfuseConfig:
    """Langfuse configuration settings"""
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    host: str = "https://cloud.langfuse.com"
    enabled: bool = False


@dataclass
class AppConfig:
    """Application configuration settings"""
    debug: bool = False
    port: int = 5001
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    cors_enabled: bool = True
    rate_limit_per_minute: int = 60


class Config:
    """Main configuration class that loads settings from environment variables"""
    
    def __init__(self):
        self.database = DatabaseConfig(
            db_path=os.getenv('DB_PATH', 'smart_tactic_tinydb.json'),
            backup_enabled=os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true',
            backup_interval=int(os.getenv('DB_BACKUP_INTERVAL', '3600'))
        )
        
        self.llm = LLMConfig(
            api_key=self._get_required_env('GEMINI_API_KEY'),
            model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-pro-latest'),
            max_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
            temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            timeout=int(os.getenv('GEMINI_TIMEOUT', '30'))
        )
        
        self.langfuse = LangfuseConfig(
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com'),
            enabled=bool(os.getenv('LANGFUSE_PUBLIC_KEY') and os.getenv('LANGFUSE_SECRET_KEY'))
        )
        
        self.app = AppConfig(
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            port=int(os.getenv('PORT', '5001')),
            host=os.getenv('HOST', '0.0.0.0'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            cors_enabled=os.getenv('CORS_ENABLED', 'true').lower() == 'true',
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
        )
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value


# Global config instance
config = Config()
