"""
SQL client for AlloyDB operations
Handles structured data, autofill configs, and fallback results
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Text, Integer, Boolean, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

# SQLAlchemy base
Base = declarative_base()

class EventMetadata(Base):
    """Event metadata table"""
    __tablename__ = 'event_metadata'
    
    event_id = Column(String(255), primary_key=True)
    event_type = Column(String(100))
    title = Column(String(500))
    status = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    metadata = Column(JSON)
    form_fields = Column(JSON)
    layout = Column(JSON)

class AutofillConfig(Base):
    """Autofill configuration table"""
    __tablename__ = 'autofill_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100))
    field_name = Column(String(100))
    field_type = Column(String(50))
    autofill_rule = Column(JSON)
    priority = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FallbackResult(Base):
    """Fallback processing results table"""
    __tablename__ = 'fallback_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_payload = Column(JSON)
    processed_payload = Column(JSON)
    status = Column(String(50))
    error_message = Column(Text)
    correction_method = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)

class WorkflowResult(Base):
    """Workflow execution results table"""
    __tablename__ = 'workflow_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(255), unique=True)
    workflow_type = Column(String(100))
    status = Column(String(50))
    steps = Column(JSON)
    duration = Column(Integer)  # in seconds
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class BatchResult(Base):
    """Batch processing results table"""
    __tablename__ = 'batch_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(255), unique=True)
    total_events = Column(Integer)
    processed_events = Column(Integer)
    failed_events = Column(Integer)
    duration = Column(Integer)  # in seconds
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SQLClient:
    """Client for AlloyDB operations"""
    
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.Session = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            # Build connection string
            connection_string = self._build_connection_string()
            
            if not connection_string:
                logger.warning("No AlloyDB connection configured")
                return
            
            # Create engine
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.info("AlloyDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AlloyDB client: {str(e)}")
            self.engine = None
            self.Session = None
    
    def _build_connection_string(self) -> Optional[str]:
        """Build database connection string"""
        host = self.config.ALLOYDB_HOST
        port = self.config.ALLOYDB_PORT
        database = self.config.ALLOYDB_DATABASE
        user = self.config.ALLOYDB_USER
        password = self.config.ALLOYDB_PASSWORD
        
        if not all([host, database, user, password]):
            return None
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            if self.engine:
                Base.metadata.create_all(self.engine)
                logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
    
    def store_event_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store event metadata in AlloyDB"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                # Create or update event metadata
                event_meta = EventMetadata(
                    event_id=metadata['event_id'],
                    event_type=metadata.get('event_type'),
                    title=metadata.get('title'),
                    status=metadata.get('status', 'draft'),
                    created_at=metadata.get('created_at', datetime.utcnow()),
                    updated_at=datetime.utcnow(),
                    metadata=metadata.get('metadata', {}),
                    form_fields=metadata.get('form_fields', {}),
                    layout=metadata.get('layout', {})
                )
                
                # Use merge to handle upsert
                session.merge(event_meta)
                session.commit()
                
                logger.info(f"Event metadata stored: {metadata['event_id']}")
                
                return {
                    'success': True,
                    'event_id': metadata['event_id']
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error storing event metadata: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing event metadata: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_event_metadata(self, event_id: str) -> Dict[str, Any]:
        """Retrieve event metadata from AlloyDB"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                event_meta = session.query(EventMetadata).filter_by(event_id=event_id).first()
                
                if event_meta:
                    data = {
                        'event_id': event_meta.event_id,
                        'event_type': event_meta.event_type,
                        'title': event_meta.title,
                        'status': event_meta.status,
                        'created_at': event_meta.created_at,
                        'updated_at': event_meta.updated_at,
                        'metadata': event_meta.metadata or {},
                        'form_fields': event_meta.form_fields or {},
                        'layout': event_meta.layout or {}
                    }
                    
                    logger.info(f"Event metadata retrieved: {event_id}")
                    return {
                        'success': True,
                        'data': data
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Event metadata not found: {event_id}"
                    }
                    
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving event metadata: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving event metadata: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_event_metadata(self, event_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update event metadata in AlloyDB"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                event_meta = session.query(EventMetadata).filter_by(event_id=event_id).first()
                
                if event_meta:
                    # Update fields
                    event_meta.event_type = metadata.get('event_type', event_meta.event_type)
                    event_meta.title = metadata.get('title', event_meta.title)
                    event_meta.status = metadata.get('status', event_meta.status)
                    event_meta.updated_at = datetime.utcnow()
                    event_meta.metadata = metadata.get('metadata', event_meta.metadata)
                    event_meta.form_fields = metadata.get('form_fields', event_meta.form_fields)
                    event_meta.layout = metadata.get('layout', event_meta.layout)
                    
                    session.commit()
                    
                    logger.info(f"Event metadata updated: {event_id}")
                    return {
                        'success': True,
                        'event_id': event_id
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Event metadata not found: {event_id}"
                    }
                    
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating event metadata: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error updating event metadata: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_autofill_configs(self, event_type: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve autofill configurations"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                query = session.query(AutofillConfig).filter_by(active=True)
                
                if event_type:
                    query = query.filter_by(event_type=event_type)
                
                configs = query.order_by(AutofillConfig.priority.desc()).all()
                
                results = []
                for config in configs:
                    results.append({
                        'id': config.id,
                        'event_type': config.event_type,
                        'field_name': config.field_name,
                        'field_type': config.field_type,
                        'autofill_rule': config.autofill_rule,
                        'priority': config.priority
                    })
                
                logger.info(f"Retrieved {len(results)} autofill configs")
                return {
                    'success': True,
                    'configs': results
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving autofill configs: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving autofill configs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_fallback_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store fallback processing result"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                fallback_result = FallbackResult(
                    original_payload=result_data.get('original_payload', {}),
                    processed_payload=result_data.get('processed_payload', {}),
                    status=result_data.get('status', 'unknown'),
                    error_message=result_data.get('error_message'),
                    correction_method=result_data.get('correction_method'),
                    timestamp=datetime.utcnow()
                )
                
                session.add(fallback_result)
                session.commit()
                
                logger.info(f"Fallback result stored: {fallback_result.id}")
                return {
                    'success': True,
                    'result_id': fallback_result.id
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error storing fallback result: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing fallback result: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_workflow_result(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store workflow execution result"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                workflow_result = WorkflowResult(
                    workflow_id=workflow_data['workflow_id'],
                    workflow_type=workflow_data.get('workflow_type', 'unknown'),
                    status=workflow_data.get('status', 'unknown'),
                    steps=workflow_data.get('steps', []),
                    duration=workflow_data.get('duration', 0),
                    error_message=workflow_data.get('error'),
                    created_at=datetime.utcnow()
                )
                
                session.merge(workflow_result)  # Use merge for upsert
                session.commit()
                
                logger.info(f"Workflow result stored: {workflow_data['workflow_id']}")
                return {
                    'success': True,
                    'workflow_id': workflow_data['workflow_id']
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error storing workflow result: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing workflow result: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def store_batch_result(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store batch processing result"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                batch_result = BatchResult(
                    batch_id=batch_data['batch_id'],
                    total_events=batch_data.get('total_events', 0),
                    processed_events=batch_data.get('processed_events', 0),
                    failed_events=batch_data.get('failed_events', 0),
                    duration=batch_data.get('duration', 0),
                    results=batch_data.get('results', []),
                    created_at=datetime.utcnow()
                )
                
                session.merge(batch_result)  # Use merge for upsert
                session.commit()
                
                logger.info(f"Batch result stored: {batch_data['batch_id']}")
                return {
                    'success': True,
                    'batch_id': batch_data['batch_id']
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error storing batch result: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing batch result: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_workflow_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        try:
            if not self.Session:
                return {'success': False, 'error': 'Database not initialized'}
            
            session = self.Session()
            
            try:
                # Calculate date threshold
                threshold_date = datetime.utcnow() - timedelta(days=days)
                
                # Get workflow statistics
                total_workflows = session.query(WorkflowResult).filter(
                    WorkflowResult.created_at >= threshold_date
                ).count()
                
                successful_workflows = session.query(WorkflowResult).filter(
                    WorkflowResult.created_at >= threshold_date,
                    WorkflowResult.status == 'completed'
                ).count()
                
                failed_workflows = session.query(WorkflowResult).filter(
                    WorkflowResult.created_at >= threshold_date,
                    WorkflowResult.status == 'failed'
                ).count()
                
                # Get average duration
                avg_duration = session.query(
                    func.avg(WorkflowResult.duration)
                ).filter(
                    WorkflowResult.created_at >= threshold_date,
                    WorkflowResult.status == 'completed'
                ).scalar() or 0
                
                stats = {
                    'total_workflows': total_workflows,
                    'successful_workflows': successful_workflows,
                    'failed_workflows': failed_workflows,
                    'success_rate': (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
                    'average_duration': float(avg_duration),
                    'period_days': days
                }
                
                logger.info(f"Retrieved workflow stats for {days} days")
                return {
                    'success': True,
                    'stats': stats
                }
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving workflow stats: {str(e)}")
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving workflow stats: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.engine:
                return {'success': False, 'error': 'Database not initialized'}
            
            # Test connection
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                'success': True,
                'status': 'healthy',
                'database': 'AlloyDB'
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'unhealthy'
            }
