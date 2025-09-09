"""
Centralized logging configuration for the Smart Tactics application
Supports both console and Google Cloud Logging
"""

import os
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import logging as cloud_logging
from flask import Flask, request, g

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if hasattr(g, 'request_id'):
            log_entry['request_id'] = g.request_id
        
        if hasattr(g, 'user_id'):
            log_entry['user_id'] = g.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records"""
    
    def filter(self, record):
        # Add request context if available
        if hasattr(g, 'request_id'):
            record.request_id = g.request_id
        
        if hasattr(g, 'user_id'):
            record.user_id = g.user_id
        
        if hasattr(g, 'start_time'):
            record.request_duration = (datetime.utcnow() - g.start_time).total_seconds()
        
        return True

def setup_logging(app: Flask):
    """Setup logging configuration for the Flask application"""
    
    # Get log level from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level, logging.INFO)
    
    # Clear existing handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # Set log level
    app.logger.setLevel(log_level)
    
    # Console handler for development
    if app.config.get('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Use simple format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
    
    # Google Cloud Logging for production
    if app.config.get('FLASK_ENV') == 'production':
        try:
            # Initialize Google Cloud Logging
            client = cloud_logging.Client()
            client.setup_logging()
            
            # Create a custom handler for structured logging
            cloud_handler = cloud_logging.handlers.CloudLoggingHandler(client)
            cloud_handler.setLevel(log_level)
            
            # Use JSON formatter for structured logs
            json_formatter = JSONFormatter()
            cloud_handler.setFormatter(json_formatter)
            
            # Add request context filter
            context_filter = RequestContextFilter()
            cloud_handler.addFilter(context_filter)
            
            app.logger.addHandler(cloud_handler)
            
            app.logger.info("Google Cloud Logging configured")
            
        except Exception as e:
            app.logger.error(f"Failed to setup Google Cloud Logging: {str(e)}")
            
            # Fallback to console logging with JSON format
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            
            json_formatter = JSONFormatter()
            console_handler.setFormatter(json_formatter)
            
            context_filter = RequestContextFilter()
            console_handler.addFilter(context_filter)
            
            app.logger.addHandler(console_handler)
    
    # Add request logging middleware
    @app.before_request
    def log_request():
        g.start_time = datetime.utcnow()
        g.request_id = os.urandom(8).hex()
        
        app.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'request_id': g.request_id
            }
        )
    
    @app.after_request
    def log_response(response):
        duration = (datetime.utcnow() - g.start_time).total_seconds()
        
        app.logger.info(
            f"Request completed: {response.status_code}",
            extra={
                'status_code': response.status_code,
                'duration': duration,
                'request_id': g.request_id
            }
        )
        
        return response
    
    # Log unhandled exceptions
    @app.errorhandler(Exception)
    def log_exception(error):
        app.logger.error(
            f"Unhandled exception: {str(error)}",
            extra={
                'exception_type': type(error).__name__,
                'request_id': getattr(g, 'request_id', None)
            },
            exc_info=True
        )
        
        return {
            'error': 'Internal server error',
            'request_id': getattr(g, 'request_id', None)
        }, 500

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

def log_performance_metric(metric_name: str, value: float, 
                          unit: str = "seconds", metadata: Optional[Dict[str, Any]] = None):
    """Log a performance metric"""
    logger = get_logger('performance')
    logger.info(
        f"Performance metric: {metric_name} = {value} {unit}",
        extra={
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit,
            'metadata': metadata or {},
            'metric_type': 'performance'
        }
    )

def log_business_event(event_name: str, data: Dict[str, Any]):
    """Log a business event"""
    logger = get_logger('business')
    logger.info(
        f"Business event: {event_name}",
        extra={
            'event_name': event_name,
            'event_data': data,
            'event_type': 'business'
        }
    )

def log_security_event(event_name: str, data: Dict[str, Any]):
    """Log a security event"""
    logger = get_logger('security')
    logger.warning(
        f"Security event: {event_name}",
        extra={
            'event_name': event_name,
            'event_data': data,
            'event_type': 'security'
        }
    )

def log_llm_interaction(interaction_type: str, input_data: Dict[str, Any], 
                       output_data: Optional[Dict[str, Any]] = None,
                       model: str = "gemini-pro", tokens_used: Optional[int] = None):
    """Log an LLM interaction"""
    logger = get_logger('llm')
    logger.info(
        f"LLM interaction: {interaction_type}",
        extra={
            'interaction_type': interaction_type,
            'model': model,
            'input_data': input_data,
            'output_data': output_data,
            'tokens_used': tokens_used,
            'interaction_type': 'llm'
        }
    )

def log_database_operation(operation: str, table: str, 
                          duration: Optional[float] = None,
                          metadata: Optional[Dict[str, Any]] = None):
    """Log a database operation"""
    logger = get_logger('database')
    logger.info(
        f"Database operation: {operation} on {table}",
        extra={
            'operation': operation,
            'table': table,
            'duration': duration,
            'metadata': metadata or {},
            'operation_type': 'database'
        }
    )

def log_api_call(endpoint: str, method: str, status_code: int,
                duration: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None):
    """Log an API call"""
    logger = get_logger('api')
    logger.info(
        f"API call: {method} {endpoint} -> {status_code}",
        extra={
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration': duration,
            'metadata': metadata or {},
            'call_type': 'api'
        }
    )
