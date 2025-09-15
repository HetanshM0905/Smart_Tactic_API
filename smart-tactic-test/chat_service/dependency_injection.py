"""Dependency injection container for the chat service"""

from repositories.tinydb_repository import DatabaseManager
from services.llm_service import GeminiLLMService, MockLLMService
from services.chat_service import ChatService
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
        self._instances['chat_repo'] = db_manager.chat_repo
        self._instances['workflow_repo'] = db_manager.workflow_repo
        self._instances['prompt_repo'] = db_manager.prompt_repo
        self._instances['data_repo'] = db_manager.data_repo
        
        # LLM Service
        try:
            self._instances['llm_service'] = GeminiLLMService()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini service, using mock: {e}")
            self._instances['llm_service'] = MockLLMService()
        
        # Chat Service
        self._instances['chat_service'] = ChatService(
            chat_repo=self._instances['chat_repo'],
            workflow_repo=self._instances['workflow_repo'],
            prompt_repo=self._instances['prompt_repo'],
            data_repo=self._instances['data_repo'],
            llm_service=self._instances['llm_service']
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
