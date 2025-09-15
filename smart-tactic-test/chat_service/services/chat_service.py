from typing import Optional, Dict, Any
import json

from models.schemas import ChatRequest, ChatResponse, GeminiResponse
from repositories.base import ChatRepository, WorkflowRepository, PromptRepository, DataRepository
from services.llm_service import LLMService
from exceptions import ValidationException, DatabaseException, LLMException
from utils.logger import logger


class ChatService:
    """Main chat service that orchestrates chat operations"""
    
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
        logger.info("ChatService initialized")
    
    def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request and return response"""
        try:
            logger.info(f"Processing chat request for session: {request.session_id}")
            
            # Get required data
            form_object = self._get_form_object(request.workflow_id)
            logger.debug(f"form_object: {form_object}")
            form_schema = form_object.get('schema', {})
            chat_history = self._get_chat_history(request.session_id)
            suggested_data = self._get_suggested_data()
            prompt_template = self._get_prompt_template()
            
            # Build prompt
            prompt = self._build_prompt(
                prompt_template, 
                form_object, 
                chat_history, 
                suggested_data,
                request.question
            )
            logger.debug(f"Built prompt sync: {prompt}")
            
            # Save user message to chat history
            
            # Get LLM response
            logger.debug(f"chat_history: {chat_history}")
            logger.debug(f"schema: {form_schema}")
            llm_response = self.llm_service.get_response(prompt,form_schema,chat_history)
            self.chat_repo.save_message(request.session_id, 'user', request.question)

            
            # Save AI response to chat history (including suggested buttons)
            ai_response_content = {
                "markdown": llm_response.markdown,
                "field_data": llm_response.field_data,
                "suggested_buttons": [btn.dict() for btn in llm_response.suggested_buttons]
            }
            self.chat_repo.save_message(request.session_id, 'assistant', json.dumps(ai_response_content))
            
            # Build response
            response = ChatResponse(
                response=llm_response.markdown,
                field_data=llm_response.field_data,
                suggested_buttons=llm_response.suggested_buttons,
                session_id=request.session_id
            )
            
            logger.info(f"Successfully processed chat request for session: {request.session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process chat request: {e}")
            if isinstance(e, (ValidationException, DatabaseException, LLMException)):
                raise e
            raise Exception(f"Chat processing failed: {e}")
    
    def _get_form_object(self, workflow_id: str) -> Dict[str, Any]:
        """Get form object for workflow"""
        try:
            workflow = self.workflow_repo.get_form_options(workflow_id)
            if workflow:
                return workflow.dict()
            return {}
        except Exception as e:
            logger.warning(f"Failed to get form object for workflow {workflow_id}: {e}")
            return {}
    
    def _get_chat_history(self, session_id: str) -> Dict[str, Any]:
        """Get chat history for session"""
        try:
            # Using hardcoded session for now - can be made dynamic
            chat_history = self.chat_repo.get_chat_history(session_id)
            if chat_history:
                return chat_history.dict()
            return {}
        except Exception as e:
            logger.warning(f"Failed to get chat history for session {session_id}: {e}")
            return {}
    
    def _get_suggested_data(self) -> Dict[str, Any]:
        """Get suggested data"""
        try:
            # Using hardcoded ID for now - can be made dynamic
            suggested_data = self.data_repo.get_suggested_data('1')
            return suggested_data or {}
        except Exception as e:
            logger.warning(f"Failed to get suggested data: {e}")
            return {}
    
    def _get_prompt_template(self) -> str:
        """Get prompt template"""
        try:
            prompt = self.prompt_repo.get_prompt("prompt1")
            if prompt:
                return prompt.text
            return ""
        except Exception as e:
            logger.warning(f"Failed to get prompt template: {e}")
            return ""
    
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
            logger.debug(f"Built prompt sync: {prompt}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build prompt: {e}")
            return "You are a helpful assistant."
