import asyncio
from typing import Optional, Dict, Any
import json

from models.schemas import ChatRequest, ChatResponse, GeminiResponse
from repositories.base import ChatRepository, WorkflowRepository, PromptRepository, DataRepository
from services.llm_service import LLMService
from exceptions import ValidationException, DatabaseException, LLMException
from utils.logger import logger


class AsyncChatService:
    """Async version of chat service for better performance"""
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        workflow_repo: WorkflowRepository,
        prompt_repo: PromptRepository,
        data_repo: DataRepository,
        llm_service: LLMService
    ):
        self.chat_repo = chat_repo
        self.workflow_repo = workflow_repo
        self.prompt_repo = prompt_repo
        self.data_repo = data_repo
        self.llm_service = llm_service
        logger.info("AsyncChatService initialized")
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request asynchronously"""
        try:
            logger.info(f"Processing async chat request for session: {request.session_id}")
            
            # Run database operations concurrently
            form_object_task = asyncio.create_task(self._get_form_object_async(request.workflow_id))
            chat_history_task = asyncio.create_task(self._get_chat_history_async(request.session_id))
            suggested_data_task = asyncio.create_task(self._get_suggested_data_async())
            prompt_template_task = asyncio.create_task(self._get_prompt_template_async())
            
            # Wait for all database operations to complete
            form_object, chat_history, suggested_data, prompt_template = await asyncio.gather(
                form_object_task,
                chat_history_task,
                suggested_data_task,
                prompt_template_task
            )
            
            # Build prompt
            prompt = self._build_prompt(prompt_template, form_object, chat_history, suggested_data, request.question)
            logger.debug(f"Built prompt async: {prompt}")
            
            # Save user message to chat history
            await self._save_message_async(request.session_id, 'user', request.question)
            
            # Get LLM response (this could also be made async if the LLM service supports it)
            llm_response = await self._get_llm_response_async(prompt)
            
            # Save AI response to chat history (including suggested buttons)
            ai_response_content = {
                "markdown": llm_response.markdown,
                "field_data": llm_response.field_data,
                "suggested_buttons": [btn.dict() for btn in llm_response.suggested_buttons]
            }
            await self._save_message_async(request.session_id, 'assistant', json.dumps(ai_response_content))
            
            # Build response
            response = ChatResponse(
                response=llm_response.markdown,
                field_data=llm_response.field_data,
                suggested_buttons=llm_response.suggested_buttons,
                session_id=request.session_id
            )
            
            logger.info(f"Successfully processed async chat request for session: {request.session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process async chat request: {e}")
            if isinstance(e, (ValidationException, DatabaseException, LLMException)):
                raise e
            raise Exception(f"Async chat processing failed: {e}")
    
    async def _get_form_object_async(self, workflow_id: str) -> Dict[str, Any]:
        """Get form object asynchronously"""
        try:
            # Run in thread pool since TinyDB is synchronous
            loop = asyncio.get_event_loop()
            workflow = await loop.run_in_executor(None, self.workflow_repo.get_form_options, workflow_id)
            if workflow:
                return workflow.dict()
            return {}
        except Exception as e:
            logger.warning(f"Failed to get form object for workflow {workflow_id}: {e}")
            return {}
    
    async def _get_chat_history_async(self, session_id: str) -> Dict[str, Any]:
        """Get chat history asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            chat_history = await loop.run_in_executor(None, self.chat_repo.get_chat_history, '1234')
            if chat_history:
                return chat_history.dict()
            return {}
        except Exception as e:
            logger.warning(f"Failed to get chat history for session {session_id}: {e}")
            return {}
    
    async def _get_suggested_data_async(self) -> Dict[str, Any]:
        """Get suggested data asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            suggested_data = await loop.run_in_executor(None, self.data_repo.get_suggested_data, '1')
            return suggested_data or {}
        except Exception as e:
            logger.warning(f"Failed to get suggested data: {e}")
            return {}
    
    async def _get_prompt_template_async(self) -> str:
        """Get prompt template asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            prompt = await loop.run_in_executor(None, self.prompt_repo.get_prompt, "prompt1")
            if prompt:
                return prompt.text
            return ""
        except Exception as e:
            logger.warning(f"Failed to get prompt template: {e}")
            return ""
    
    async def _get_llm_response_async(self, prompt: str) -> GeminiResponse:
        """Get LLM response asynchronously"""
        try:
            # Run LLM call in thread pool since it's synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.llm_service.get_response, prompt)
            return response
        except Exception as e:
            logger.error(f"Async LLM request failed: {e}")
            raise LLMException(f"Async LLM request failed: {e}")
    
    async def _save_message_async(self, session_id: str, role: str, content: str) -> None:
        """Save message to chat history asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.chat_repo.save_message, session_id, role, content)
            logger.debug(f"Saved {role} message for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    def _build_prompt(
        self, 
        template: str, 
        form_object: Dict[str, Any], 
        chat_history: Dict[str, Any], 
        suggested_data: Dict[str, Any],
        user_question: str = ""
    ) -> str:
        """Build final prompt from template and data"""
        try:
            if not template:
                return "You are a helpful assistant."
            
            # Replace template variables
            prompt = template.replace('{{FormObject}}', json.dumps(form_object))
            prompt = prompt.replace('{{chathistory}}', json.dumps(chat_history))
            prompt = prompt.replace('{{data}}', json.dumps(suggested_data))
            prompt = prompt.replace('{{user_question}}', user_question)
            
            return prompt
        except Exception as e:
            logger.error(f"Failed to build prompt: {e}")
            return "You are a helpful assistant."
