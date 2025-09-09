#!/usr/bin/env python3
"""
Test script for TinyDB API endpoints
"""

import requests
import json
import time

def test_api():
    """Test the TinyDB API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🚀 Testing TinyDB API...")
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API. Make sure the server is running.")
        return
    
    # Test getting all forms (should be empty initially)
    try:
        response = requests.get(f"{base_url}/api/forms")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Get all forms: {len(data.get('forms', []))} forms found")
        else:
            print(f"✗ Get all forms failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Get all forms error: {e}")
    
    # Test creating a form
    test_form = {
        "category": "Event",
        "tactic_type": "Conference",
        "event_kind": "Single",
        "aligned_to_multi_event": False,
        "basic": {
            "event_name": "Test Conference",
            "description": "A test conference for API testing",
            "priority": "High",
            "owner_email": "test@example.com",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "event_date_confidence": "Confirmed",
            "leads_expected": True,
            "no_of_inquiries": 100
        },
        "organization": {
            "ring": "Ring 1",
            "party": "Marketing",
            "category": "Technology",
            "subcategory": "Cloud Computing"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/forms", json=test_form)
        if response.status_code == 201:
            data = response.json()
            form_id = data.get('form_id')
            print(f"✓ Created form with ID: {form_id}")
            
            # Test getting the specific form
            response = requests.get(f"{base_url}/api/forms/{form_id}")
            if response.status_code == 200:
                form_data = response.json()
                print(f"✓ Retrieved form: {form_data.get('basic', [{}])[0].get('event_name', 'Unknown')}")
            else:
                print(f"✗ Get form failed: {response.status_code}")
            
            # Test updating the form
            update_data = {
                "category": "Updated Event",
                "tactic_type": "Updated Conference"
            }
            response = requests.put(f"{base_url}/api/forms/{form_id}", json=update_data)
            if response.status_code == 200:
                print("✓ Updated form successfully")
            else:
                print(f"✗ Update form failed: {response.status_code}")
            
            # Test deleting the form
            response = requests.delete(f"{base_url}/api/forms/{form_id}")
            if response.status_code == 200:
                print("✓ Deleted form successfully")
            else:
                print(f"✗ Delete form failed: {response.status_code}")
                
        else:
            print(f"✗ Create form failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Create form error: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api()
