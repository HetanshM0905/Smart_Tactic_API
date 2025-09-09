from flask import Flask, request, jsonify
import json
from datetime import datetime
import os
from tinydb import TinyDB, Query

app = Flask(__name__)

# TinyDB database configuration
class TinyDBManager:
    def __init__(self, db_path="smart_tactic_tinydb.json"):
        """Initialize TinyDB connection"""
        try:
            self.db = TinyDB(db_path)
            self.db_path = db_path
            
            # Initialize tables (collections in TinyDB)
            self.tables = {
                'forms': self.db.table('forms'),
                'form_basic': self.db.table('form_basic'),
                'form_organization': self.db.table('form_organization'),
                'form_logistics': self.db.table('form_logistics'),
                'form_countries': self.db.table('form_countries'),
                'form_finance': self.db.table('form_finance'),
                'form_cost_center_splits': self.db.table('form_cost_center_splits'),
                'form_extras': self.db.table('form_extras'),
                'form_partners': self.db.table('form_partners'),
                'form_partner_responsibilities': self.db.table('form_partner_responsibilities'),
                'form_forecasts': self.db.table('form_forecasts'),
                'form_campaign_program': self.db.table('form_campaign_program'),
                'form_program_splits': self.db.table('form_program_splits'),
                'form_alignments': self.db.table('form_alignments'),
                'form_review': self.db.table('form_review')
            }
            
        except Exception as e:
            print(f"Error connecting to TinyDB: {e}")
            raise

# Initialize database
try:
    db = TinyDBManager()
    print("Connected to TinyDB successfully!")
except Exception as e:
    print(f"Failed to connect to TinyDB: {e}")
    db = None

