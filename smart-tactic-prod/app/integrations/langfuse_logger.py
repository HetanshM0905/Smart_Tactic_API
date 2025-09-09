"""
Langfuse integration for LLM tracing and monitoring
Tracks LLM invocations, errors, and performance metrics
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LangfuseLogger:
    """Langfuse client for LLM tracing and monitoring"""
    
    def __init__(self):
        self.config = Config()
        self.public_key = self.config.LANGFUSE_PUBLIC_KEY
        self.secret_key = self.config.LANGFUSE_SECRET_KEY
        self.host = self.config.LANGFUSE_HOST
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Langfuse client"""
        try:
            if not all([self.public_key, self.secret_key]):
                logger.warning("Langfuse credentials not configured")
                return
            
            # Initialize Langfuse client
            self.client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host
            )
            
            logger.info("Langfuse client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse client: {str(e)}")
            self.client = None
    
    def start_trace(self, name: str, input_data: Dict[str, Any], 
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Start a new trace"""
        try:
            if not self.client:
                return None
            
            trace = self.client.trace(
                name=name,
                input=input_data,
                metadata=metadata or {},
                tags=["smart-tactics-backend"]
            )
            
            logger.debug(f"Started Langfuse trace: {name}")
            return trace
            
        except Exception as e:
            logger.error(f"Error starting Langfuse trace: {str(e)}")
            return None
    
    def end_trace(self, trace: Optional[Any], output: Optional[Dict[str, Any]] = None,
                 error: Optional[str] = None, status: str = "success") -> None:
        """End a trace"""
        try:
            if not trace or not self.client:
                return
            
            if error:
                trace.update(
                    output={"error": error},
                    status="error"
                )
            else:
                trace.update(
                    output=output or {},
                    status=status
                )
            
            # Flush the trace
            self.client.flush()
            
            logger.debug(f"Ended Langfuse trace with status: {status}")
            
        except Exception as e:
            logger.error(f"Error ending Langfuse trace: {str(e)}")
    
    def log_generation(self, trace: Optional[Any], name: str, 
                      input_data: Dict[str, Any], output_data: Dict[str, Any],
                      model: str = "gemini-pro", tokens_used: Optional[int] = None) -> None:
        """Log a generation event"""
        try:
            if not trace or not self.client:
                return
            
            generation = trace.generation(
                name=name,
                input=input_data,
                output=output_data,
                model=model,
                usage={
                    "input": tokens_used or 0,
                    "output": tokens_used or 0,
                    "total": (tokens_used or 0) * 2
                } if tokens_used else None
            )
            
            logger.debug(f"Logged generation: {name}")
            
        except Exception as e:
            logger.error(f"Error logging generation: {str(e)}")
    
    def log_span(self, trace: Optional[Any], name: str, 
                input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None,
                metadata: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Log a span within a trace"""
        try:
            if not trace or not self.client:
                return None
            
            span = trace.span(
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
            
            logger.debug(f"Logged span: {name}")
            return span
            
        except Exception as e:
            logger.error(f"Error logging span: {str(e)}")
            return None
    
    def log_event(self, name: str, input_data: Dict[str, Any], 
                 output_data: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a standalone event"""
        try:
            if not self.client:
                return
            
            event = self.client.event(
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata or {},
                tags=["smart-tactics-backend"]
            )
            
            # Flush the event
            self.client.flush()
            
            logger.debug(f"Logged event: {name}")
            
        except Exception as e:
            logger.error(f"Error logging event: {str(e)}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error event"""
        try:
            if not self.client:
                return
            
            error_data = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {}
            }
            
            self.log_event(
                name="error_occurred",
                input_data=error_data,
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "error"
                }
            )
            
        except Exception as e:
            logger.error(f"Error logging error event: {str(e)}")
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             unit: str = "seconds", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a performance metric"""
        try:
            if not self.client:
                return
            
            metric_data = {
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "metadata": metadata or {}
            }
            
            self.log_event(
                name="performance_metric",
                input_data=metric_data,
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "metric_type": "performance"
                }
            )
            
        except Exception as e:
            logger.error(f"Error logging performance metric: {str(e)}")
    
    def get_callback_handler(self) -> Optional[CallbackHandler]:
        """Get Langfuse callback handler for automatic tracing"""
        try:
            if not self.client:
                return None
            
            return CallbackHandler(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host
            )
            
        except Exception as e:
            logger.error(f"Error creating callback handler: {str(e)}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check Langfuse service health"""
        try:
            if not self.client:
                return {
                    'success': False,
                    'error': 'Langfuse client not initialized',
                    'status': 'unhealthy'
                }
            
            # Test with a simple event
            test_event = self.client.event(
                name="health_check",
                input={"test": True},
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
            
            # Flush to ensure it's sent
            self.client.flush()
            
            return {
                'success': True,
                'status': 'healthy',
                'service': 'Langfuse'
            }
            
        except Exception as e:
            logger.error(f"Langfuse health check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'unhealthy'
            }
