from flask import Flask, request, jsonify
import json
from datetime import datetime
import os
from google.cloud import firestore
from google.oauth2 import service_account

app = Flask(__name__)

# Firestore database configuration
class FirestoreDB:
    def __init__(self, credentials_path=None):
        """Initialize Firestore connection"""
        try:
            if credentials_path and os.path.exists(credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.db = firestore.Client(credentials=credentials)
            else:
                # Use default credentials (for local development or GCP environment)
                self.db = firestore.Client()
            
            # Initialize collections
            self.collections = {
                'forms': self.db.collection('forms'),
                'form_basic': self.db.collection('form_basic'),
                'form_organization': self.db.collection('form_organization'),
                'form_logistics': self.db.collection('form_logistics'),
                'form_countries': self.db.collection('form_countries'),
                'form_finance': self.db.collection('form_finance'),
                'form_cost_center_splits': self.db.collection('form_cost_center_splits'),
                'form_extras': self.db.collection('form_extras'),
                'form_partners': self.db.collection('form_partners'),
                'form_partner_responsibilities': self.db.collection('form_partner_responsibilities'),
                'form_forecasts': self.db.collection('form_forecasts'),
                'form_campaign_program': self.db.collection('form_campaign_program'),
                'form_program_splits': self.db.collection('form_program_splits'),
                'form_alignments': self.db.collection('form_alignments'),
                'form_review': self.db.collection('form_review')
            }
            
        except Exception as e:
            print(f"Error connecting to Firestore: {e}")
            raise

# Initialize database
try:
    # You can specify a path to your service account JSON file here
    # credentials_path = "path/to/your/service-account-key.json"
    credentials_path = None  # Will use default credentials
    db = FirestoreDB(credentials_path)
    print("Connected to Firestore successfully!")
except Exception as e:
    print(f"Failed to connect to Firestore: {e}")
    db = None

def validate_form_data(data):
    """Validate incoming form data"""
    required_fields = ['category', 'tactic_type', 'event_kind']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def create_form_in_firestore(form_data):
    """Create a new form in Firestore"""
    try:
        if not db:
            return False, "Database connection not available"
        
        # Create main form document
        main_form_data = {
            'category': form_data.get('category', ''),
            'tactic_type': form_data.get('tactic_type', ''),
            'event_kind': form_data.get('event_kind', 'Single'),
            'aligned_to_multi_event': form_data.get('aligned_to_multi_event', False),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Add to forms collection
        form_ref = db.collections['forms'].add(main_form_data)[1]
        form_id = form_ref.id
        print(f"Created form with ID: {form_id}")
        
        # Insert basic information if provided
        if 'basic' in form_data:
            basic = form_data['basic']
            basic_data = {
                'form_id': form_id,
                'event_name': basic.get('event_name', ''),
                'description': basic.get('description', ''),
                'priority': basic.get('priority', ''),
                'owner_email': basic.get('owner_email', ''),
                'start_date': basic.get('start_date', ''),
                'end_date': basic.get('end_date', ''),
                'event_date_confidence': basic.get('event_date_confidence', ''),
                'leads_expected': basic.get('leads_expected', False),
                'no_of_inquiries': basic.get('no_of_inquiries', 0),
                'created_at': datetime.now()
            }
            db.collections['form_basic'].add(basic_data)
        
        # Insert organization if provided
        if 'organization' in form_data:
            org = form_data['organization']
            org_data = {
                'form_id': form_id,
                'ring': org.get('ring', ''),
                'party': org.get('party', ''),
                'category': org.get('category', ''),
                'subcategory': org.get('subcategory', ''),
                'created_at': datetime.now()
            }
            db.collections['form_organization'].add(org_data)
        
        # Insert logistics if provided
        if 'logistics' in form_data:
            logistics = form_data['logistics']
            logistics_data = {
                'form_id': form_id,
                'funding_status': logistics.get('funding_status', ''),
                'hosting_type': logistics.get('hosting_type', ''),
                'city': logistics.get('city', ''),
                'created_at': datetime.now()
            }
            db.collections['form_logistics'].add(logistics_data)
            
            # Insert countries if provided
            if 'countries' in logistics and logistics['countries']:
                for country in logistics['countries']:
                    country_data = {
                        'form_id': form_id,
                        'country': country,
                        'created_at': datetime.now()
                    }
                    db.collections['form_countries'].add(country_data)
        
        # Insert finance if provided
        if 'finance' in form_data:
            finance = form_data['finance']
            finance_data = {
                'form_id': form_id,
                'cloud_marketing_cost_center': finance.get('cloud_marketing_cost_center', ''),
                'has_spend': finance.get('has_spend', False),
                'total_budget': float(finance.get('total_budget', 0)),
                'split_cost_center': finance.get('split_cost_center', False),
                'created_at': datetime.now()
            }
            db.collections['form_finance'].add(finance_data)
            
            # Insert cost center splits if provided
            if 'cost_center_split' in finance and finance['cost_center_split']:
                for split in finance['cost_center_split']:
                    if isinstance(split, dict):
                        split_data = {
                            'form_id': form_id,
                            'cost_center': split.get('cost_center', ''),
                            'percentage': float(split.get('percentage', 0)),
                            'created_at': datetime.now()
                        }
                        db.collections['form_cost_center_splits'].add(split_data)
        
        # Insert extras if provided
        if 'extras' in form_data:
            extras = form_data['extras']
            extras_data = {
                'form_id': form_id,
                'venue': extras.get('venue', ''),
                'registration_link': extras.get('registration_link', ''),
                'sales_kit_link': extras.get('sales_kit_link', ''),
                'created_at': datetime.now()
            }
            db.collections['form_extras'].add(extras_data)
        
        # Insert partners if provided
        if 'partners' in form_data:
            partners = form_data['partners']
            partners_data = {
                'form_id': form_id,
                'partner_involved': partners.get('partner_involved', 'No Partner Involvement'),
                'partner_name': partners.get('partner_name', ''),
                'lead_followup': partners.get('lead_followup', ''),
                'created_at': datetime.now()
            }
            db.collections['form_partners'].add(partners_data)
            
            # Insert partner responsibilities if provided
            if 'responsibilities' in partners and partners['responsibilities']:
                for resp in partners['responsibilities']:
                    resp_data = {
                        'form_id': form_id,
                        'responsibility': resp,
                        'created_at': datetime.now()
                    }
                    db.collections['form_partner_responsibilities'].add(resp_data)
        
        # Insert forecasts if provided
        if 'forecasts' in form_data:
            forecasts = form_data['forecasts']
            forecasts_data = {
                'form_id': form_id,
                'expected_registrations': forecasts.get('expected_registrations', 0),
                'expected_attendees': forecasts.get('expected_attendees', 0),
                'created_at': datetime.now()
            }
            db.collections['form_forecasts'].add(forecasts_data)
        
        # Insert campaign program if provided
        if 'campaign_program' in form_data:
            campaign = form_data['campaign_program']
            campaign_data = {
                'form_id': form_id,
                'tied_to_program': campaign.get('tied_to_program', False),
                'adopt_adapt_invent': campaign.get('adopt_adapt_invent', ''),
                'created_at': datetime.now()
            }
            db.collections['form_campaign_program'].add(campaign_data)
            
            # Insert program splits if provided
            if 'program_splits' in campaign and campaign['program_splits']:
                for split in campaign['program_splits']:
                    if isinstance(split, dict):
                        split_data = {
                            'form_id': form_id,
                            'program': split.get('program', ''),
                            'percentage': float(split.get('percentage', 0)),
                            'created_at': datetime.now()
                        }
                        db.collections['form_program_splits'].add(split_data)
        
        # Insert alignments if provided
        if 'alignments' in form_data:
            alignments = form_data['alignments']
            
            # Handle different alignment types
            alignment_fields = [
                'account_segment', 'account_segment_type', 'buyer_segment_rollups',
                'industry', 'product', 'customer_lifecycle', 'core_messaging'
            ]
            
            for field in alignment_fields:
                if field in alignments and alignments[field]:
                    for value in alignments[field]:
                        alignment_data = {
                            'form_id': form_id,
                            field: value,
                            'created_at': datetime.now()
                        }
                        db.collections['form_alignments'].add(alignment_data)
        
        # Insert review if provided
        if 'review' in form_data:
            review = form_data['review']
            review_data = {
                'form_id': form_id,
                'status_basic': review.get('status_basic', False),
                'status_execution': review.get('status_execution', False),
                'ready_for_activation': review.get('ready_for_activation', False),
                'created_at': datetime.now()
            }
            db.collections['form_review'].add(review_data)
        
        return True, form_id
        
    except Exception as e:
        print(f"Error creating form in Firestore: {e}")
        return False, str(e)

def get_form_from_firestore(form_id):
    """Get a complete form from Firestore by ID"""
    try:
        if not db:
            return None, "Database connection not available"
        
        # Get main form
        form_doc = db.collections['forms'].document(form_id).get()
        if not form_doc.exists:
            return None, "Form not found"
        
        form_data = form_doc.to_dict()
        form_data['id'] = form_id
        
        # Get all related data
        collections_to_fetch = [
            'form_basic', 'form_organization', 'form_logistics', 
            'form_finance', 'form_extras', 'form_partners', 
            'form_forecasts', 'form_campaign_program', 'form_review'
        ]
        
        for collection_name in collections_to_fetch:
            docs = db.collections[collection_name].where('form_id', '==', form_id).stream()
            form_data[collection_name] = [doc.to_dict() for doc in docs]
        
        # Get arrays (countries, cost center splits, etc.)
        countries = db.collections['form_countries'].where('form_id', '==', form_id).stream()
        form_data['countries'] = [doc.to_dict()['country'] for doc in countries]
        
        cost_splits = db.collections['form_cost_center_splits'].where('form_id', '==', form_id).stream()
        form_data['cost_center_splits'] = [doc.to_dict() for doc in cost_splits]
        
        partner_resps = db.collections['form_partner_responsibilities'].where('form_id', '==', form_id).stream()
        form_data['partner_responsibilities'] = [doc.to_dict()['responsibility'] for doc in partner_resps]
        
        program_splits = db.collections['form_program_splits'].where('form_id', '==', form_id).stream()
        form_data['program_splits'] = [doc.to_dict() for doc in program_splits]
        
        return form_data, None
        
    except Exception as e:
        print(f"Error getting form from Firestore: {e}")
        return None, str(e)

def get_all_forms_from_firestore():
    """Get all forms from Firestore"""
    try:
        if not db:
            return [], "Database connection not available"
        
        forms = []
        docs = db.collections['forms'].stream()
        
        for doc in docs:
            form_data = doc.to_dict()
            form_data['id'] = doc.id
            forms.append(form_data)
        
        return forms, None
        
    except Exception as e:
        print(f"Error getting all forms from Firestore: {e}")
        return [], str(e)

# API Routes
@app.route('/api/forms', methods=['POST'])
def create_form():
    """Create a new form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate form data
        is_valid, message = validate_form_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Create form in Firestore
        success, result = create_form_in_firestore(data)
        
        if success:
            return jsonify({
                'message': 'Form created successfully',
                'form_id': result
            }), 201
        else:
            return jsonify({'error': result}), 500
            
    except Exception as e:
        print(f"Error in create_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form(form_id):
    """Get a specific form by ID"""
    try:
        form_data, error = get_form_from_firestore(form_id)
        
        if error:
            return jsonify({'error': error}), 404
        
        return jsonify(form_data), 200
        
    except Exception as e:
        print(f"Error in get_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get all forms"""
    try:
        forms, error = get_all_forms_from_firestore()
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({'forms': forms}), 200
        
    except Exception as e:
        print(f"Error in get_forms: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['PUT'])
def update_form(form_id):
    """Update an existing form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if form exists
        existing_form, error = get_form_from_firestore(form_id)
        if error:
            return jsonify({'error': 'Form not found'}), 404
        
        # Update the form (this is a simplified update - you might want to implement more sophisticated update logic)
        # For now, we'll just update the main form document
        if 'category' in data or 'tactic_type' in data or 'event_kind' in data:
            update_data = {}
            if 'category' in data:
                update_data['category'] = data['category']
            if 'tactic_type' in data:
                update_data['tactic_type'] = data['tactic_type']
            if 'event_kind' in data:
                update_data['event_kind'] = data['event_kind']
            
            update_data['updated_at'] = datetime.now()
            
            db.collections['forms'].document(form_id).update(update_data)
        
        return jsonify({'message': 'Form updated successfully'}), 200
        
    except Exception as e:
        print(f"Error in update_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['DELETE'])
def delete_form(form_id):
    """Delete a form"""
    try:
        # Check if form exists
        existing_form, error = get_form_from_firestore(form_id)
        if error:
            return jsonify({'error': 'Form not found'}), 404
        
        # Delete all related documents
        collections_to_delete = [
            'form_basic', 'form_organization', 'form_logistics', 
            'form_countries', 'form_finance', 'form_cost_center_splits',
            'form_extras', 'form_partners', 'form_partner_responsibilities',
            'form_forecasts', 'form_campaign_program', 'form_program_splits',
            'form_alignments', 'form_review'
        ]
        
        for collection_name in collections_to_delete:
            docs = db.collections[collection_name].where('form_id', '==', form_id).stream()
            for doc in docs:
                doc.reference.delete()
        
        # Delete main form
        db.collections['forms'].document(form_id).delete()
        
        return jsonify({'message': 'Form deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error in delete_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if db:
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    if db:
        print("Starting Flask app with Firestore...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Cannot start app: Firestore connection failed")
