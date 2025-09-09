"""
Event orchestrator for coordinating complex event processing workflows
Manages the flow between different services and handles error recovery
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.event_handler import EventHandler
from app.services.fallback_engine import FallbackEngine
from app.services.autofill_engine import AutofillEngine
from app.integrations.firestore_client import FirestoreClient
from app.integrations.sql_client import SQLClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

class EventOrchestrator:
    """Orchestrates complex event processing workflows"""
    
    def __init__(self):
        self.event_handler = EventHandler()
        self.fallback_engine = FallbackEngine()
        self.autofill_engine = AutofillEngine()
        self.firestore_client = FirestoreClient()
        self.sql_client = SQLClient()
        self.workflow_cache = {}
    
    def orchestrate_event_creation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete event creation workflow"""
        try:
            workflow_id = self._generate_workflow_id()
            logger.info(f"Starting event creation workflow: {workflow_id}")
            
            # Initialize workflow tracking
            workflow_state = {
                'workflow_id': workflow_id,
                'status': 'started',
                'start_time': datetime.utcnow(),
                'steps': [],
                'payload': payload
            }
            
            # Step 1: Pre-processing validation
            preprocess_result = self._preprocess_event(payload)
            workflow_state['steps'].append({
                'step': 'preprocess',
                'status': 'completed' if preprocess_result['success'] else 'failed',
                'result': preprocess_result
            })
            
            if not preprocess_result['success']:
                return self._handle_workflow_failure(workflow_state, preprocess_result['error'])
            
            # Step 2: Event creation
            create_result = self.event_handler.create_event(preprocess_result['processed_payload'])
            workflow_state['steps'].append({
                'step': 'create_event',
                'status': 'completed' if create_result['success'] else 'failed',
                'result': create_result
            })
            
            if not create_result['success']:
                # Try fallback recovery
                fallback_result = self._attempt_fallback_recovery(workflow_state, create_result['error'])
                if fallback_result['success']:
                    create_result = fallback_result
                    workflow_state['steps'].append({
                        'step': 'fallback_recovery',
                        'status': 'completed',
                        'result': fallback_result
                    })
                else:
                    return self._handle_workflow_failure(workflow_state, create_result['error'])
            
            # Step 3: Post-processing
            postprocess_result = self._postprocess_event(create_result)
            workflow_state['steps'].append({
                'step': 'postprocess',
                'status': 'completed' if postprocess_result['success'] else 'failed',
                'result': postprocess_result
            })
            
            # Complete workflow
            workflow_state['status'] = 'completed'
            workflow_state['end_time'] = datetime.utcnow()
            workflow_state['duration'] = (workflow_state['end_time'] - workflow_state['start_time']).total_seconds()
            
            # Store workflow result
            self._store_workflow_result(workflow_state)
            
            logger.info(f"Event creation workflow completed: {workflow_id}")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'event_id': create_result.get('event_id'),
                'workflow_duration': workflow_state['duration'],
                'steps_completed': len([s for s in workflow_state['steps'] if s['status'] == 'completed'])
            }
            
        except Exception as e:
            logger.error(f"Error in event creation orchestration: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id if 'workflow_id' in locals() else None
            }
    
    def orchestrate_event_update(self, event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete event update workflow"""
        try:
            workflow_id = self._generate_workflow_id()
            logger.info(f"Starting event update workflow: {workflow_id} for event: {event_id}")
            
            # Initialize workflow tracking
            workflow_state = {
                'workflow_id': workflow_id,
                'event_id': event_id,
                'status': 'started',
                'start_time': datetime.utcnow(),
                'steps': [],
                'payload': payload
            }
            
            # Step 1: Validate event exists
            event_check = self._validate_event_exists(event_id)
            workflow_state['steps'].append({
                'step': 'validate_event',
                'status': 'completed' if event_check['success'] else 'failed',
                'result': event_check
            })
            
            if not event_check['success']:
                return self._handle_workflow_failure(workflow_state, event_check['error'])
            
            # Step 2: Analyze changes
            change_analysis = self._analyze_changes(event_id, payload)
            workflow_state['steps'].append({
                'step': 'analyze_changes',
                'status': 'completed' if change_analysis['success'] else 'failed',
                'result': change_analysis
            })
            
            # Step 3: Update event
            update_result = self.event_handler.update_event(event_id, payload)
            workflow_state['steps'].append({
                'step': 'update_event',
                'status': 'completed' if update_result['success'] else 'failed',
                'result': update_result
            })
            
            if not update_result['success']:
                return self._handle_workflow_failure(workflow_state, update_result['error'])
            
            # Step 4: Handle dependent updates
            dependent_updates = self._handle_dependent_updates(event_id, change_analysis.get('changes', []))
            workflow_state['steps'].append({
                'step': 'dependent_updates',
                'status': 'completed' if dependent_updates['success'] else 'failed',
                'result': dependent_updates
            })
            
            # Complete workflow
            workflow_state['status'] = 'completed'
            workflow_state['end_time'] = datetime.utcnow()
            workflow_state['duration'] = (workflow_state['end_time'] - workflow_state['start_time']).total_seconds()
            
            # Store workflow result
            self._store_workflow_result(workflow_state)
            
            logger.info(f"Event update workflow completed: {workflow_id}")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'event_id': event_id,
                'workflow_duration': workflow_state['duration'],
                'changes_applied': change_analysis.get('changes', []),
                'dependent_updates': dependent_updates.get('updates', [])
            }
            
        except Exception as e:
            logger.error(f"Error in event update orchestration: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id if 'workflow_id' in locals() else None
            }
    
    def orchestrate_batch_processing(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Orchestrate batch processing of multiple events"""
        try:
            batch_id = self._generate_workflow_id()
            logger.info(f"Starting batch processing: {batch_id} for {len(events)} events")
            
            batch_state = {
                'batch_id': batch_id,
                'status': 'started',
                'start_time': datetime.utcnow(),
                'total_events': len(events),
                'processed_events': 0,
                'failed_events': 0,
                'results': []
            }
            
            # Process events in parallel (with concurrency limit)
            semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent operations
            
            async def process_single_event(event_payload):
                async with semaphore:
                    return self.orchestrate_event_creation(event_payload)
            
            # Run batch processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                tasks = [process_single_event(event) for event in events]
                results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                
                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        batch_state['failed_events'] += 1
                        batch_state['results'].append({
                            'event_index': i,
                            'success': False,
                            'error': str(result)
                        })
                    elif result.get('success'):
                        batch_state['processed_events'] += 1
                        batch_state['results'].append({
                            'event_index': i,
                            'success': True,
                            'event_id': result.get('event_id'),
                            'workflow_id': result.get('workflow_id')
                        })
                    else:
                        batch_state['failed_events'] += 1
                        batch_state['results'].append({
                            'event_index': i,
                            'success': False,
                            'error': result.get('error')
                        })
                
            finally:
                loop.close()
            
            # Complete batch processing
            batch_state['status'] = 'completed'
            batch_state['end_time'] = datetime.utcnow()
            batch_state['duration'] = (batch_state['end_time'] - batch_state['start_time']).total_seconds()
            
            # Store batch result
            self._store_batch_result(batch_state)
            
            logger.info(f"Batch processing completed: {batch_id}")
            
            return {
                'success': True,
                'batch_id': batch_id,
                'total_events': batch_state['total_events'],
                'processed_events': batch_state['processed_events'],
                'failed_events': batch_state['failed_events'],
                'duration': batch_state['duration'],
                'results': batch_state['results']
            }
            
        except Exception as e:
            logger.error(f"Error in batch processing orchestration: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'batch_id': batch_id if 'batch_id' in locals() else None
            }
    
    def _preprocess_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process event payload before creation"""
        try:
            # Apply data normalization
            normalized_payload = self._normalize_payload(payload)
            
            # Apply business rules
            processed_payload = self._apply_business_rules(normalized_payload)
            
            # Validate processed payload
            validation_result = self._validate_processed_payload(processed_payload)
            
            if not validation_result['valid']:
                # Try to fix validation issues
                corrected_payload = self._fix_validation_issues(processed_payload, validation_result['errors'])
                return {
                    'success': True,
                    'processed_payload': corrected_payload,
                    'corrections_applied': True
                }
            
            return {
                'success': True,
                'processed_payload': processed_payload,
                'corrections_applied': False
            }
            
        except Exception as e:
            logger.error(f"Error in event preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _postprocess_event(self, create_result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process event after creation"""
        try:
            event_id = create_result.get('event_id')
            if not event_id:
                return {'success': False, 'error': 'No event ID in create result'}
            
            # Trigger dependent processes
            dependent_results = []
            
            # Update related events
            related_update = self._update_related_events(event_id)
            if related_update['success']:
                dependent_results.append(related_update)
            
            # Send notifications
            notification_result = self._send_creation_notifications(event_id)
            if notification_result['success']:
                dependent_results.append(notification_result)
            
            # Update analytics
            analytics_result = self._update_analytics(event_id)
            if analytics_result['success']:
                dependent_results.append(analytics_result)
            
            return {
                'success': True,
                'dependent_processes': dependent_results
            }
            
        except Exception as e:
            logger.error(f"Error in event postprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _attempt_fallback_recovery(self, workflow_state: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Attempt fallback recovery for failed operations"""
        try:
            logger.info(f"Attempting fallback recovery for error: {error}")
            
            # Use fallback engine to process the original payload
            original_payload = workflow_state['payload']
            fallback_result = self.fallback_engine.process_event(original_payload)
            
            if fallback_result['success']:
                # Try to create event with corrected payload
                corrected_payload = fallback_result['processed_payload']
                create_result = self.event_handler.create_event(corrected_payload)
                
                if create_result['success']:
                    return {
                        'success': True,
                        'event_id': create_result['event_id'],
                        'fallback_applied': True,
                        'original_error': error
                    }
            
            return {
                'success': False,
                'error': 'Fallback recovery failed',
                'original_error': error
            }
            
        except Exception as e:
            logger.error(f"Error in fallback recovery: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_error': error
            }
    
    def _validate_event_exists(self, event_id: str) -> Dict[str, Any]:
        """Validate that an event exists before updating"""
        try:
            result = self.firestore_client.get_event(event_id)
            return {
                'success': result['success'],
                'error': result.get('error') if not result['success'] else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_changes(self, event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes in the update payload"""
        try:
            # Get current event data
            current_result = self.firestore_client.get_event(event_id)
            if not current_result['success']:
                return {
                    'success': False,
                    'error': 'Could not retrieve current event data'
                }
            
            current_data = current_result['data']
            changes = []
            
            # Compare fields
            for key, new_value in payload.items():
                current_value = current_data.get(key)
                if current_value != new_value:
                    changes.append({
                        'field': key,
                        'old_value': current_value,
                        'new_value': new_value,
                        'change_type': self._determine_change_type(current_value, new_value)
                    })
            
            return {
                'success': True,
                'changes': changes,
                'change_count': len(changes)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing changes: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_dependent_updates(self, event_id: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle updates that depend on the event changes"""
        try:
            updates = []
            
            for change in changes:
                field = change['field']
                
                # Handle specific field dependencies
                if field == 'event_type':
                    type_update = self._update_event_type_dependencies(event_id, change['new_value'])
                    if type_update['success']:
                        updates.append(type_update)
                
                elif field == 'venue':
                    venue_update = self._update_venue_dependencies(event_id, change['new_value'])
                    if venue_update['success']:
                        updates.append(venue_update)
                
                elif field == 'date':
                    date_update = self._update_date_dependencies(event_id, change['new_value'])
                    if date_update['success']:
                        updates.append(date_update)
            
            return {
                'success': True,
                'updates': updates
            }
            
        except Exception as e:
            logger.error(f"Error handling dependent updates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_workflow_failure(self, workflow_state: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Handle workflow failure"""
        workflow_state['status'] = 'failed'
        workflow_state['end_time'] = datetime.utcnow()
        workflow_state['error'] = error
        
        # Store failed workflow
        self._store_workflow_result(workflow_state)
        
        logger.error(f"Workflow failed: {workflow_state['workflow_id']} - {error}")
        
        return {
            'success': False,
            'error': error,
            'workflow_id': workflow_state['workflow_id']
        }
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        return f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
    
    def _normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize payload data"""
        normalized = payload.copy()
        
        # Normalize string fields
        string_fields = ['title', 'description', 'event_type']
        for field in string_fields:
            if field in normalized and isinstance(normalized[field], str):
                normalized[field] = normalized[field].strip()
        
        # Normalize date fields
        if 'date' in normalized and isinstance(normalized['date'], str):
            try:
                normalized['date'] = datetime.fromisoformat(normalized['date'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        return normalized
    
    def _apply_business_rules(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to payload"""
        processed = payload.copy()
        
        # Set default values
        if not processed.get('status'):
            processed['status'] = 'draft'
        
        if not processed.get('created_at'):
            processed['created_at'] = datetime.utcnow()
        
        # Apply type-specific rules
        event_type = processed.get('event_type', '')
        if event_type == 'conference':
            if not processed.get('capacity'):
                processed['capacity'] = 100
        elif event_type == 'workshop':
            if not processed.get('duration'):
                processed['duration'] = 2
        
        return processed
    
    def _validate_processed_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processed payload"""
        errors = []
        
        # Required fields
        required_fields = ['title', 'event_type']
        for field in required_fields:
            if not payload.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Field-specific validation
        if payload.get('email') and '@' not in payload['email']:
            errors.append("Invalid email format")
        
        if payload.get('capacity') and not isinstance(payload['capacity'], int):
            errors.append("Capacity must be an integer")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _fix_validation_issues(self, payload: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Fix validation issues in payload"""
        fixed = payload.copy()
        
        for error in errors:
            if 'Missing required field: title' in error:
                fixed['title'] = 'Untitled Event'
            elif 'Missing required field: event_type' in error:
                fixed['event_type'] = 'general'
            elif 'Invalid email format' in error:
                fixed.pop('email', None)
            elif 'Capacity must be an integer' in error:
                try:
                    fixed['capacity'] = int(fixed['capacity'])
                except (ValueError, TypeError):
                    fixed['capacity'] = 100
        
        return fixed
    
    def _determine_change_type(self, old_value: Any, new_value: Any) -> str:
        """Determine the type of change"""
        if old_value is None and new_value is not None:
            return 'added'
        elif old_value is not None and new_value is None:
            return 'removed'
        else:
            return 'modified'
    
    def _update_event_type_dependencies(self, event_id: str, new_type: str) -> Dict[str, Any]:
        """Update dependencies when event type changes"""
        # This would update related configurations, templates, etc.
        return {'success': True, 'type': 'event_type_dependency'}
    
    def _update_venue_dependencies(self, event_id: str, new_venue: str) -> Dict[str, Any]:
        """Update dependencies when venue changes"""
        # This would update capacity, amenities, etc.
        return {'success': True, 'type': 'venue_dependency'}
    
    def _update_date_dependencies(self, event_id: str, new_date: Any) -> Dict[str, Any]:
        """Update dependencies when date changes"""
        # This would update scheduling, conflicts, etc.
        return {'success': True, 'type': 'date_dependency'}
    
    def _update_related_events(self, event_id: str) -> Dict[str, Any]:
        """Update related events"""
        return {'success': True, 'type': 'related_events'}
    
    def _send_creation_notifications(self, event_id: str) -> Dict[str, Any]:
        """Send notifications for event creation"""
        return {'success': True, 'type': 'notifications'}
    
    def _update_analytics(self, event_id: str) -> Dict[str, Any]:
        """Update analytics for event creation"""
        return {'success': True, 'type': 'analytics'}
    
    def _store_workflow_result(self, workflow_state: Dict[str, Any]) -> None:
        """Store workflow result for tracking"""
        try:
            self.sql_client.store_workflow_result(workflow_state)
        except Exception as e:
            logger.error(f"Failed to store workflow result: {str(e)}")
    
    def _store_batch_result(self, batch_state: Dict[str, Any]) -> None:
        """Store batch processing result"""
        try:
            self.sql_client.store_batch_result(batch_state)
        except Exception as e:
            logger.error(f"Failed to store batch result: {str(e)}")