def validate_form_data(data):
    """Validate incoming form data"""
    required_fields = ['category', 'tactic_type', 'event_kind']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def create_form_in_tinydb(form_data):
    """Create a new form in TinyDB"""
    try:
        if not db:
            return False, "Database connection not available"
        
        # Create main form document
        main_form_data = {
            'category': form_data.get('category', ''),
            'tactic_type': form_data.get('tactic_type', ''),
            'event_kind': form_data.get('event_kind', 'Single'),
            'aligned_to_multi_event': form_data.get('aligned_to_multi_event', False),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to forms table
        form_id = db.tables['forms'].insert(main_form_data)
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
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_basic'].insert(basic_data)
        
        # Insert organization if provided
        if 'organization' in form_data:
            org = form_data['organization']
            org_data = {
                'form_id': form_id,
                'ring': org.get('ring', ''),
                'party': org.get('party', ''),
                'category': org.get('category', ''),
                'subcategory': org.get('subcategory', ''),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_organization'].insert(org_data)
        
        # Insert logistics if provided
        if 'logistics' in form_data:
            logistics = form_data['logistics']
            logistics_data = {
                'form_id': form_id,
                'funding_status': logistics.get('funding_status', ''),
                'hosting_type': logistics.get('hosting_type', ''),
                'city': logistics.get('city', ''),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_logistics'].insert(logistics_data)
            
            # Insert countries if provided
            if 'countries' in logistics and logistics['countries']:
                for country in logistics['countries']:
                    country_data = {
                        'form_id': form_id,
                        'country': country,
                        'created_at': datetime.now().isoformat()
                    }
                    db.tables['form_countries'].insert(country_data)
        
        # Insert finance if provided
        if 'finance' in form_data:
            finance = form_data['finance']
            finance_data = {
                'form_id': form_id,
                'cloud_marketing_cost_center': finance.get('cloud_marketing_cost_center', ''),
                'has_spend': finance.get('has_spend', False),
                'total_budget': float(finance.get('total_budget', 0)),
                'split_cost_center': finance.get('split_cost_center', False),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_finance'].insert(finance_data)
            
            # Insert cost center splits if provided
            if 'cost_center_split' in finance and finance['cost_center_split']:
                for split in finance['cost_center_split']:
                    if isinstance(split, dict):
                        split_data = {
                            'form_id': form_id,
                            'cost_center': split.get('cost_center', ''),
                            'percentage': float(split.get('percentage', 0)),
                            'created_at': datetime.now().isoformat()
                        }
                        db.tables['form_cost_center_splits'].insert(split_data)
        
        # Insert extras if provided
        if 'extras' in form_data:
            extras = form_data['extras']
            extras_data = {
                'form_id': form_id,
                'venue': extras.get('venue', ''),
                'registration_link': extras.get('registration_link', ''),
                'sales_kit_link': extras.get('sales_kit_link', ''),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_extras'].insert(extras_data)
        
        # Insert partners if provided
        if 'partners' in form_data:
            partners = form_data['partners']
            partners_data = {
                'form_id': form_id,
                'partner_involved': partners.get('partner_involved', 'No Partner Involvement'),
                'partner_name': partners.get('partner_name', ''),
                'lead_followup': partners.get('lead_followup', ''),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_partners'].insert(partners_data)
            
            # Insert partner responsibilities if provided
            if 'responsibilities' in partners and partners['responsibilities']:
                for resp in partners['responsibilities']:
                    resp_data = {
                        'form_id': form_id,
                        'responsibility': resp,
                        'created_at': datetime.now().isoformat()
                    }
                    db.tables['form_partner_responsibilities'].insert(resp_data)
        
        # Insert forecasts if provided
        if 'forecasts' in form_data:
            forecasts = form_data['forecasts']
            forecasts_data = {
                'form_id': form_id,
                'expected_registrations': forecasts.get('expected_registrations', 0),
                'expected_attendees': forecasts.get('expected_attendees', 0),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_forecasts'].insert(forecasts_data)
        
        # Insert campaign program if provided
        if 'campaign_program' in form_data:
            campaign = form_data['campaign_program']
            campaign_data = {
                'form_id': form_id,
                'tied_to_program': campaign.get('tied_to_program', False),
                'adopt_adapt_invent': campaign.get('adopt_adapt_invent', ''),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_campaign_program'].insert(campaign_data)
            
            # Insert program splits if provided
            if 'program_splits' in campaign and campaign['program_splits']:
                for split in campaign['program_splits']:
                    if isinstance(split, dict):
                        split_data = {
                            'form_id': form_id,
                            'program': split.get('program', ''),
                            'percentage': float(split.get('percentage', 0)),
                            'created_at': datetime.now().isoformat()
                        }
                        db.tables['form_program_splits'].insert(split_data)
        
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
                            'created_at': datetime.now().isoformat()
                        }
                        db.tables['form_alignments'].insert(alignment_data)
        
        # Insert review if provided
        if 'review' in form_data:
            review = form_data['review']
            review_data = {
                'form_id': form_id,
                'status_basic': review.get('status_basic', False),
                'status_execution': review.get('status_execution', False),
                'ready_for_activation': review.get('ready_for_activation', False),
                'created_at': datetime.now().isoformat()
            }
            db.tables['form_review'].insert(review_data)
        
        return True, form_id
        
    except Exception as e:
        print(f"Error creating form in TinyDB: {e}")
        return False, str(e)

def get_form_from_tinydb(form_id):
    """Get a complete form from TinyDB by ID"""
    try:
        if not db:
            return None, "Database connection not available"
        
        # Get main form
        form_doc = db.tables['forms'].get(doc_id=form_id)
        if not form_doc:
            return None, "Form not found"
        
        form_data = form_doc
        form_data['id'] = form_id
        
        # Get all related data
        collections_to_fetch = [
            'form_basic', 'form_organization', 'form_logistics', 
            'form_finance', 'form_extras', 'form_partners', 
            'form_forecasts', 'form_campaign_program', 'form_review'
        ]
        
        for collection_name in collections_to_fetch:
            docs = db.tables[collection_name].search(Query().form_id == form_id)
            form_data[collection_name] = docs
        
        # Get arrays (countries, cost center splits, etc.)
        countries = db.tables['form_countries'].search(Query().form_id == form_id)
        form_data['countries'] = [doc['country'] for doc in countries]
        
        cost_splits = db.tables['form_cost_center_splits'].search(Query().form_id == form_id)
        form_data['cost_center_splits'] = cost_splits
        
        partner_resps = db.tables['form_partner_responsibilities'].search(Query().form_id == form_id)
        form_data['partner_responsibilities'] = [doc['responsibility'] for doc in partner_resps]
        
        program_splits = db.tables['form_program_splits'].search(Query().form_id == form_id)
        form_data['program_splits'] = program_splits
        
        return form_data, None
        
    except Exception as e:
        print(f"Error getting form from TinyDB: {e}")
        return None, str(e)

def get_all_forms_from_tinydb():
    """Get all forms from TinyDB"""
    try:
        if not db:
            return [], "Database connection not available"
        
        forms = db.tables['forms'].all()
        for form in forms:
            form['id'] = form.doc_id
        
        return forms, None
        
    except Exception as e:
        print(f"Error getting all forms from TinyDB: {e}")
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
        
        # Create form in TinyDB
        success, result = create_form_in_tinydb(data)
        
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
        form_data, error = get_form_from_tinydb(int(form_id))
        
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
        forms, error = get_all_forms_from_tinydb()
        
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
        existing_form, error = get_form_from_tinydb(int(form_id))
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
            
            update_data['updated_at'] = datetime.now().isoformat()
            
            db.tables['forms'].update(update_data, Query().doc_id == int(form_id))
        
        return jsonify({'message': 'Form updated successfully'}), 200
        
    except Exception as e:
        print(f"Error in update_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['DELETE'])
def delete_form(form_id):
    """Delete a form"""
    try:
        # Check if form exists
        existing_form, error = get_form_from_tinydb(int(form_id))
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
            db.tables[collection_name].remove(Query().form_id == int(form_id))
        
        # Delete main form
        db.tables['forms'].remove(Query().doc_id == int(form_id))
        
        return jsonify({'message': 'Form deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error in delete_form: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if db:
            return jsonify({'status': 'healthy', 'database': 'connected', 'type': 'TinyDB'}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    if db:
        print("Starting Flask app with TinyDB...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Cannot start app: TinyDB connection failed")
