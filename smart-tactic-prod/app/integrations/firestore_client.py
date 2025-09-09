"""
Firestore client for unstructured data storage
Handles tactics, session state, and event documents
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class FirestoreClient:
    """Client for Firestore operations"""
    
    def __init__(self):
        self.config = Config()
        self.project_id = self.config.FIRESTORE_PROJECT_ID
        
        if not self.project_id:
            logger.warning("No Firestore project ID configured")
            self.db = None
        else:
            try:
                self.db = firestore.Client(project=self.project_id)
                logger.info(f"Firestore client initialized for project: {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {str(e)}")
                self.db = None
    
    def store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store event data in Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            # Prepare document data
            doc_data = self._prepare_event_document(event_data)
            
            # Store in events collection
            doc_ref = self.db.collection('events').document(doc_data['event_id'])
            doc_ref.set(doc_data)
            
            logger.info(f"Event stored in Firestore: {doc_data['event_id']}")
            
            return {
                'success': True,
                'document_id': doc_data['event_id'],
                'path': f"events/{doc_data['event_id']}"
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error storing event: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Retrieve event data from Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            doc_ref = self.db.collection('events').document(event_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Event retrieved from Firestore: {event_id}")
                return {
                    'success': True,
                    'data': data,
                    'document_id': event_id
                }
            else:
                logger.warning(f"Event not found in Firestore: {event_id}")
                return {
                    'success': False,
                    'error': f"Event not found: {event_id}"
                }
                
        except GoogleCloudError as e:
            logger.error(f"Firestore error retrieving event: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update event data in Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            # Prepare update data
            update_data = self._prepare_update_document(event_data)
            
            # Update document
            doc_ref = self.db.collection('events').document(event_id)
            doc_ref.update(update_data)
            
            logger.info(f"Event updated in Firestore: {event_id}")
            
            return {
                'success': True,
                'document_id': event_id,
                'updated_fields': list(update_data.keys())
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error updating event: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error updating event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete event from Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            doc_ref = self.db.collection('events').document(event_id)
            doc_ref.delete()
            
            logger.info(f"Event deleted from Firestore: {event_id}")
            
            return {
                'success': True,
                'document_id': event_id
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error deleting event: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error deleting event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def query_events(self, filters: Dict[str, Any], limit: int = 100) -> Dict[str, Any]:
        """Query events with filters"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            query = self.db.collection('events')
            
            # Apply filters
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Handle range queries
                    if 'gte' in value:
                        query = query.where(field, '>=', value['gte'])
                    if 'lte' in value:
                        query = query.where(field, '<=', value['lte'])
                    if 'gt' in value:
                        query = query.where(field, '>', value['gt'])
                    if 'lt' in value:
                        query = query.where(field, '<', value['lt'])
                else:
                    # Handle equality queries
                    query = query.where(field, '==', value)
            
            # Apply limit
            query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['document_id'] = doc.id
                results.append(data)
            
            logger.info(f"Query returned {len(results)} events")
            
            return {
                'success': True,
                'results': results,
                'count': len(results)
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error querying events: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error querying events: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_tactic(self, tactic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store tactic data in Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            # Prepare tactic document
            doc_data = self._prepare_tactic_document(tactic_data)
            
            # Store in tactics collection
            doc_ref = self.db.collection('tactics').document(doc_data['tactic_id'])
            doc_ref.set(doc_data)
            
            logger.info(f"Tactic stored in Firestore: {doc_data['tactic_id']}")
            
            return {
                'success': True,
                'document_id': doc_data['tactic_id'],
                'path': f"tactics/{doc_data['tactic_id']}"
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error storing tactic: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing tactic: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_tactic(self, tactic_id: str) -> Dict[str, Any]:
        """Retrieve tactic data from Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            doc_ref = self.db.collection('tactics').document(tactic_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Tactic retrieved from Firestore: {tactic_id}")
                return {
                    'success': True,
                    'data': data,
                    'document_id': tactic_id
                }
            else:
                return {
                    'success': False,
                    'error': f"Tactic not found: {tactic_id}"
                }
                
        except GoogleCloudError as e:
            logger.error(f"Firestore error retrieving tactic: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving tactic: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_session_state(self, session_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store session state in Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            # Prepare session document
            doc_data = {
                'session_id': session_id,
                'state': state_data,
                'updated_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            # Store in sessions collection
            doc_ref = self.db.collection('sessions').document(session_id)
            doc_ref.set(doc_data)
            
            logger.info(f"Session state stored in Firestore: {session_id}")
            
            return {
                'success': True,
                'document_id': session_id,
                'path': f"sessions/{session_id}"
            }
            
        except GoogleCloudError as e:
            logger.error(f"Firestore error storing session state: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing session state: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session state from Firestore"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Firestore client not initialized'}
            
            doc_ref = self.db.collection('sessions').document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Session state retrieved from Firestore: {session_id}")
                return {
                    'success': True,
                    'data': data,
                    'document_id': session_id
                }
            else:
                return {
                    'success': False,
                    'error': f"Session not found: {session_id}"
                }
                
        except GoogleCloudError as e:
            logger.error(f"Firestore error retrieving session state: {str(e)}")
            return {'success': False, 'error': f"Firestore error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving session state: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_event_document(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare event data for Firestore storage"""
        doc_data = event_data.copy()
        
        # Ensure required fields
        if 'event_id' not in doc_data:
            doc_data['event_id'] = event_data.get('id', 'unknown')
        
        # Add metadata
        doc_data['firestore_created_at'] = datetime.utcnow()
        doc_data['firestore_updated_at'] = datetime.utcnow()
        
        # Convert datetime objects to Firestore timestamps
        for key, value in doc_data.items():
            if isinstance(value, datetime):
                doc_data[key] = value
        
        return doc_data
    
    def _prepare_tactic_document(self, tactic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tactic data for Firestore storage"""
        doc_data = tactic_data.copy()
        
        # Ensure required fields
        if 'tactic_id' not in doc_data:
            doc_data['tactic_id'] = tactic_data.get('id', 'unknown')
        
        # Add metadata
        doc_data['firestore_created_at'] = datetime.utcnow()
        doc_data['firestore_updated_at'] = datetime.utcnow()
        
        return doc_data
    
    def _prepare_update_document(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare update data for Firestore"""
        update_data = event_data.copy()
        
        # Add update timestamp
        update_data['firestore_updated_at'] = datetime.utcnow()
        
        # Convert datetime objects
        for key, value in update_data.items():
            if isinstance(value, datetime):
                update_data[key] = value
        
        return update_data
