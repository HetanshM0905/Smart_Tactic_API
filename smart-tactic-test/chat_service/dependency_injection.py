"""Dependency injection container for the chat service"""

from repositories.tinydb_repository import DatabaseManager
from services.chat_service import ChatService
from services.async_chat_service import AsyncChatService
from services.state_service import StateService
from services.langfuse_service import LangfuseService
from services.llm_service import GeminiLLMService
from utils.logger import logger
from config import config
import os


class DIContainer:
    """Dependency injection container"""
    
    def __init__(self):
        self._instances = {}
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Setup all dependencies"""
        logger.info("Setting up dependency injection container")
        
        # Database
        self._instances['db_manager'] = DatabaseManager()
        
        # Repositories
        db_manager = self._instances['db_manager']
        self._instances['session_repo'] = db_manager.session_repo
        self._instances['workflow_repo'] = db_manager.workflow_repo
        self._instances['prompt_repo'] = db_manager.prompt_repo
        self._instances['data_repo'] = db_manager.data_repo
        
        # LLM Service
        try:
            self._instances['llm_service'] = GeminiLLMService()
            logger.info("Initialized Gemini LLM service")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise
        
        # State Service
        from services.state_service import StateService
        self._instances['state_service'] = StateService(
            session_repo=self._instances['session_repo']
        )
        
        # Langfuse Service
        self._instances['langfuse_service'] = LangfuseService()
        
        # Chat Service
        self._instances['chat_service'] = ChatService(
            session_repo=self._instances['session_repo'],
            workflow_repo=self._instances['workflow_repo'],
            prompt_repo=self._instances['prompt_repo'],
            data_repo=self._instances['data_repo'],
            state_service=self._instances['state_service'],
            llm_service=self._instances['llm_service'],
            langfuse_service=self._instances['langfuse_service']
        )
        
        # Async Chat Service
        from services.async_chat_service import AsyncChatService
        self._instances['async_chat_service'] = AsyncChatService(
            session_repo=self._instances['session_repo'],
            workflow_repo=self._instances['workflow_repo'],
            prompt_repo=self._instances['prompt_repo'],
            data_repo=self._instances['data_repo'],
            state_service=self._instances['state_service'],
            llm_service=self._instances['llm_service'],
            langfuse_service=self._instances['langfuse_service']
        )
        
        logger.info("Dependency injection container setup complete")
    
    def get(self, service_name: str):
        """Get service instance by name"""
        if service_name not in self._instances:
            raise ValueError(f"Service {service_name} not found in container")
        return self._instances[service_name]
    
    def cleanup(self):
        """Cleanup resources"""
        if 'db_manager' in self._instances:
            self._instances['db_manager'].close()
        logger.info("DI container cleanup complete")


# Global container instance
container = DIContainer()
