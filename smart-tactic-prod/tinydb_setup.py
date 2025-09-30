"""
TinyDB database setup script for Smart Tactics application
Uses TinyDB for NoSQL data storage
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from tinydb import TinyDB, Query
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TinyDBDatabaseSetup:
    """TinyDB database setup and management class"""
    
    def __init__(self):
        self.config = Config()
        self.data_dir = Path(__file__).parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / 'smart_tactic_tinydb.json'
        self.db = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize TinyDB database"""
        try:
            self.db = TinyDB(self.db_path)
            logger.info(f"TinyDB initialized at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize TinyDB: {str(e)}")
            self.db = None
    
    def load_json_data(self, json_file_path: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Loaded JSON data from {json_file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            return None
    
    def setup_form_structure(self, form_data: Dict[str, Any]) -> bool:
        """Setup form structure in TinyDB"""
        try:
            if not self.db:
                return False
            
            form_structure = {
                "_id": "smart_tactic_form",
                "form_name": "Smart Tactic Event Form",
                "form_mapping": form_data.get('form_structure', {}).get('form_mapping', {}),
                "sections": form_data.get('form_structure', {}).get('sections', []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in TinyDB
            form_structures_table = self.db.table('form_structures')
            query = Query()
            
            # Check if exists and update, otherwise insert
            existing = form_structures_table.search(query._id == "smart_tactic_form")
            if existing:
                form_structures_table.update(form_structure, query._id == "smart_tactic_form")
                logger.info("Updated existing form structure")
            else:
                form_structures_table.insert(form_structure)
                logger.info("Created new form structure")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up form structure: {str(e)}")
            return False
    
    def setup_form_options(self, form_data: Dict[str, Any]) -> bool:
        """Setup form options in TinyDB"""
        try:
            if not self.db:
                return False
            
            form_options = form_data.get('form_options', {})
            form_options_table = self.db.table('form_options')
            
            # Clear existing options
            form_options_table.truncate()
            
            # Insert new options
            for field_id, options in form_options.items():
                option_doc = {
                    "_id": field_id,
                    "field_id": field_id,
                    "field_name": self._get_field_name_from_mapping(field_id, form_data),
                    "options": options,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                form_options_table.insert(option_doc)
            
            logger.info(f"Inserted {len(form_options)} form options")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up form options: {str(e)}")
            return False
    
    def _get_field_name_from_mapping(self, field_id: str, form_data: Dict[str, Any]) -> str:
        """Get field name from form mapping"""
        form_mapping = form_data.get('form_structure', {}).get('form_mapping', {})
        return form_mapping.get(field_id, field_id)
    
    def setup_autofill_configs(self) -> bool:
        """Setup autofill configurations in TinyDB"""
        try:
            if not self.db:
                return False
            
            autofill_configs = [
                {
                    "_id": "autofill_001",
                    "event_type": "conference",
                    "field_name": "eventName",
                    "field_type": "text",
                    "autofill_rule": {
                        "type": "template",
                        "template": "Google Cloud {eventType} - {location}",
                        "priority": 1
                    },
                    "priority": 10,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "autofill_002",
                    "event_type": "conference",
                    "field_name": "priority",
                    "field_type": "select",
                    "autofill_rule": {
                        "type": "default",
                        "value": "P0 - In budget",
                        "priority": 1
                    },
                    "priority": 5,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "autofill_003",
                    "event_type": "conference",
                    "field_name": "hostingType",
                    "field_type": "select",
                    "autofill_rule": {
                        "type": "conditional",
                        "conditions": [
                            {"if": "venue", "then": "Physical Event"},
                            {"if": "registrationLink", "then": "Digital Event"}
                        ],
                        "default": "Hybrid Event",
                        "priority": 1
                    },
                    "priority": 8,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "autofill_004",
                    "event_type": "conference",
                    "field_name": "fundingStatus",
                    "field_type": "select",
                    "autofill_rule": {
                        "type": "default",
                        "value": "Fully Funded",
                        "priority": 1
                    },
                    "priority": 3,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            # Store in TinyDB
            autofill_table = self.db.table('autofill_configs')
            autofill_table.truncate()  # Clear existing
            
            for config in autofill_configs:
                autofill_table.insert(config)
            
            logger.info(f"Inserted {len(autofill_configs)} autofill configs")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up autofill configs: {str(e)}")
            return False
    
    def create_sample_event(self) -> bool:
        """Create a sample event in TinyDB"""
        try:
            if not self.db:
                return False
            
            sample_event = {
                "_id": "sample_event_001",
                "event_id": "sample_event_001",
                "event_type": "conference",
                "status": "draft",
                "eventName": "Google Cloud Next 2024",
                "eventDescription": "Annual Google Cloud conference showcasing latest innovations",
                "priority": "P0 - In budget",
                "owner": "demo_user@relanto.com",
                "eventStartDate": "2024-08-27T00:00:00Z",
                "eventEndDate": "2024-08-29T00:00:00Z",
                "EventDateConfidence": "High",
                "leads": "Yes",
                "numberOfInquiries": 1000,
                "eventRing": "R1",
                "eventParty": "P1",
                "eventCategory": "C1",
                "eventCategoryOwner": "C01",
                "eventSubCategory": "SC01",
                "eventSubCategoryOwner": "SCW01",
                "fundingStatus": "Fully Funded",
                "hostingType": "Hybrid Event",
                "city": "San Francisco",
                "costCenter": "CC-US",
                "hasSpend": "Yes",
                "totalBudget": 50000.0,
                "splitCostCenter": "No",
                "partnerInvolved": "No Partner Involvement",
                "tiedToProgram": True,
                "adoptAdaptInvent": "Adopt",
                "statusBasicDetails": True,
                "statusExecutionDetails": False,
                "readyForActivation": False,
                "venue": "Moscone Center",
                "registrationLink": "https://cloud.withgoogle.com/next",
                "salesKitLink": "https://cloud.google.com/sales-kit",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in TinyDB
            events_table = self.db.table('events')
            query = Query()
            
            # Check if exists and update, otherwise insert
            existing = events_table.search(query._id == "sample_event_001")
            if existing:
                events_table.update(sample_event, query._id == "sample_event_001")
                logger.info("Updated existing sample event")
            else:
                events_table.insert(sample_event)
                logger.info("Created new sample event")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample event: {str(e)}")
            return False
    
    def create_collections_structure(self) -> bool:
        """Create collections structure documentation"""
        try:
            if not self.db:
                return False
            
            collections_info = {
                "_id": "collections_info",
                "description": "Smart Tactic Collections Structure",
                "collections": {
                    "form_structures": {
                        "description": "Form structure definitions",
                        "primary_key": "_id",
                        "indexes": ["form_name"]
                    },
                    "form_options": {
                        "description": "Form field options and dependencies",
                        "primary_key": "_id",
                        "indexes": ["field_id", "field_name"]
                    },
                    "autofill_configs": {
                        "description": "Autofill configuration rules",
                        "primary_key": "_id",
                        "indexes": ["event_type", "field_name", "active"]
                    },
                    "events": {
                        "description": "Event data",
                        "primary_key": "_id",
                        "indexes": ["event_id", "event_type", "status", "owner"]
                    }
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in TinyDB
            collections_table = self.db.table('collections_info')
            query = Query()
            
            existing = collections_table.search(query._id == "collections_info")
            if existing:
                collections_table.update(collections_info, query._id == "collections_info")
            else:
                collections_table.insert(collections_info)
            
            logger.info("Created collections structure documentation")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collections structure: {str(e)}")
            return False
    
    def verify_setup(self) -> Dict[str, Any]:
        """Verify TinyDB database setup"""
        try:
            if not self.db:
                return {'error': 'Database not initialized'}
            
            verification = {
                "database_path": str(self.db_path),
                "database_exists": self.db_path.exists(),
                "tables": list(self.db.tables()),
                "form_structure": False,
                "form_options": False,
                "autofill_configs": False,
                "sample_event": False,
                "collections_info": False
            }
            
            # Check each table
            tables_to_check = [
                ("form_structures", "form_structure"),
                ("form_options", "form_options"),
                ("autofill_configs", "autofill_configs"),
                ("events", "sample_event"),
                ("collections_info", "collections_info")
            ]
            
            for table_name, key in tables_to_check:
                if table_name in verification["tables"]:
                    table = self.db.table(table_name)
                    count = len(table.all())
                    verification[key] = count > 0
                    logger.info(f"Verified {table_name}: {count} documents")
            
            return verification
            
        except Exception as e:
            logger.error(f"Error verifying setup: {str(e)}")
            return {'error': str(e)}
    
    def run_full_setup(self, json_file_path: str = None) -> bool:
        """Run complete TinyDB database setup"""
        logger.info("Starting TinyDB database setup...")
        
        if not self.db:
            logger.error("Database not initialized")
            return False
        
        # Load form data if provided
        form_data = None
        if json_file_path and os.path.exists(json_file_path):
            form_data = self.load_json_data(json_file_path)
            if not form_data:
                logger.error("Failed to load form data")
                return False
        
        # Setup form structure
        if form_data:
            if not self.setup_form_structure(form_data):
                logger.error("Failed to setup form structure")
                return False
        
        # Setup form options
        if form_data:
            if not self.setup_form_options(form_data):
                logger.error("Failed to setup form options")
                return False
        
        # Setup autofill configs
        if not self.setup_autofill_configs():
            logger.error("Failed to setup autofill configs")
            return False
        
        # Create sample event
        if not self.create_sample_event():
            logger.error("Failed to create sample event")
            return False
        
        # Create collections structure
        if not self.create_collections_structure():
            logger.error("Failed to create collections structure")
            return False
        
        # Verify setup
        verification = self.verify_setup()
        if 'error' not in verification:
            logger.info("TinyDB database setup completed successfully!")
            logger.info(f"Setup summary: {verification}")
            return True
        else:
            logger.error(f"TinyDB database setup verification failed: {verification['error']}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
            logger.info("TinyDB connection closed")

def main():
    """Main function to run TinyDB database setup"""
    import sys
    
    # Get JSON file path from command line or use default
    json_file_path = sys.argv[1] if len(sys.argv) > 1 else '../smart-tactic-test/refactored_code.json'
    
    # Initialize TinyDB database setup
    db_setup = TinyDBDatabaseSetup()
    
    try:
        # Run full setup
        success = db_setup.run_full_setup(json_file_path)
        
        if success:
            print("✅ TinyDB database setup completed successfully!")
            sys.exit(0)
        else:
            print("❌ TinyDB database setup failed!")
            sys.exit(1)
    finally:
        db_setup.close()

if __name__ == "__main__":
    main()


