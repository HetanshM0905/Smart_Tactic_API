"""
Context Cache Service for optimizing LLM requests by caching workflow data
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SessionContext:
    session_id: str
    workflow_id: str
    workflow_hash: str
    context_sent: bool
    created_at: datetime
    last_accessed: datetime
    
class ContextCacheService:
    """Service to manage context caching for LLM requests"""
    
    def __init__(self, cache_ttl_hours: int = 2):
        self.session_contexts: Dict[str, SessionContext] = {}
        self.workflow_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
    def _generate_workflow_hash(self, workflow_data: Dict[str, Any]) -> str:
        """Generate hash for workflow data to detect changes"""
        workflow_str = json.dumps(workflow_data, sort_keys=True)
        return hashlib.md5(workflow_str.encode()).hexdigest()
    
    def _cleanup_expired_contexts(self):
        """Remove expired session contexts"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, context in self.session_contexts.items()
            if current_time - context.last_accessed > self.cache_ttl
        ]
        
        for session_id in expired_sessions:
            del self.session_contexts[session_id]
            logger.debug(f"Cleaned up expired context for session: {session_id}")
    
    def should_send_full_context(self, session_id: str, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Determine if full workflow context should be sent to LLM"""
        self._cleanup_expired_contexts()
        
        current_time = datetime.now()
        workflow_hash = self._generate_workflow_hash(workflow_data)
        
        if session_id not in self.session_contexts:
            # First request for this session
            self.session_contexts[session_id] = SessionContext(
                session_id=session_id,
                workflow_id=workflow_id,
                workflow_hash=workflow_hash,
                context_sent=True,
                created_at=current_time,
                last_accessed=current_time
            )
            logger.debug(f"First request for session {session_id} - sending full context")
            return True
        
        context = self.session_contexts[session_id]
        context.last_accessed = current_time
        
        # Check if workflow changed
        if context.workflow_hash != workflow_hash:
            context.workflow_hash = workflow_hash
            context.context_sent = True
            logger.debug(f"Workflow changed for session {session_id} - sending updated context")
            return True
        
        # Check if workflow_id changed
        if context.workflow_id != workflow_id:
            context.workflow_id = workflow_id
            context.workflow_hash = workflow_hash
            context.context_sent = True
            logger.debug(f"Workflow ID changed for session {session_id} - sending new context")
            return True
        
        logger.debug(f"Using cached context for session {session_id}")
        return False
    
    def get_optimized_prompt_context(self, session_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized context for prompt based on caching status"""
        if self.should_send_full_context(session_id, workflow_data.get('id', ''), workflow_data):
            logger.debug(f"Sending full workflow context for session {session_id}")
            return {
                'include_full_workflow': True,
                'workflow_data': workflow_data,
                'context_reference': None
            }
        else:
            logger.debug(f"Using cached workflow context for session {session_id}")
            return {
                'include_full_workflow': False,
                'workflow_data': None,
                'context_reference': f"[Using cached workflow context for session {session_id}]"
            }
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about context caching"""
        active_sessions = len(self.session_contexts)
        total_workflows_cached = len(set(ctx.workflow_id for ctx in self.session_contexts.values()))
        
        return {
            'active_sessions': active_sessions,
            'workflows_cached': total_workflows_cached,
            'cache_hit_potential': max(0, active_sessions - total_workflows_cached),
            'memory_saved_estimate': f"{total_workflows_cached * 50}KB"  # Rough estimate
        }
    
    def invalidate_session(self, session_id: str):
        """Invalidate cached context for a specific session"""
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
            logger.debug(f"Invalidated context cache for session: {session_id}")
    
    def clear_all_cache(self):
        """Clear all cached contexts"""
        self.session_contexts.clear()
        self.workflow_cache.clear()
        logger.info("Cleared all context cache")
