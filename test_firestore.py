#!/usr/bin/env python3
"""
Test script for Firestore database setup
Run this to verify your Firestore connection and basic operations
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from google.cloud import firestore
    from google.oauth2 import service_account
    print("✓ Firestore dependencies imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Firestore dependencies: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

def test_firestore_connection():
    """Test basic Firestore connection"""
    print("\n=== Testing Firestore Connection ===")
    
    try:
        # Check environment variables
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        print(f"Project ID: {project_id or 'Not set'}")
        print(f"Credentials: {credentials_path or 'Using default'}")
        
        if not project_id:
            print("⚠️  GOOGLE_CLOUD_PROJECT_ID not set - using default project")
        
        # Try to connect
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = firestore.Client(credentials=credentials)
            print("✓ Connected using service account credentials")
        else:
            client = firestore.Client()
            print("✓ Connected using default credentials")
        
        return client
        
    except Exception as e:
        print(f"✗ Failed to connect to Firestore: {e}")
        return None

def test_collections(client):
    """Test collection creation and basic operations"""
    print("\n=== Testing Collections ===")
    
    try:
        # Test collection
        test_collection = client.collection('test_collection')
        
        # Create a test document
        test_doc = test_collection.document('test_doc')
        test_data = {
            'test_field': 'test_value',
            'timestamp': datetime.now(),
            'number': 42
        }
        
        test_doc.set(test_data)
        print("✓ Created test document")
        
        # Read the document
        doc = test_doc.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"✓ Read test document: {data['test_field']}")
        else:
            print("✗ Failed to read test document")
            return False
        
        # Update the document
        test_doc.update({'test_field': 'updated_value'})
        print("✓ Updated test document")
        
        # Delete the document
        test_doc.delete()
        print("✓ Deleted test document")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test collections: {e}")
        return False

def test_query_operations(client):
    """Test basic query operations"""
    print("\n=== Testing Query Operations ===")
    
    try:
        # Create a test collection with multiple documents
        test_collection = client.collection('test_query_collection')
        
        # Add some test documents
        test_docs = [
            {'name': 'Alice', 'age': 25, 'city': 'New York'},
            {'name': 'Bob', 'age': 30, 'city': 'Los Angeles'},
            {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
        ]
        
        for doc_data in test_docs:
            test_collection.add(doc_data)
        
        print("✓ Created test documents for querying")
        
        # Test simple query
        docs = test_collection.where('age', '>', 25).stream()
        count = len(list(docs))
        print(f"✓ Query result: {count} documents with age > 25")
        
        # Test multiple conditions
        docs = test_collection.where('age', '>', 25).where('city', '==', 'Los Angeles').stream()
        count = len(list(docs))
        print(f"✓ Complex query result: {count} documents")
        
        # Clean up
        docs = test_collection.stream()
        for doc in docs:
            doc.reference.delete()
        print("✓ Cleaned up test documents")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test query operations: {e}")
        return False

def test_batch_operations(client):
    """Test batch operations"""
    print("\n=== Testing Batch Operations ===")
    
    try:
        # Create a batch
        batch = client.batch()
        
        # Add multiple operations to batch
        test_collection = client.collection('test_batch_collection')
        
        for i in range(3):
            doc_ref = test_collection.document(f'doc_{i}')
            batch.set(doc_ref, {
                'index': i,
                'value': f'value_{i}',
                'timestamp': datetime.now()
            })
        
        # Commit the batch
        batch.commit()
        print("✓ Batch write completed")
        
        # Verify documents were created
        docs = test_collection.stream()
        count = len(list(docs))
        print(f"✓ Batch created {count} documents")
        
        # Clean up
        docs = test_collection.stream()
        for doc in docs:
            doc.reference.delete()
        print("✓ Cleaned up batch test documents")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test batch operations: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Firestore Tests...")
    
    # Test connection
    client = test_firestore_connection()
    if not client:
        print("\n❌ Firestore connection failed. Please check your configuration.")
        return
    
    # Test basic operations
    success = True
    success &= test_collections(client)
    success &= test_query_operations(client)
    success &= test_batch_operations(client)
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! Firestore is working correctly.")
        print("\nNext steps:")
        print("1. Run: python db_setup_firestore.py")
        print("2. Run: python app_firestore.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("="*50)

if __name__ == "__main__":
    main()
