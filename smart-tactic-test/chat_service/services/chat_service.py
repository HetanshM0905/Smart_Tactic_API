from typing import Optional, Dict, Any
import json

from models.schemas import ChatRequest, ChatResponse, SuggestedButton
from repositories.base import ChatRepository, WorkflowRepository, PromptRepository, DataRepository
from .langfuse_service import LangfuseService
from .state_service import StateService
from .context_cache_service import ContextCacheService
from exceptions import LLMException, ValidationException, DatabaseException
from utils.logger import logger
from services.llm_service import LLMService


class ChatService:
    """Main chat service that orchestrates chat operations"""
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        workflow_repo: WorkflowRepository,
        prompt_repo: PromptRepository,
        data_repo: DataRepository,
        state_service: StateService,
        llm_service: LLMService,
        langfuse_service: LangfuseService = None
    ):
        self.chat_repo = chat_repo
        self.workflow_repo = workflow_repo
        self.prompt_repo = prompt_repo
        self.data_repo = data_repo
        self.context_cache = ContextCacheService()
        self.state_service = state_service
        self.llm_service = llm_service
        self.langfuse_service = langfuse_service
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
            
            # Update state using StateService
            state = self.state_service.update_state(request.session_id, request.state)
            logger.debug(f"Updated state: {state}")

            # Build prompt
            prompt = self._build_prompt(
                prompt_template, 
                form_object, 
                chat_history, 
                suggested_data,
                request.question,
                state
            )
            logger.debug(f"Built prompt sync: {prompt}")

            
            # Save user message to chat history
            
            # Get LLM response with Langfuse tracing
            logger.debug(f"chat_history: {chat_history}")
            logger.debug(f"schema: {form_schema}")
            llm_response = self._get_llm_response(prompt, form_schema, request)
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
            prompt = self.prompt_repo.get_prompt("smart_tactic_form_assistant", 2)
            if prompt:
                return prompt.text
            return ""
        except Exception as e:
            logger.warning(f"Failed to get prompt template: {e}")
            return ""
    
    def _get_llm_response(self, prompt: str, form_schema: Dict[str, Any], request: ChatRequest) -> str:
        """Get LLM response with comprehensive Langfuse tracing and prompt management"""
        try:
            logger.debug(f"Getting LLM response for session: {request.session_id}")
            if self.langfuse_service and self.langfuse_service.is_enabled():
                logger.debug("Langfuse is enabled - tracing LLM response")
                # Get context data with caching optimization
                workflow = self._get_form_object(request.workflow_id)
                chat_history = self._get_chat_history(request.session_id)
                suggested_data = self._get_suggested_data()
                
                # Check if we should send full workflow context or use cached reference
                context_info = self.context_cache.get_optimized_prompt_context(
                    request.session_id, workflow
                )
                
                # Create comprehensive trace with all context
                trace_id = self.langfuse_service.create_request_trace(
                    session_id=request.session_id,
                    user_question=request.question,
                    workflow_data=workflow,
                    current_state=request.state,
                    chat_history=chat_history
                )
                
                # Prepare optimized prompt variables for tracking
                if context_info['include_full_workflow']:
                    prompt_variables = {
                        'state': request.state,
                        'FormObject': workflow,
                        'chathistory': chat_history,
                        'user_question': request.question,
                        'data': suggested_data
                    }
                    logger.debug(f"Sending full workflow context for session: {request.session_id}")
                else:
                    # Use cached context reference - significantly smaller payload
                    prompt_variables = {
                        'state': request.state,
                        'FormObject': context_info['context_reference'],
                        'chathistory': chat_history,  # Only recent chat history
                        'user_question': request.question,
                        'data': suggested_data
                    }
                    logger.debug(f"Using cached workflow context for session: {prompt_variables['FormObject']}")

                # Get prompt from Langfuse or fallback to local
                langfuse_prompt = self.langfuse_service.get_prompt("smart_tactic_form_assistant",2)
                logger.debug(f"Langfuse prompt: {langfuse_prompt}")
                if langfuse_prompt:
                    prompt_template = langfuse_prompt['prompt']
                    prompt_version = langfuse_prompt['version']
                    
                    # Compile prompt with variables
                    compiled_prompt = self.langfuse_service.compile_prompt(prompt_template, prompt_variables)
                    
                    # Log prompt usage
                    self.langfuse_service.log_prompt_usage(
                        trace_id=trace_id,
                        prompt_name="smart_tactic_form_assistant",
                        prompt_version=prompt_version,
                        variables=prompt_variables,
                        compiled_prompt=compiled_prompt
                    )
                    
                    # Use compiled prompt for LLM
                    final_prompt = compiled_prompt
                    logger.debug(f"Using Langfuse prompt v{prompt_version}")
                else:
                    # Fallback to local prompt template
                    prompt_template = self._get_prompt_template()
                    final_prompt = self._build_prompt(
                        prompt_template,
                        workflow,
                        chat_history,
                        suggested_data,
                        request.question,
                        request.state
                    )
                    prompt_version = 1
                    logger.debug("Using local prompt template")
                
                # Log LLM generation with full context
                llm_response = self.langfuse_service.log_llm_generation_with_context(
                    trace_id=trace_id,
                    name="chat_completion",
                    model=getattr(self.llm_service, 'model_name', 'gemini-1.5-pro-latest'),
                    input_prompt=final_prompt,
                    prompt_template=prompt_template,
                    prompt_variables=prompt_variables,
                    llm_service=self.llm_service,
                    form_schema=form_schema
                )
                
                # Log state update if field_data is returned
                if hasattr(llm_response, 'field_data') and llm_response.field_data:
                    self.langfuse_service.log_state_update(
                        trace_id=trace_id,
                        field_updates=llm_response.field_data,
                        session_id=request.session_id
                    )
            else:
                # Build prompt locally when Langfuse is not available
                workflow = self._get_form_object(request.workflow_id)
                chat_history = self._get_chat_history(request.session_id)
                suggested_data = self._get_suggested_data()
                prompt_template = self._get_prompt_template()
                
                final_prompt = self._build_prompt(
                    prompt_template,
                    workflow,
                    chat_history,
                    suggested_data,
                    request.question,
                    request.state
                )
                
                llm_response = self.llm_service.get_response(final_prompt, form_schema)
            
            logger.debug(f"LLM response: {llm_response}")
            return llm_response
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            raise LLMException(f"Failed to get LLM response: {e}")
    
    def _build_prompt(
        self, 
        template: str, 
        form_object: Dict[str, Any], 
        chat_history: Dict[str, Any], 
        suggested_data: Dict[str, Any],
        user_question: str = "",
        state: Dict[str, Any] = {}
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
            prompt = prompt.replace('{{state}}', json.dumps(state))
            logger.debug(f"Built prompt sync: {prompt}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build prompt: {e}")
            return "You are a helpful assistant."
