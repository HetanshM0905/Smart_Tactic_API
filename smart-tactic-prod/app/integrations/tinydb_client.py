"""
TinyDB client for Smart Tactics application
Handles data operations using TinyDB NoSQL database
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TinyDBClient:
    """TinyDB client for data operations"""
    
    def __init__(self, db_path: str = None):
        self.config = Config()
        self.db_path = db_path or self._get_default_db_path()
        self.db = None
        self._initialize_database()
    
    def _get_default_db_path(self) -> str:
        """Get default database path"""
        data_dir = Path(__file__).parent.parent.parent / 'data'
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / 'smart_tactic_tinydb.json')
    
    def _initialize_database(self):
        """Initialize TinyDB database"""
        try:
            # Use caching middleware for better performance
            storage = CachingMiddleware(JSONStorage)
            self.db = TinyDB(self.db_path, storage=storage)
            logger.info(f"TinyDB initialized at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize TinyDB: {str(e)}")
            self.db = None
    
    def _get_table(self, collection_name: str):
        """Get TinyDB table for collection"""
        if not self.db:
            raise Exception("Database not initialized")
        return self.db.table(collection_name)
    
    def store_document(self, collection_name: str, document_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a document in the collection"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            # Add metadata
            document_data['_id'] = document_id
            document_data['_created_at'] = datetime.utcnow().isoformat()
            document_data['_updated_at'] = datetime.utcnow().isoformat()
            
            table = self._get_table(collection_name)
            query = Query()
            
            # Check if document exists
            existing = table.search(query._id == document_id)
            
            if existing:
                # Update existing document
                table.update(document_data, query._id == document_id)
                logger.info(f"Document {document_id} updated in collection {collection_name}")
            else:
                # Insert new document
                table.insert(document_data)
                logger.info(f"Document {document_id} inserted in collection {collection_name}")
            
            return {'success': True, 'document_id': document_id}
            
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_document(self, collection_name: str, document_id: str) -> Dict[str, Any]:
        """Get a document from the collection"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            table = self._get_table(collection_name)
            query = Query()
            
            result = table.search(query._id == document_id)
            
            if result:
                logger.info(f"Document {document_id} retrieved from collection {collection_name}")
                return {'success': True, 'data': result[0]}
            else:
                return {'success': False, 'error': f'Document {document_id} not found'}
                
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_documents(self, collection_name: str, filters: Optional[Dict[str, Any]] = None, 
                     limit: Optional[int] = None, order_by: Optional[str] = None) -> Dict[str, Any]:
        """Get multiple documents from the collection"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            table = self._get_table(collection_name)
            query = Query()
            
            # Apply filters
            if filters:
                # Build query conditions
                conditions = []
                for key, value in filters.items():
                    if key.startswith('_'):
                        continue  # Skip metadata fields
                    conditions.append((query[key] == value))
                
                if conditions:
                    # Combine conditions with AND
                    combined_query = conditions[0]
                    for condition in conditions[1:]:
                        combined_query = combined_query & condition
                    results = table.search(combined_query)
                else:
                    results = table.all()
            else:
                results = table.all()
            
            # Apply ordering
            if order_by and results:
                try:
                    results.sort(key=lambda x: x.get(order_by, ''))
                except Exception as e:
                    logger.warning(f"Could not sort by {order_by}: {str(e)}")
            
            # Apply limit
            if limit:
                results = results[:limit]
            
            logger.info(f"Retrieved {len(results)} documents from collection {collection_name}")
            return {'success': True, 'data': results, 'count': len(results)}
            
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_document(self, collection_name: str, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in the collection"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            table = self._get_table(collection_name)
            query = Query()
            
            # Add update timestamp
            updates['_updated_at'] = datetime.utcnow().isoformat()
            
            # Update document
            updated_count = table.update(updates, query._id == document_id)
            
            if updated_count:
                logger.info(f"Document {document_id} updated in collection {collection_name}")
                return {'success': True, 'document_id': document_id}
            else:
                return {'success': False, 'error': f'Document {document_id} not found'}
                
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_document(self, collection_name: str, document_id: str) -> Dict[str, Any]:
        """Delete a document from the collection"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            table = self._get_table(collection_name)
            query = Query()
            
            # Delete document
            deleted_count = table.remove(query._id == document_id)
            
            if deleted_count:
                logger.info(f"Document {document_id} deleted from collection {collection_name}")
                return {'success': True, 'document_id': document_id}
            else:
                return {'success': False, 'error': f'Document {document_id} not found'}
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_form_structure(self) -> Dict[str, Any]:
        """Get form structure"""
        try:
            result = self.get_document('form_structures', 'smart_tactic_form')
            if result['success']:
                return result
            else:
                # Try to load from JSON file as fallback
                return self._load_from_json_file('form_structure.json')
        except Exception as e:
            logger.error(f"Error getting form structure: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_form_options(self) -> Dict[str, Any]:
        """Get form options"""
        try:
            result = self.get_documents('form_options')
            if result['success']:
                return result
            else:
                # Try to load from JSON file as fallback
                return self._load_from_json_file('form_options.json')
        except Exception as e:
            logger.error(f"Error getting form options: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_autofill_configs(self, event_type: Optional[str] = None) -> Dict[str, Any]:
        """Get autofill configurations"""
        try:
            filters = {'event_type': event_type} if event_type else None
            result = self.get_documents('autofill_configs', filters)
            if result['success']:
                return result
            else:
                # Try to load from JSON file as fallback
                return self._load_from_json_file('autofill_configs.json')
        except Exception as e:
            logger.error(f"Error getting autofill configs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _load_from_json_file(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file as fallback"""
        try:
            data_dir = Path(__file__).parent.parent.parent / 'data'
            file_path = data_dir / filename
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                return {'success': True, 'data': data}
            else:
                return {'success': False, 'error': f'File {filename} not found'}
        except Exception as e:
            logger.error(f"Error loading from JSON file {filename}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store an event"""
        event_id = event_data.get('event_id')
        if not event_id:
            return {'success': False, 'error': 'Event ID is required'}
        
        return self.store_document('events', event_id, event_data)
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get an event by ID"""
        return self.get_document('events', event_id)
    
    def get_events(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: Optional[int] = None) -> Dict[str, Any]:
        """Get multiple events"""
        return self.get_documents('events', filters, limit)
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an event"""
        return self.update_document('events', event_id, updates)
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete an event"""
        return self.delete_document('events', event_id)
    
    def health_check(self) -> Dict[str, Any]:
        """Check TinyDB client health"""
        try:
            if not self.db:
                return {'success': False, 'error': 'Database not initialized'}
            
            # Test basic operations
            test_data = {'test': True, 'timestamp': datetime.utcnow().isoformat()}
            store_result = self.store_document('test', 'health_check', test_data)
            
            if not store_result['success']:
                return {'success': False, 'error': 'Store test failed'}
            
            get_result = self.get_document('test', 'health_check')
            
            if not get_result['success']:
                return {'success': False, 'error': 'Get test failed'}
            
            # Clean up test data
            self.delete_document('test', 'health_check')
            
            return {
                'success': True,
                'status': 'healthy',
                'storage_type': 'TinyDB',
                'database_path': self.db_path,
                'tables': list(self.db.tables())
            }
            
        except Exception as e:
            logger.error(f"TinyDB client health check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'unhealthy'
            }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
            logger.info("TinyDB connection closed")


