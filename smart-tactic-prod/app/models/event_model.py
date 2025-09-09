"""
Event data model for Smart Tactics application
Defines the structure and behavior of event objects
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from app.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class EventModel:
    """Event data model"""
    
    # Core fields
    event_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    status: str = 'draft'
    
    # Metadata
    metadata: Dict[str, Any] = None
    form_fields: Dict[str, Any] = None
    layout: Dict[str, Any] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Event details
    date: Optional[datetime] = None
    venue: Optional[str] = None
    capacity: Optional[int] = None
    duration: Optional[int] = None
    price: Optional[float] = None
    
    def __post_init__(self):
        """Initialize default values after object creation"""
        if self.metadata is None:
            self.metadata = {}
        if self.form_fields is None:
            self.form_fields = {}
        if self.layout is None:
            self.layout = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """Convert event to metadata dictionary for database storage"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'title': self.title,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata,
            'form_fields': self.form_fields,
            'layout': self.layout
        }
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update event with new data"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                # Store unknown fields in metadata
                self.metadata[key] = value
        
        self.updated_at = datetime.utcnow()
        logger.info(f"Event {self.event_id} updated")
    
    def validate(self) -> Dict[str, Any]:
        """Validate event data"""
        errors = []
        warnings = []
        
        # Required field validation
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if not self.event_type or not self.event_type.strip():
            errors.append("Event type is required")
        
        # Field length validation
        if self.title and len(self.title) > 200:
            errors.append("Title must be less than 200 characters")
        
        if self.description and len(self.description) > 2000:
            errors.append("Description must be less than 2000 characters")
        
        # Value validation
        if self.capacity is not None and self.capacity < 1:
            errors.append("Capacity must be at least 1")
        
        if self.duration is not None and self.duration < 0:
            errors.append("Duration must be non-negative")
        
        if self.price is not None and self.price < 0:
            errors.append("Price must be non-negative")
        
        # Business rule validation
        if self.status == 'published':
            if not self.date:
                warnings.append("Published events should have a date")
            
            if self.event_type in ['conference', 'workshop'] and self.price is None:
                warnings.append("Published events typically require a price")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def is_published(self) -> bool:
        """Check if event is published"""
        return self.status == 'published'
    
    def is_draft(self) -> bool:
        """Check if event is draft"""
        return self.status == 'draft'
    
    def is_cancelled(self) -> bool:
        """Check if event is cancelled"""
        return self.status == 'cancelled'
    
    def is_completed(self) -> bool:
        """Check if event is completed"""
        return self.status == 'completed'
    
    def get_contact_info(self) -> Dict[str, str]:
        """Get contact information"""
        contact = {}
        if self.email:
            contact['email'] = self.email
        if self.phone:
            contact['phone'] = self.phone
        return contact
    
    def has_contact_info(self) -> bool:
        """Check if event has contact information"""
        return bool(self.email or self.phone)
    
    def get_event_summary(self) -> Dict[str, Any]:
        """Get event summary for display"""
        return {
            'event_id': self.event_id,
            'title': self.title,
            'event_type': self.event_type,
            'status': self.status,
            'date': self.date.isoformat() if self.date else None,
            'venue': self.venue,
            'capacity': self.capacity,
            'has_contact': self.has_contact_info(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def add_form_field(self, field_name: str, field_config: Dict[str, Any]) -> None:
        """Add a form field to the event"""
        if 'fields' not in self.form_fields:
            self.form_fields['fields'] = []
        
        # Check if field already exists
        existing_field = None
        for field in self.form_fields['fields']:
            if field.get('name') == field_name:
                existing_field = field
                break
        
        if existing_field:
            # Update existing field
            existing_field.update(field_config)
        else:
            # Add new field
            field_config['name'] = field_name
            self.form_fields['fields'].append(field_config)
        
        self.updated_at = datetime.utcnow()
        logger.info(f"Form field '{field_name}' added/updated for event {self.event_id}")
    
    def remove_form_field(self, field_name: str) -> bool:
        """Remove a form field from the event"""
        if 'fields' not in self.form_fields:
            return False
        
        original_count = len(self.form_fields['fields'])
        self.form_fields['fields'] = [
            field for field in self.form_fields['fields']
            if field.get('name') != field_name
        ]
        
        removed = len(self.form_fields['fields']) < original_count
        if removed:
            self.updated_at = datetime.utcnow()
            logger.info(f"Form field '{field_name}' removed from event {self.event_id}")
        
        return removed
    
    def get_form_field(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific form field"""
        if 'fields' not in self.form_fields:
            return None
        
        for field in self.form_fields['fields']:
            if field.get('name') == field_name:
                return field
        
        return None
    
    def update_layout(self, layout_config: Dict[str, Any]) -> None:
        """Update event layout"""
        self.layout.update(layout_config)
        self.updated_at = datetime.utcnow()
        logger.info(f"Layout updated for event {self.event_id}")
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the event"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
        logger.info(f"Metadata '{key}' added to event {self.event_id}")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def remove_metadata(self, key: str) -> bool:
        """Remove metadata key"""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.utcnow()
            logger.info(f"Metadata '{key}' removed from event {self.event_id}")
            return True
        return False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventModel':
        """Create EventModel from dictionary"""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'date']
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Could not parse datetime for field {field}: {data[field]}")
        
        return cls(**data)
    
    @classmethod
    def create_draft(cls, event_id: str, title: str, event_type: str, 
                    description: str = None) -> 'EventModel':
        """Create a new draft event"""
        return cls(
            event_id=event_id,
            title=title,
            event_type=event_type,
            description=description,
            status='draft'
        )
    
    @classmethod
    def create_from_template(cls, event_id: str, template: Dict[str, Any]) -> 'EventModel':
        """Create event from template"""
        event_data = template.copy()
        event_data['event_id'] = event_id
        event_data['status'] = 'draft'
        
        return cls.from_dict(event_data)
