from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import time
from config import config
from utils.logger import logger

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not available - LLM monitoring will be disabled")


class LangfuseService:
    """Service for Langfuse LLM observability and monitoring"""
    
    def __init__(self):
        self.langfuse = None
        self._initialize_langfuse()
        logger.info("LangfuseService initialized")
    
    def _initialize_langfuse(self):
        """Initialize Langfuse client if credentials are available"""
        try:
            if not LANGFUSE_AVAILABLE:
                logger.info("Langfuse package not installed - monitoring disabled")
                return
                
            # if config.langfuse.enabled:
            self.langfuse = Langfuse(
                    public_key="pk-lf-d4ea518b-81fb-459a-9f66-ef93743d204d",
                    secret_key="sk-lf-7d7a00f7-d5e7-405e-ba7e-207a50acccbb",
                    host="https://us.cloud.langfuse.com"
                    
                )
            logger.info("Langfuse client initialized successfully")
            # else:
            #     logger.info("Langfuse credentials not provided - monitoring disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            self.langfuse = None
    
    def create_trace(self, 
                    session_id: str, 
                    user_id: str = None, 
                    metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a new trace for a user session"""
        if not self.langfuse:
            return None
            
        try:
            trace = self.langfuse.trace(
                name="smart_tactic_chat_session",
                user_id=user_id or session_id,
                session_id=session_id,
                metadata=metadata or {},
                tags=["smart-tactic", "form-assistant"]
            )
            
            logger.debug(f"Created Langfuse trace for session: {session_id}")
            return trace.id
            
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None
    
    def create_request_trace(self, 
                           session_id: str,
                           user_question: str,
                           workflow_data: Dict[str, Any] = None,
                           current_state: Dict[str, Any] = None,
                           chat_history: List[Dict[str, Any]] = None) -> Optional[str]:
        """Create a comprehensive trace for a chat request with all context"""
        if not self.langfuse:
            return None
            
        try:
            # Prepare metadata with all context
            metadata = {
                'session_id': session_id,
                'user_question': user_question,
                'timestamp': datetime.now().isoformat(),
                'workflow_id': workflow_data.get('id') if workflow_data else None,
                'workflow_name': workflow_data.get('name') if workflow_data else None,
                'current_state': current_state or {},
                'state_completion': self._calculate_completion_percentage(current_state, workflow_data),
                'chat_history_length': len(chat_history) if chat_history else 0,
                'form_schema_fields': list(workflow_data.get('schema', {}).keys()) if workflow_data else []
            }
            
            trace = self.langfuse.trace(
                name="smart_tactic_chat_request",
                user_id=session_id,
                session_id=session_id,
                input={
                    'user_question': user_question,
                    'current_state': current_state,
                    'workflow_context': workflow_data.get('name') if workflow_data else None
                },
                metadata=metadata,
                tags=["smart-tactic", "form-assistant", "chat-request"]
            )
            
            # Log workflow data as a span
            if workflow_data:
                self._log_workflow_span(trace.id, workflow_data)
            
            # Log state data as a span
            if current_state:
                self._log_state_span(trace.id, current_state, workflow_data)
            
            # Log chat history as a span
            if chat_history:
                self._log_chat_history_span(trace.id, chat_history)
            
            logger.debug(f"Created comprehensive Langfuse trace for session: {session_id}")
            return trace.id
            
        except Exception as e:
            logger.error(f"Failed to create request trace: {e}")
            return None

    def log_llm_generation_with_context(self, 
                                      trace_id: str,
                                      name: str, 
                                      model: str, 
                                      input_prompt: str,
                                      prompt_template: str,
                                      prompt_variables: Dict[str, Any],
                                      llm_service, 
                                      form_schema: Dict[str, Any] = None):
        """Log LLM generation with full prompt context"""
        if not self.langfuse or not trace_id:
            # Fallback to direct LLM call
            return llm_service.get_response(input_prompt, form_schema)
        
        try:
            start_time = time.time()
            
            # Call the LLM service
            response = llm_service.get_response(input_prompt, form_schema)
            
            end_time = time.time()
            
            # Log the generation to Langfuse with comprehensive context
            self.langfuse.generation(
                name=name,
                model=model,
                input=input_prompt,
                output=response.dict() if hasattr(response, 'dict') else str(response),
                metadata={
                    'prompt_template': prompt_template,
                    'prompt_variables': prompt_variables,
                    'form_schema': form_schema,
                    'response_time': end_time - start_time,
                    'model_config': {
                        'temperature': getattr(llm_service, 'temperature', None),
                        'max_tokens': getattr(llm_service, 'max_tokens', None)
                    }
                },
                trace_id=trace_id
            )
            
            logger.debug(f"Logged LLM generation with context to Langfuse")
            return response
            
        except Exception as e:
            logger.error(f"Failed to log LLM generation: {e}")
            # Fallback to direct LLM call
            return llm_service.get_response(input_prompt, form_schema)

    def log_llm_generation(self, 
                          trace, 
                          name: str, 
                          model: str, 
                          input_prompt: str, 
                          llm_service, 
                          form_schema: Dict[str, Any] = None):
        """Log LLM generation with Langfuse (legacy method)"""
        if not self.langfuse or not trace:
            # Fallback to direct LLM call
            return llm_service.get_response(input_prompt, form_schema)
        
        try:
            start_time = time.time()
            
            # Call the LLM service
            response = llm_service.get_response(input_prompt, form_schema)
            
            end_time = time.time()
            
            # Log the generation to Langfuse using the correct API
            self.langfuse.generation(
                name=name,
                model=model,
                input=input_prompt,
                output=response.dict() if hasattr(response, 'dict') else str(response),
                metadata={
                    'form_schema': form_schema,
                    'response_time': end_time - start_time
                },
                trace_id=trace
            )
            
            logger.debug(f"Logged LLM generation to Langfuse")
            return response
            
        except Exception as e:
            logger.error(f"Failed to log LLM generation: {e}")
            # Fallback to direct LLM call
            return llm_service.get_response(input_prompt, form_schema)

    def _log_workflow_span(self, trace_id: str, workflow_data: Dict[str, Any]):
        """Log workflow information as a span"""
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="workflow_context",
                input=workflow_data,
                metadata={
                    'workflow_id': workflow_data.get('id'),
                    'workflow_name': workflow_data.get('name'),
                    'form_fields_count': len(workflow_data.get('formSchema', {}).get('fields', [])),
                    'schema_fields': list(workflow_data.get('schema', {}).keys()),
                    'options_available': list(workflow_data.get('options', {}).keys())
                }
            )
        except Exception as e:
            logger.error(f"Failed to log workflow span: {e}")

    def _log_state_span(self, trace_id: str, current_state: Dict[str, Any], workflow_data: Dict[str, Any] = None):
        """Log current form state as a span"""
        try:
            completion_info = self._calculate_state_analysis(current_state, workflow_data)
            
            self.langfuse.span(
                trace_id=trace_id,
                name="form_state",
                input=current_state,
                metadata={
                    'filled_fields': list(current_state.keys()),
                    'filled_count': len(current_state),
                    'completion_percentage': completion_info['completion_percentage'],
                    'next_empty_fields': completion_info['next_empty_fields'],
                    'state_analysis': completion_info
                }
            )
        except Exception as e:
            logger.error(f"Failed to log state span: {e}")

    def _log_chat_history_span(self, trace_id: str, chat_history: List[Dict[str, Any]]):
        """Log chat history as a span"""
        try:
            # Prepare condensed history for logging
            condensed_history = []
            full_conversation = []
            
            for msg in chat_history:
                # Condensed version for metadata
                condensed_history.append({
                    'role': msg.get('role'),
                    'content_length': len(str(msg.get('content', ''))),
                    'timestamp': msg.get('timestamp'),
                    'has_buttons': 'suggested_buttons' in str(msg.get('content', ''))
                })
                
                # Full conversation for session tracking
                full_conversation.append({
                    'role': msg.get('role'),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp')
                })
            
            self.langfuse.span(
                trace_id=trace_id,
                name="chat_history",
                input={
                    'full_conversation': full_conversation,
                    'recent_messages_summary': condensed_history[-10:] if condensed_history else []  # Last 10 for quick view
                },
                metadata={
                    'total_messages': len(chat_history),
                    'conversation_length': sum(len(str(msg.get('content', ''))) for msg in chat_history),
                    'user_messages': len([msg for msg in chat_history if msg.get('role') == 'user']),
                    'assistant_messages': len([msg for msg in chat_history if msg.get('role') == 'assistant']),
                    'last_message_timestamp': chat_history[-1].get('timestamp') if chat_history and len(chat_history) > 0 else None,
                    'conversation_turns': len([msg for msg in chat_history if msg.get('role') == 'user']),
                    'session_duration_estimate': self._calculate_session_duration(chat_history)
                }
            )
        except Exception as e:
            logger.error(f"Failed to log chat history span: {e}")

    def log_session_summary(self, session_id: str, chat_history: List[Dict[str, Any]], final_state: Dict[str, Any] = None):
        """Log a comprehensive session summary"""
        if not self.langfuse:
            return
            
        try:
            session_metrics = self._calculate_session_metrics(chat_history, final_state)
            
            self.langfuse.trace(
                name="session_summary",
                session_id=session_id,
                input={
                    'session_id': session_id,
                    'complete_chat_history': chat_history,
                    'final_form_state': final_state or {}
                },
                output={
                    'session_completed': session_metrics['session_completed'],
                    'form_completion_rate': session_metrics['completion_percentage'],
                    'total_interactions': session_metrics['total_interactions']
                },
                metadata={
                    'session_metrics': session_metrics,
                    'conversation_flow': self._analyze_conversation_flow(chat_history),
                    'user_engagement': self._calculate_user_engagement(chat_history)
                },
                tags=["smart-tactic", "session-summary", "chat-history"]
            )
            
            logger.debug(f"Logged session summary for: {session_id}")
        except Exception as e:
            logger.error(f"Failed to log session summary: {e}")

    def _calculate_session_duration(self, chat_history: List[Dict[str, Any]]) -> str:
        """Calculate estimated session duration from chat history"""
        if len(chat_history) < 2:
            return "0 minutes"
        
        try:
            first_msg = chat_history[0].get('timestamp') if chat_history and len(chat_history) > 0 else None
            last_msg = chat_history[-1].get('timestamp') if chat_history and len(chat_history) > 0 else None
            
            if first_msg and last_msg:
                from datetime import datetime
                start = datetime.fromisoformat(first_msg.replace('Z', '+00:00'))
                end = datetime.fromisoformat(last_msg.replace('Z', '+00:00'))
                duration = end - start
                return f"{duration.total_seconds() / 60:.1f} minutes"
        except Exception:
            pass
        
        return "Unknown duration"

    def _calculate_session_metrics(self, chat_history: List[Dict[str, Any]], final_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate comprehensive session metrics"""
        user_messages = [msg for msg in chat_history if msg.get('role') == 'user']
        assistant_messages = [msg for msg in chat_history if msg.get('role') == 'assistant']
        
        # Estimate completion percentage
        completion_percentage = 0.0
        if final_state:
            filled_fields = len([k for k, v in final_state.items() if v])
            total_estimated_fields = 8  # Based on schema
            completion_percentage = (filled_fields / total_estimated_fields) * 100
        
        return {
            'total_interactions': len(chat_history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'completion_percentage': completion_percentage,
            'session_completed': completion_percentage >= 80,
            'average_response_length': sum(len(str(msg.get('content', ''))) for msg in assistant_messages) / len(assistant_messages) if assistant_messages else 0,
            'session_duration': self._calculate_session_duration(chat_history)
        }

    def _analyze_conversation_flow(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the flow and patterns in conversation"""
        user_questions = []
        repeated_questions = 0
        
        for msg in chat_history:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                if content in user_questions:
                    repeated_questions += 1
                user_questions.append(content)
        
        return {
            'unique_user_questions': len(set(user_questions)),
            'repeated_questions': repeated_questions,
            'conversation_patterns': {
                'help_requests': len([q for q in user_questions if 'help' in q]),
                'form_related': len([q for q in user_questions if 'form' in q])
            }
        }

    def _calculate_user_engagement(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        user_messages = [msg for msg in chat_history if msg.get('role') == 'user']
        
        if not user_messages:
            return {'engagement_score': 0, 'interaction_frequency': 0}
        
        # Simple engagement scoring
        avg_message_length = sum(len(str(msg.get('content', ''))) for msg in user_messages) / len(user_messages)
        engagement_score = min(100, (len(user_messages) * 10) + (avg_message_length / 10))
        
        return {
            'engagement_score': round(engagement_score, 2),
            'interaction_frequency': len(user_messages),
            'average_message_length': round(avg_message_length, 2)
        }

    def _calculate_completion_percentage(self, current_state: Dict[str, Any], workflow_data: Dict[str, Any]) -> float:
        """Calculate form completion percentage"""
        if not workflow_data or not workflow_data.get('schema'):
            return 0.0
        
        total_fields = len(workflow_data['schema'])
        filled_fields = len([k for k, v in current_state.items() if v])
        
        return round((filled_fields / total_fields) * 100, 2) if total_fields > 0 else 0.0

    def _calculate_state_analysis(self, current_state: Dict[str, Any], workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current state and provide insights"""
        if not workflow_data or not workflow_data.get('schema'):
            return {
                'completion_percentage': 0.0,
                'next_empty_fields': [],
                'field_analysis': {}
            }
        
        schema = workflow_data['schema']
        filled_fields = {k: v for k, v in current_state.items() if v}
        empty_fields = [k for k in schema.keys() if k not in filled_fields]
        
        return {
            'completion_percentage': self._calculate_completion_percentage(current_state, workflow_data),
            'next_empty_fields': empty_fields[:3],  # Next 3 empty fields
            'field_analysis': {
                'total_fields': len(schema),
                'filled_fields': len(filled_fields),
                'empty_fields': len(empty_fields),
                'field_types': {k: v.get('type', 'unknown') for k, v in schema.items()}
            }
        }

    def log_state_update(self, trace_id: str, field_updates: Dict[str, Any], session_id: str):
        """Log when form state is updated"""
        if not self.langfuse or not trace_id:
            return
        
        try:
            self.langfuse.event(
                trace_id=trace_id,
                name="state_update",
                input=field_updates,
                metadata={
                    'session_id': session_id,
                    'updated_fields': list(field_updates.keys()),
                    'update_count': len(field_updates),
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.debug(f"Logged state update to Langfuse")
        except Exception as e:
            logger.error(f"Failed to log state update: {e}")

    def log_validation_error(self, trace_id: str, field_id: str, error_message: str, field_value: Any):
        """Log field validation errors"""
        if not self.langfuse or not trace_id:
            return
        
        try:
            self.langfuse.event(
                trace_id=trace_id,
                name="validation_error",
                input={
                    'field_id': field_id,
                    'field_value': field_value,
                    'error_message': error_message
                },
                metadata={
                    'error_type': 'validation',
                    'field_id': field_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.debug(f"Logged validation error to Langfuse")
        except Exception as e:
            logger.error(f"Failed to log validation error: {e}")

    def get_prompt(self, prompt_name: str, version: int = None) -> Optional[Dict[str, Any]]:
        """Retrieve prompt from Langfuse prompt management"""
        if not self.langfuse:
            logger.warning("Langfuse not initialized - cannot retrieve prompt")
            return None
            
        try:
            if version:
                prompt = self.langfuse.get_prompt(prompt_name, version=version)
            else:
                prompt = self.langfuse.get_prompt(prompt_name)
            
            if prompt:
                logger.debug(f"Retrieved prompt '{prompt_name}' from Langfuse")
                return {
                    'name': prompt.name,
                    'version': prompt.version,
                    'prompt': prompt.prompt,
                    'config': prompt.config,
                    'labels': prompt.labels,
                    'tags': prompt.tags
                }
            else:
                logger.warning(f"Prompt '{prompt_name}' not found in Langfuse")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve prompt from Langfuse: {e}")
            return None

    def create_prompt_version(self, 
                            prompt_name: str, 
                            prompt_text: str, 
                            config: Dict[str, Any] = None,
                            labels: List[str] = None,
                            tags: List[str] = None) -> Optional[str]:
        """Create a new version of a prompt in Langfuse"""
        if not self.langfuse:
            logger.warning("Langfuse not initialized - cannot create prompt")
            return None
            
        try:
            prompt = self.langfuse.create_prompt(
                name=prompt_name,
                prompt=prompt_text,
                config=config or {},
                labels=labels or [],
                tags=tags or ["smart-tactic", "form-assistant"]
            )
            
            logger.info(f"Created prompt '{prompt_name}' version {prompt.version} in Langfuse")
            return f"{prompt_name}_v{prompt.version}"
            
        except Exception as e:
            logger.error(f"Failed to create prompt in Langfuse: {e}")
            return None

    def log_prompt_usage(self, 
                        trace_id: str,
                        prompt_name: str,
                        prompt_version: int,
                        variables: Dict[str, Any],
                        compiled_prompt: str):
        """Log prompt usage with variables and compilation"""
        if not self.langfuse or not trace_id:
            return
            
        try:
            self.langfuse.span(
                trace_id=trace_id,
                name="prompt_usage",
                input={
                    'prompt_name': prompt_name,
                    'prompt_version': prompt_version,
                    'variables': variables,
                    'compiled_prompt': compiled_prompt
                },
                metadata={
                    'prompt_management': True,
                    'prompt_source': 'langfuse',
                    'variable_count': len(variables),
                    'compiled_length': len(compiled_prompt)
                }
            )
            logger.debug(f"Logged prompt usage for {prompt_name} v{prompt_version}")
        except Exception as e:
            logger.error(f"Failed to log prompt usage: {e}")

    def compile_prompt(self, prompt_template: str, variables: Dict[str, Any]) -> str:
        """Compile prompt template with variables"""
        try:
            # Simple template compilation - replace {{variable}} with values
            compiled = prompt_template
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                compiled = compiled.replace(placeholder, str(value))
            
            return compiled
        except Exception as e:
            logger.error(f"Failed to compile prompt: {e}")
            return prompt_template

    def log_user_feedback(self,
                         trace_id: str,
                         score: float,
                         comment: str = None,
                         metadata: Dict[str, Any] = None):
        """Log user feedback for a trace"""
        if not self.langfuse or not trace_id:
            return
            
        try:
            self.langfuse.score(
                trace_id=trace_id,
                name="user_satisfaction",
                value=score,
                comment=comment,
                metadata=metadata or {}
            )
            
            logger.debug(f"Logged user feedback for trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"Failed to log user feedback: {e}")
    
    def create_span(self,
                   trace_id: str,
                   name: str,
                   input_data: Any = None,
                   output_data: Any = None,
                   metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a span for tracking specific operations"""
        if not self.langfuse or not trace_id:
            return None
            
        try:
            span = self.langfuse.span(
                trace_id=trace_id,
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
            
            logger.debug(f"Created span: {name} for trace: {trace_id}")
            return span.id
            
        except Exception as e:
            logger.error(f"Failed to create span: {e}")
            return None
    
    def log_state_update(self,
                        trace_id: str,
                        session_id: str,
                        field_updates: Dict[str, Any],
                        previous_state: Dict[str, Any] = None):
        """Log state updates to Langfuse"""
        if not self.langfuse or not trace_id:
            return
            
        try:
            self.langfuse.event(
                trace_id=trace_id,
                name="state_update",
                input={
                    "session_id": session_id,
                    "field_updates": field_updates,
                    "previous_state": previous_state
                },
                metadata={
                    "event_type": "state_change",
                    "fields_updated": list(field_updates.keys()),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.debug(f"Logged state update for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to log state update: {e}")
    
    def log_validation_error(self,
                           trace_id: str,
                           field_id: str,
                           error_message: str,
                           field_value: Any = None):
        """Log validation errors to Langfuse"""
        if not self.langfuse or not trace_id:
            return
            
        try:
            self.langfuse.event(
                trace_id=trace_id,
                name="validation_error",
                input={
                    "field_id": field_id,
                    "field_value": field_value,
                    "error_message": error_message
                },
                metadata={
                    "event_type": "validation_failure",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.debug(f"Logged validation error for field: {field_id}")
            
        except Exception as e:
            logger.error(f"Failed to log validation error: {e}")
    
    def log_form_completion(self,
                          trace_id: str,
                          session_id: str,
                          completion_time_seconds: float,
                          total_interactions: int,
                          form_data: Dict[str, Any]):
        """Log form completion metrics"""
        if not self.langfuse or not trace_id:
            return
            
        try:
            self.langfuse.event(
                trace_id=trace_id,
                name="form_completion",
                input={
                    "session_id": session_id,
                    "form_data": form_data
                },
                metadata={
                    "event_type": "completion",
                    "completion_time_seconds": completion_time_seconds,
                    "total_interactions": total_interactions,
                    "fields_completed": len(form_data),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Add completion score
            self.langfuse.score(
                trace_id=trace_id,
                name="form_completion_rate",
                value=1.0,  # Completed
                metadata={
                    "completion_time": completion_time_seconds,
                    "interaction_count": total_interactions
                }
            )
            
            logger.debug(f"Logged form completion for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to log form completion: {e}")
    
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        if not self.langfuse:
            return {}
            
        try:
            # This would require Langfuse API calls to fetch session data
            # For now, return placeholder structure
            return {
                "session_id": session_id,
                "total_interactions": 0,
                "completion_rate": 0.0,
                "average_response_time": 0.0,
                "user_satisfaction": None,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {e}")
            return {}
    
    def flush(self):
        """Flush pending events to Langfuse"""
        if self.langfuse:
            try:
                self.langfuse.flush()
                logger.debug("Flushed Langfuse events")
            except Exception as e:
                logger.error(f"Failed to flush Langfuse events: {e}")
    
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and configured"""
        return self.langfuse is not None


# Decorator for automatic tracing
def trace_llm_call(func):
    """Decorator to automatically trace LLM calls"""
    def wrapper(*args, **kwargs):
        # This would integrate with the actual LLM service
        # For now, it's a placeholder
        return func(*args, **kwargs)
    return wrapper
