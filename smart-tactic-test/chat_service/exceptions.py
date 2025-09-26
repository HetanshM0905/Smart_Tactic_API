"""Custom exceptions for the chat service"""

class ChatServiceException(Exception):
    """Base exception for chat service"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseException(ChatServiceException):
    """Database related exceptions"""
    pass


class LLMException(ChatServiceException):
    """LLM related exceptions"""
    pass


class ValidationException(ChatServiceException):
    """Input validation exceptions"""
    pass


class ConfigurationException(ChatServiceException):
    """Configuration related exceptions"""
    pass


class RateLimitException(ChatServiceException):
    """Rate limiting exceptions"""
    pass
