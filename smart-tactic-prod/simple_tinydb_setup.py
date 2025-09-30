#!/usr/bin/env python3
"""
Simple TinyDB database setup script for Smart Tactics application
Creates TinyDB database with form structure and options from JSON data
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from tinydb import TinyDB, Query

def load_json_data(json_file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON data from file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✅ Loaded JSON data from {json_file_path}")
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {str(e)}")
        return None

def setup_tinydb_database(json_file_path: str) -> bool:
    """Setup TinyDB database with form data"""
    try:
        # Create data directory
        data_dir = Path(__file__).parent / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # Initialize TinyDB
        db_path = data_dir / 'smart_tactic_tinydb.json'
        db = TinyDB(db_path)
        print(f"✅ TinyDB initialized at: {db_path}")
        
        # Load form data
        form_data = load_json_data(json_file_path)
        if not form_data:
            return False
        
        # Setup form structure
        form_structure = {
            "_id": "smart_tactic_form",
            "form_name": "Smart Tactic Event Form",
            "form_mapping": form_data.get('form_structure', {}).get('form_mapping', {}),
            "sections": form_data.get('form_structure', {}).get('sections', []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        form_structures_table = db.table('form_structures')
        query = Query()
        
        existing = form_structures_table.search(query._id == "smart_tactic_form")
        if existing:
            form_structures_table.update(form_structure, query._id == "smart_tactic_form")
            print("✅ Updated existing form structure")
        else:
            form_structures_table.insert(form_structure)
            print("✅ Created new form structure")
        
        # Setup form options
        form_options = form_data.get('form_options', {})
        form_options_table = db.table('form_options')
        form_options_table.truncate()  # Clear existing
        
        for field_id, options in form_options.items():
            option_doc = {
                "_id": field_id,
                "field_id": field_id,
                "field_name": form_data.get('form_structure', {}).get('form_mapping', {}).get(field_id, field_id),
                "options": options,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            form_options_table.insert(option_doc)
        
        print(f"✅ Inserted {len(form_options)} form options")
        
        # Setup autofill configs
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
        
        autofill_table = db.table('autofill_configs')
        autofill_table.truncate()
        
        for config in autofill_configs:
            autofill_table.insert(config)
        
        print(f"✅ Inserted {len(autofill_configs)} autofill configs")
        
        # Create sample event
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
        
        events_table = db.table('events')
        query = Query()
        
        existing = events_table.search(query._id == "sample_event_001")
        if existing:
            events_table.update(sample_event, query._id == "sample_event_001")
            print("✅ Updated existing sample event")
        else:
            events_table.insert(sample_event)
            print("✅ Created new sample event")
        
        # Create collections info
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
        
        collections_table = db.table('collections_info')
        query = Query()
        
        existing = collections_table.search(query._id == "collections_info")
        if existing:
            collections_table.update(collections_info, query._id == "collections_info")
        else:
            collections_table.insert(collections_info)
        
        print("✅ Created collections structure documentation")
        
        # Verify setup
        print("\n📊 Setup Verification:")
        print(f"   • Database Path: {db_path}")
        print(f"   • Database Exists: {db_path.exists()}")
        print(f"   • Tables: {', '.join(db.tables())}")
        
        for table_name in db.tables():
            table = db.table(table_name)
            count = len(table.all())
            print(f"   • {table_name}: {count} documents")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up TinyDB database: {str(e)}")
        return False

def main():
    """Main function to run simple TinyDB database setup"""
    print("🚀 Starting Simple Smart Tactics TinyDB Database Setup...")
    
    # Get the path to the JSON file
    current_dir = Path(__file__).parent
    json_file_path = current_dir.parent / 'smart-tactic-test' / 'refactored_code.json'
    
    if not json_file_path.exists():
        print(f"❌ JSON file not found at: {json_file_path}")
        print("Please ensure the refactored_code.json file exists in the smart-tactic-test directory")
        return False
    
    print(f"📁 Using JSON file: {json_file_path}")
    
    # Run setup
    success = setup_tinydb_database(str(json_file_path))
    
    if success:
        print("\n🎉 Simple TinyDB database setup completed successfully!")
        print("\n✨ Your Smart Tactics TinyDB database is ready to use!")
        print("\n📁 Database file: data/smart_tactic_tinydb.json")
        print("\nNext steps:")
        print("   1. Use the TinyDB client for data operations")
        print("   2. Test the database with sample queries")
        print("   3. Integrate with your application")
        
        return True
    else:
        print("❌ Simple TinyDB database setup failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


