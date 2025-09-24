import asyncio
from typing import Optional, Dict, Any
import json
from services.context_cache_service import ContextCacheService

from models.schemas import ChatRequest, ChatResponse
from repositories.base import SessionRepository, WorkflowRepository, PromptRepository, DataRepository
from services.llm_service import LLMService
from services.state_service import StateService
from services.langfuse_service import LangfuseService
from exceptions import ValidationException, DatabaseException, LLMException
from utils.logger import logger


class AsyncChatService:
    """Async version of chat service for better performance"""
    
    def __init__(
        self,
        session_repo: SessionRepository,
        workflow_repo: WorkflowRepository,
        prompt_repo: PromptRepository,
        data_repo: DataRepository,
        state_service: StateService,
        llm_service: LLMService,
        langfuse_service=None
    ):
        self.session_repo = session_repo
        self.workflow_repo = workflow_repo
        self.prompt_repo = prompt_repo
        self.data_repo = data_repo
        self.context_cache = ContextCacheService()
        self.state_service = state_service
        self.llm_service = llm_service
        self.langfuse_service = langfuse_service
        logger.info("AsyncChatService initialized")
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request asynchronously"""
        try:
            logger.info(f"Processing async chat request for session: {request.session_id}")
            
            # Run database operations concurrently
            form_object_task = asyncio.create_task(self._get_form_object_async(request.workflow_id))
            chat_history_task = asyncio.create_task(self._get_chat_history_async(request.session_id, request.current_section))
            suggested_data_task = asyncio.create_task(self._get_suggested_data_async())
            prompt_template_task = asyncio.create_task(self._get_prompt_template_async())
            

            # Wait for all database operations to complete
            form_object, chat_history, suggested_data, prompt_template = await asyncio.gather(
                form_object_task,
                chat_history_task,
                suggested_data_task,
                prompt_template_task
            )

            # Extract form_schema from form_object
            form_schema = form_object.get('schema', {})

            # Update state using StateService
            state = await self._update_state_service_async(request.session_id, request.state)
            logger.debug(f"Updated state: {state}")

            # Build prompt
            prompt = self._build_prompt(prompt_template, form_object, chat_history, suggested_data, request.question, state)
            logger.debug(f"Built prompt async: {prompt}")

            # Save user message to chat history
            await self._save_message_async(request.session_id, request.current_section, 'user', request.question)

            # Get LLM response with Langfuse tracing
            llm_response = await self._get_llm_response_async(prompt, form_schema, request)

            # Save AI response to chat history (including suggested buttons)
            ai_response_content = {
                "markdown": llm_response.markdown,
                "suggested_buttons": [btn.dict() for btn in llm_response.suggested_buttons]
            }
            await self._save_message_async(request.session_id, request.current_section, 'assistant', json.dumps(ai_response_content))

            # Build response
            response = ChatResponse(
                response=llm_response.markdown,
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
    
    async def _get_chat_history_async(self, session_id: str, section: str) -> Dict[str, Any]:
        """Get chat history for a specific section asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            user_session = await loop.run_in_executor(None, self.session_repo.get_session, session_id)
            if user_session and section in user_session.history_by_section:
                return {"history": user_session.history_by_section[section]}
            return {}
        except Exception as e:
            logger.warning(f"Failed to get chat history for session {session_id}, section {section}: {e}")
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
    
    async def _get_llm_response_async(self, prompt: str, form_schema: Dict[str, Any], request: ChatRequest):
        """Get LLM response asynchronously with comprehensive Langfuse tracing"""
        try:
            if self.langfuse_service and self.langfuse_service.is_enabled():
                # Get all context data for comprehensive tracking
                workflow = await self._get_form_object_async(request.workflow_id)
                chat_history = await self._get_chat_history_async(request.session_id, request.current_section)
                suggested_data = await self._get_suggested_data_async()

                # Use context cache to optimize prompt context
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

                # Prepare prompt variables for tracking
                if context_info['include_full_workflow']:
                    prompt_variables = {
                        'state': request.state,
                        'FormObject': workflow,
                        'chathistory': chat_history,
                        'user_question': request.question,
                        'data': suggested_data
                    }
                else:
                    prompt_variables = {
                        'state': request.state,
                        'FormObject': context_info['context_reference'],
                        'chathistory': chat_history,
                        'user_question': request.question,
                        'data': suggested_data
                    }

                # Get prompt from Langfuse or fallback to local
                loop = asyncio.get_event_loop()
                langfuse_prompt = await loop.run_in_executor(
                    None, self.langfuse_service.get_prompt, "smart_tactic_form_assistant",2
                )

                if langfuse_prompt:
                    prompt_template = langfuse_prompt['prompt']
                    prompt_version = langfuse_prompt['version']

                    # Compile prompt with variables
                    compiled_prompt = await loop.run_in_executor(
                        None, self.langfuse_service.compile_prompt, prompt_template, prompt_variables
                    )

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
                else:
                    # Fallback to local prompt template
                    prompt_template = await self._get_prompt_template_async()
                    final_prompt = prompt
                    prompt_version = 1

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

                # Note: field_data logging removed as field_data is no longer part of GeminiResponse
            else:
                # Run LLM call without Langfuse tracing
                loop = asyncio.get_event_loop()
                llm_response = await loop.run_in_executor(
                    None, self.llm_service.get_response, prompt, form_schema
                )
            
            logger.debug(f"LLM response: {llm_response}")
            return llm_response
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            raise LLMException(f"Failed to get LLM response: {e}")
    
    async def _save_message_async(self, session_id: str, section: str, role: str, content: str) -> None:
        """Save message to a specific section of chat history asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.session_repo.save_message, session_id, section, role, content)
            logger.debug(f"Saved {role} message for session: {session_id} in section: {section}")
        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    async def _update_state_service_async(self, session_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update state using StateService asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.state_service.update_state, session_id, state)
            logger.debug(f"Updated state for session: {session_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update state: {e}")
            return state

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
            
            return prompt
        except Exception as e:
            logger.error(f"Failed to build prompt: {e}")
            return "You are a helpful assistant."
