import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_form():
    """Test creating a new form"""
    print("\nTesting create form...")
    
    # Sample form data based on mockdata.json structure
    form_data = {
        "category": "promote",
        "tactic_type": "Events & Experiences",
        "event_kind": "Single",
        "aligned_to_multi_event": False,
        "basic": {
            "event_name": "Test Marketing Event 2024",
            "description": "A test event for API testing",
            "priority": "P0 - In budget",
            "owner_email": "test@example.com",
            "start_date": "2024-12-01",
            "end_date": "2024-12-01",
            "event_date_confidence": "High",
            "leads_expected": True,
            "no_of_inquiries": 50
        },
        "organization": {
            "ring": "Ring 1: Global 1st Party",
            "party": "1st party event",
            "category": "Digital AI moments",
            "subcategory": ""
        },
        "logistics": {
            "funding_status": "Fully Funded",
            "hosting_type": "Digital Event",
            "city": "",
            "countries": ["United States", "United Kingdom"]
        },
        "finance": {
            "cloud_marketing_cost_center": "CC-US",
            "has_spend": True,
            "total_budget": 10000.00,
            "split_cost_center": False,
            "cost_center_split": []
        },
        "extras": {
            "venue": "Virtual",
            "registration_link": "https://example.com/register",
            "sales_kit_link": "https://example.com/sales-kit"
        },
        "partners": {
            "partner_involved": "No Partner Involvement",
            "partner_name": "",
            "lead_followup": "",
            "responsibilities": []
        },
        "forecasts": {
            "expected_registrations": 200,
            "expected_attendees": 150
        },
        "campaign_program": {
            "tied_to_program": True,
            "program_splits": [
                {"program": "AI - General", "percentage": 100.0}
            ],
            "adopt_adapt_invent": "Adopt: Full adoption"
        },
        "alignments": {
            "account_segment": ["Enterprise"],
            "account_segment_type": ["Digital Natives"],
            "buyer_segment_rollups": ["Executive", "Decision Maker"],
            "industry": ["Financial Services"],
            "product": ["GCP"],
            "customer_lifecycle": ["Existing"],
            "core_messaging": ["AI"]
        },
        "review": {
            "status_basic": True,
            "status_execution": False,
            "ready_for_activation": False
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/forms", json=form_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            return response.json().get('form_id')
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_form(form_id):
    """Test getting form details"""
    print(f"\nTesting get form (ID: {form_id})...")
    
    try:
        response = requests.get(f"{BASE_URL}/forms/{form_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            form_data = response.json()
            print(f"Form retrieved successfully!")
            print(f"Event Name: {form_data.get('basic', {}).get('event_name', 'N/A')}")
            print(f"Category: {form_data.get('category', 'N/A')}")
            print(f"Tactic Type: {form_data.get('tactic_type', 'N/A')}")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_form(form_id):
    """Test updating a form"""
    print(f"\nTesting update form (ID: {form_id})...")
    
    update_data = {
        "category": "build_manage",
        "basic": {
            "event_name": "Updated Test Marketing Event 2024",
            "description": "Updated description for API testing"
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/forms/{form_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_forms():
    """Test listing all forms"""
    print("\nTesting list forms...")
    
    try:
        response = requests.get(f"{BASE_URL}/forms")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            forms_data = response.json()
            forms = forms_data.get('forms', [])
            print(f"Found {len(forms)} forms:")
            for form in forms:
                print(f"  - ID: {form['id']}, Name: {form['event_name']}, Category: {form['category']}")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_delete_form(form_id):
    """Test deleting a form"""
    print(f"\nTesting delete form (ID: {form_id})...")
    
    try:
        response = requests.delete(f"{BASE_URL}/forms/{form_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("Starting SmartTactic API Tests...")
    print("=" * 50)
    
    # Wait a moment for the API to be ready
    print("Waiting for API to be ready...")
    time.sleep(2)
    
    # Test health check
    if not test_health_check():
        print("Health check failed. Make sure the API is running.")
        return
    
    # Test create form
    form_id = test_create_form()
    if not form_id:
        print("Failed to create form. Stopping tests.")
        return
    
    # Test get form
    test_get_form(form_id)
    
    # Test list forms
    test_list_forms()
    
    # Test update form
    test_update_form(form_id)
    
    # Verify update
    test_get_form(form_id)
    
    # Test delete form
    test_delete_form(form_id)
    
    # Verify deletion
    test_get_form(form_id)
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()
