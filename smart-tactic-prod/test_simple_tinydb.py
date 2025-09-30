#!/usr/bin/env python3
"""
Simple test script to verify TinyDB database setup
"""

import json
from pathlib import Path
from tinydb import TinyDB, Query

def test_tinydb_database():
    """Test TinyDB database"""
    print("🔍 Testing TinyDB database...")
    
    try:
        # Open database
        data_dir = Path(__file__).parent / 'data'
        db_path = data_dir / 'smart_tactic_tinydb.json'
        
        if not db_path.exists():
            print("❌ Database file not found")
            return False
        
        db = TinyDB(db_path)
        print(f"✅ Database opened: {db_path}")
        
        # Test tables
        tables = db.tables()
        print(f"✅ Tables found: {', '.join(tables)}")
        
        # Test form structure
        form_structures_table = db.table('form_structures')
        form_structures = form_structures_table.all()
        print(f"✅ Form structures: {len(form_structures)}")
        
        if form_structures:
            form_structure = form_structures[0]
            print(f"   • Form Name: {form_structure.get('form_name')}")
            print(f"   • Fields: {len(form_structure.get('form_mapping', {}))}")
            print(f"   • Sections: {len(form_structure.get('sections', []))}")
        
        # Test form options
        form_options_table = db.table('form_options')
        form_options = form_options_table.all()
        print(f"✅ Form options: {len(form_options)}")
        
        if form_options:
            print("   • Sample options:")
            for option in form_options[:3]:
                print(f"     - {option.get('field_id')}: {option.get('field_name')}")
        
        # Test autofill configs
        autofill_table = db.table('autofill_configs')
        autofill_configs = autofill_table.all()
        print(f"✅ Autofill configs: {len(autofill_configs)}")
        
        if autofill_configs:
            print("   • Sample configs:")
            for config in autofill_configs[:2]:
                print(f"     - {config.get('field_name')}: {config.get('event_type')}")
        
        # Test events
        events_table = db.table('events')
        events = events_table.all()
        print(f"✅ Events: {len(events)}")
        
        if events:
            event = events[0]
            print(f"   • Event Name: {event.get('eventName')}")
            print(f"   • Event Type: {event.get('event_type')}")
            print(f"   • Status: {event.get('status')}")
            print(f"   • Priority: {event.get('priority')}")
            print(f"   • Owner: {event.get('owner')}")
        
        # Test collections info
        collections_table = db.table('collections_info')
        collections_info = collections_table.all()
        print(f"✅ Collections info: {len(collections_info)}")
        
        if collections_info:
            info = collections_info[0]
            print(f"   • Description: {info.get('description')}")
            print(f"   • Collections: {len(info.get('collections', {}))}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing TinyDB database: {str(e)}")
        return False

def test_basic_operations():
    """Test basic TinyDB operations"""
    print("\n🔍 Testing basic TinyDB operations...")
    
    try:
        # Open database
        data_dir = Path(__file__).parent / 'data'
        db_path = data_dir / 'smart_tactic_tinydb.json'
        db = TinyDB(db_path)
        
        # Test insert
        test_table = db.table('test_operations')
        test_doc = {
            "test_field": "test_value",
            "test_number": 123,
            "test_boolean": True
        }
        
        doc_id = test_table.insert(test_doc)
        print(f"✅ Document inserted with ID: {doc_id}")
        
        # Test search
        query = Query()
        results = test_table.search(query.test_field == "test_value")
        print(f"✅ Document found: {len(results)} results")
        
        if results:
            print(f"   • Test Field: {results[0].get('test_field')}")
            print(f"   • Test Number: {results[0].get('test_number')}")
        
        # Test update
        test_table.update({"test_field": "updated_value"}, query.test_field == "test_value")
        updated_results = test_table.search(query.test_field == "updated_value")
        print(f"✅ Document updated: {len(updated_results)} results")
        
        # Test delete
        deleted_count = test_table.remove(query.test_field == "updated_value")
        print(f"✅ Document deleted: {deleted_count} documents")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing basic operations: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Simple TinyDB Database Test")
    print("=" * 50)
    
    tests = [
        ("TinyDB Database", test_tinydb_database),
        ("Basic Operations", test_basic_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   • {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! TinyDB database is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


