import logging
import sys
from typing import Optional
from config import config


class Logger:
    """Centralized logging utility"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with proper formatting and handlers"""
        self._logger = logging.getLogger('chat_service')
        self._logger.setLevel(getattr(logging, config.app.log_level))
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (optional)
        try:
            file_handler = logging.FileHandler('chat_service.log')
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            self._logger.warning(f"Could not create file handler: {e}")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self._logger
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._logger.debug(message, extra=kwargs)


# Global logger instance
logger = Logger()
