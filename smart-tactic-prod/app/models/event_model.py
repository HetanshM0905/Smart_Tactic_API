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
    """Event data model based on Smart Tactic form structure"""
    
    # Core fields
    event_id: str
    event_type: str = 'conference'
    status: str = 'draft'
    
    # Basic Info fields (from form structure)
    eventName: Optional[str] = None
    eventDescription: Optional[str] = None
    priority: Optional[str] = None
    owner: Optional[str] = None
    eventStartDate: Optional[datetime] = None
    eventEndDate: Optional[datetime] = None
    EventDateConfidence: Optional[str] = None
    leads: Optional[str] = None
    numberOfInquiries: Optional[int] = None
    
    # Event categorization
    eventRing: Optional[str] = None
    eventParty: Optional[str] = None
    eventCategory: Optional[str] = None
    eventCategoryOwner: Optional[str] = None
    eventSubCategory: Optional[str] = None
    eventSubCategoryOwner: Optional[str] = None
    
    # Logistics
    fundingStatus: Optional[str] = None
    hostingType: Optional[str] = None
    city: Optional[str] = None
    countries: Optional[str] = None
    
    # Financial Details
    costCenter: Optional[str] = None
    hasSpend: Optional[str] = None
    totalBudget: Optional[float] = None
    splitCostCenter: Optional[str] = None
    costCenterSplit: Optional[List[Dict[str, Any]]] = None
    
    # Partner Details
    partnerInvolved: Optional[str] = None
    partnerName: Optional[str] = None
    responsibilities: Optional[str] = None
    leadFollowUp: Optional[str] = None
    
    # Alignments
    account_segments: Optional[str] = None
    account_segment_type: Optional[str] = None
    buyer_segment_rollups: Optional[str] = None
    industries: Optional[str] = None
    products: Optional[str] = None
    customer_lifecycle: Optional[str] = None
    core_messaging: Optional[str] = None
    
    # Campaign Program
    tiedToProgram: Optional[bool] = None
    adoptAdaptInvent: Optional[str] = None
    
    # Review & Submit
    statusBasicDetails: Optional[bool] = None
    statusExecutionDetails: Optional[bool] = None
    readyForActivation: Optional[bool] = None
    
    # Extras
    venue: Optional[str] = None
    registrationLink: Optional[str] = None
    salesKitLink: Optional[str] = None
    
    # Metadata and system fields
    metadata: Dict[str, Any] = None
    form_fields: Dict[str, Any] = None
    layout: Dict[str, Any] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
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
        """Convert event to metadata dictionary for NoSQL storage"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'eventName': self.eventName,
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
        """Validate event data based on form structure"""
        errors = []
        warnings = []
        
        # Required field validation based on form structure
        if not self.eventName or not self.eventName.strip():
            errors.append("Event name is required")
        
        if not self.eventDescription or not self.eventDescription.strip():
            errors.append("Event description is required")
        
        if not self.priority:
            errors.append("Priority is required")
        
        if not self.owner:
            errors.append("Owner is required")
        
        if not self.eventStartDate:
            errors.append("Event start date is required")
        
        if not self.eventEndDate:
            errors.append("Event end date is required")
        
        if not self.EventDateConfidence:
            errors.append("Event date confidence is required")
        
        if not self.leads:
            errors.append("Leads expected field is required")
        
        if not self.eventRing:
            errors.append("Event ring is required")
        
        if not self.eventParty:
            errors.append("Event party is required")
        
        if not self.eventCategoryOwner:
            errors.append("Event category owner is required")
        
        if not self.eventSubCategoryOwner:
            errors.append("Event sub category owner is required")
        
        if not self.fundingStatus:
            errors.append("Funding status is required")
        
        if not self.hostingType:
            errors.append("Hosting type is required")
        
        if not self.costCenter:
            errors.append("Cost center is required")
        
        if not self.hasSpend:
            errors.append("Has spend field is required")
        
        if not self.partnerInvolved:
            errors.append("Partner involvement is required")
        
        if not self.tiedToProgram:
            errors.append("Tied to program field is required")
        
        if not self.adoptAdaptInvent:
            errors.append("Adopt/Adapt/Invent field is required")
        
        # Field length validation
        if self.eventName and len(self.eventName) > 200:
            errors.append("Event name must be less than 200 characters")
        
        if self.eventDescription and len(self.eventDescription) > 2000:
            errors.append("Event description must be less than 2000 characters")
        
        # Date validation
        if self.eventStartDate and self.eventEndDate:
            if self.eventStartDate > self.eventEndDate:
                errors.append("Event start date must be before end date")
        
        # Conditional field validation
        if self.leads == "Yes" and not self.numberOfInquiries:
            warnings.append("Number of inquiries should be provided when leads are expected")
        
        if self.hasSpend == "Yes":
            if not self.totalBudget:
                errors.append("Total budget is required when event has spend")
            if not self.splitCostCenter:
                errors.append("Split cost center field is required when event has spend")
        
        if self.splitCostCenter == "Yes" and not self.costCenterSplit:
            errors.append("Cost center split details are required when splitting budget")
        
        if self.partnerInvolved != "No Partner Involvement":
            if not self.partnerName:
                errors.append("Partner name is required when partner is involved")
            if not self.leadFollowUp:
                errors.append("Lead follow-up is required when partner is involved")
        
        # Location validation based on hosting type
        if self.hostingType in ["Physical Event", "Hybrid Event"] and not self.city:
            warnings.append("City should be provided for physical or hybrid events")
        
        if self.hostingType == "Digital Event" and not self.countries:
            warnings.append("Country should be provided for digital events")
        
        # Budget validation
        if self.totalBudget is not None and self.totalBudget < 0:
            errors.append("Total budget must be non-negative")
        
        if self.numberOfInquiries is not None and self.numberOfInquiries < 0:
            errors.append("Number of inquiries must be non-negative")
        
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
            'event_name': self.eventName,
            'event_type': self.event_type,
            'status': self.status,
            'priority': self.priority,
            'owner': self.owner,
            'start_date': self.eventStartDate.isoformat() if self.eventStartDate else None,
            'end_date': self.eventEndDate.isoformat() if self.eventEndDate else None,
            'hosting_type': self.hostingType,
            'funding_status': self.fundingStatus,
            'total_budget': self.totalBudget,
            'venue': self.venue,
            'city': self.city,
            'countries': self.countries,
            'partner_involved': self.partnerInvolved,
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
    
    def save_to_tinydb(self, tinydb_client=None) -> Dict[str, Any]:
        """Save event to TinyDB storage"""
        try:
            if tinydb_client is None:
                from app.integrations.tinydb_client import TinyDBClient
                tinydb_client = TinyDBClient()
            
            event_data = self.to_dict()
            result = tinydb_client.store_event(event_data)
            
            if result['success']:
                logger.info(f"Event {self.event_id} saved to TinyDB storage")
            else:
                logger.error(f"Failed to save event {self.event_id}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving event to TinyDB: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def load_from_tinydb(cls, event_id: str, tinydb_client=None) -> 'EventModel':
        """Load event from TinyDB storage"""
        try:
            if tinydb_client is None:
                from app.integrations.tinydb_client import TinyDBClient
                tinydb_client = TinyDBClient()
            
            result = tinydb_client.get_event(event_id)
            
            if result['success']:
                event_data = result['data']
                # Remove TinyDB metadata fields
                for key in ['_id', '_created_at', '_updated_at']:
                    event_data.pop(key, None)
                
                event = cls.from_dict(event_data)
                logger.info(f"Event {event_id} loaded from TinyDB storage")
                return event
            else:
                logger.error(f"Failed to load event {event_id}: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading event from TinyDB: {str(e)}")
            return None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventModel':
        """Create EventModel from dictionary"""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'eventStartDate', 'eventEndDate']
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Could not parse datetime for field {field}: {data[field]}")
        
        return cls(**data)
    
    @classmethod
    def create_draft(cls, event_id: str, event_name: str, event_type: str = 'conference', 
                    event_description: str = None) -> 'EventModel':
        """Create a new draft event"""
        return cls(
            event_id=event_id,
            eventName=event_name,
            event_type=event_type,
            eventDescription=event_description,
            status='draft'
        )
    
    @classmethod
    def create_from_template(cls, event_id: str, template: Dict[str, Any]) -> 'EventModel':
        """Create event from template"""
        event_data = template.copy()
        event_data['event_id'] = event_id
        event_data['status'] = 'draft'
        
        return cls.from_dict(event_data)
