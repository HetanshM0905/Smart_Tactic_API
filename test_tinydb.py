#!/usr/bin/env python3
"""
Test script for TinyDB database setup
Run this to verify your TinyDB connection and basic operations
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tinydb import TinyDB, Query
    print("✓ TinyDB dependencies imported successfully")
except ImportError as e:
    print(f"✗ Failed to import TinyDB dependencies: {e}")
    print("Please run: pip install tinydb")
    sys.exit(1)

def test_tinydb_connection():
    """Test basic TinyDB connection"""
    print("\n=== Testing TinyDB Connection ===")
    
    try:
        # Create a test database
        test_db_path = "test_tinydb.json"
        db = TinyDB(test_db_path)
        print(f"✓ Connected to TinyDB: {test_db_path}")
        
        return db, test_db_path
        
    except Exception as e:
        print(f"✗ Failed to connect to TinyDB: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_tables(db):
    """Test table creation and basic operations"""
    print("\n=== Testing Tables ===")
    
    try:
        # Create a test table
        test_table = db.table('test_table')
        
        # Create a test document
        test_data = {
            'test_field': 'test_value',
            'timestamp': datetime.now().isoformat(),
            'number': 42
        }
        
        doc_id = test_table.insert(test_data)
        print(f"✓ Created test document with ID: {doc_id}")
        
        # Read the document
        doc = test_table.get(doc_id=doc_id)
        if doc:
            print(f"✓ Read test document: {doc['test_field']}")
        else:
            print("✗ Failed to read test document")
            return False
        
        # Update the document
        test_table.update({'test_field': 'updated_value'}, doc_ids=[doc_id])
        print("✓ Updated test document")
        
        # Verify update
        updated_doc = test_table.get(doc_id=doc_id)
        if updated_doc and updated_doc['test_field'] == 'updated_value':
            print("✓ Update verified")
        else:
            print("✗ Update verification failed")
            return False
        
        # Delete the document
        test_table.remove(doc_ids=[doc_id])
        print("✓ Deleted test document")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test tables: {e}")
        return False

def test_query_operations(db):
    """Test basic query operations"""
    print("\n=== Testing Query Operations ===")
    
    try:
        # Create a test table with multiple documents
        test_table = db.table('test_query_table')
        
        # Add some test documents
        test_docs = [
            {'name': 'Alice', 'age': 25, 'city': 'New York'},
            {'name': 'Bob', 'age': 30, 'city': 'Los Angeles'},
            {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
        ]
        
        doc_ids = []
        for doc_data in test_docs:
            doc_id = test_table.insert(doc_data)
            doc_ids.append(doc_id)
        
        print("✓ Created test documents for querying")
        
        # Test simple query
        User = Query()
        results = test_table.search(User.age > 25)
        print(f"✓ Query result: {len(results)} documents with age > 25")
        
        # Test multiple conditions
        results = test_table.search((User.age > 25) & (User.city == 'Los Angeles'))
        print(f"✓ Complex query result: {len(results)} documents")
        
        # Test search with specific field
        results = test_table.search(User.name == 'Alice')
        if results and results[0]['name'] == 'Alice':
            print("✓ Field search working correctly")
        else:
            print("✗ Field search failed")
            return False
        
        # Clean up
        test_table.remove(doc_ids=doc_ids)
        print("✓ Cleaned up test documents")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test query operations: {e}")
        return False

def test_batch_operations(db):
    """Test batch operations"""
    print("\n=== Testing Batch Operations ===")
    
    try:
        # Create a test table
        test_table = db.table('test_batch_table')
        
        # Add multiple documents
        test_docs = []
        for i in range(3):
            doc_data = {
                'index': i,
                'value': f'value_{i}',
                'timestamp': datetime.now().isoformat()
            }
            doc_id = test_table.insert(doc_data)
            test_docs.append(doc_id)
        
        print("✓ Batch insert completed")
        
        # Verify documents were created
        all_docs = test_table.all()
        print(f"✓ Batch created {len(all_docs)} documents")
        
        # Test batch update
        for doc_id in test_docs:
            test_table.update({'updated': True}, doc_ids=[doc_id])
        print("✓ Batch update completed")
        
        # Verify updates
        updated_docs = test_table.search(Query().updated == True)
        if len(updated_docs) == 3:
            print("✓ Batch update verified")
        else:
            print("✗ Batch update verification failed")
            return False
        
        # Clean up
        test_table.remove(doc_ids=test_docs)
        print("✓ Cleaned up batch test documents")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test batch operations: {e}")
        return False

def test_smart_tactic_structure(db):
    """Test Smart Tactic specific structure"""
    print("\n=== Testing Smart Tactic Structure ===")
    
    try:
        # Create tables similar to Smart Tactic structure
        forms_table = db.table('forms')
        basic_table = db.table('form_basic')
        
        # Create a test form
        form_data = {
            'category': 'Event',
            'tactic_type': 'Conference',
            'event_kind': 'Single',
            'aligned_to_multi_event': False,
            'created_at': datetime.now().isoformat()
        }
        
        form_id = forms_table.insert(form_data)
        print(f"✓ Created test form with ID: {form_id}")
        
        # Create related basic info
        basic_data = {
            'form_id': form_id,
            'event_name': 'Test Conference',
            'description': 'A test conference',
            'owner_email': 'test@example.com',
            'created_at': datetime.now().isoformat()
        }
        
        basic_id = basic_table.insert(basic_data)
        print(f"✓ Created related basic info with ID: {basic_id}")
        
        # Test relationship query
        Form = Query()
        Basic = Query()
        
        # Get form by ID
        form = forms_table.get(doc_id=form_id)
        if form and form['category'] == 'Event':
            print("✓ Form retrieval working")
        else:
            print("✗ Form retrieval failed")
            return False
        
        # Get related basic info
        basic_info = basic_table.search(Basic.form_id == form_id)
        if basic_info and basic_info[0]['event_name'] == 'Test Conference':
            print("✓ Relationship query working")
        else:
            print("✗ Relationship query failed")
            return False
        
        # Clean up
        forms_table.remove(doc_ids=[form_id])
        basic_table.remove(doc_ids=[basic_id])
        print("✓ Cleaned up Smart Tactic test data")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test Smart Tactic structure: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting TinyDB Tests...")
    
    # Test connection
    db, test_db_path = test_tinydb_connection()
    if db is None:
        print("\n❌ TinyDB connection failed. Please check your configuration.")
        return
    
    # Test basic operations
    success = True
    success &= test_tables(db)
    success &= test_query_operations(db)
    success &= test_batch_operations(db)
    success &= test_smart_tactic_structure(db)
    
    # Clean up test database
    try:
        db.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        print(f"✓ Cleaned up test database: {test_db_path}")
    except Exception as e:
        print(f"⚠️  Could not clean up test database: {e}")
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! TinyDB is working correctly.")
        print("\nNext steps:")
        print("1. Run: python db_setup_tinydb.py")
        print("2. Run: python app_tinydb.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("="*50)

if __name__ == "__main__":
    main()
