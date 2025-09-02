from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
DB_PATH = "smart_tactic.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_form_data(data):
    """Validate incoming form data"""
    required_fields = ['category', 'tactic_type', 'event_kind']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def create_form_in_db(form_data):
    """Create a new form in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert main form
        cursor.execute('''
            INSERT INTO forms (category, tactic_type, event_kind, aligned_to_multi_event)
            VALUES (?, ?, ?, ?)
        ''', (
            form_data.get('category', ''),
            form_data.get('tactic_type', ''),
            form_data.get('event_kind', 'Single'),
            form_data.get('aligned_to_multi_event', False)
        ))
        
        form_id = cursor.lastrowid
        
        # Insert basic information if provided
        if 'basic' in form_data:
            basic = form_data['basic']
            cursor.execute('''
                INSERT INTO form_basic (form_id, event_name, description, priority, owner_email, 
                                      start_date, end_date, event_date_confidence, leads_expected, no_of_inquiries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_id,
                basic.get('event_name', ''),
                basic.get('description', ''),
                basic.get('priority', ''),
                basic.get('owner_email', ''),
                basic.get('start_date', ''),
                basic.get('end_date', ''),
                basic.get('event_date_confidence', ''),
                basic.get('leads_expected', False),
                basic.get('no_of_inquiries', 0)
            ))
        
        # Insert organization if provided
        if 'organization' in form_data:
            org = form_data['organization']
            cursor.execute('''
                INSERT INTO form_organization (form_id, ring, party, category, subcategory)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                form_id,
                org.get('ring', ''),
                org.get('party', ''),
                org.get('category', ''),
                org.get('subcategory', '')
            ))
        
        # Insert logistics if provided
        if 'logistics' in form_data:
            logistics = form_data['logistics']
            cursor.execute('''
                INSERT INTO form_logistics (form_id, funding_status, hosting_type, city)
                VALUES (?, ?, ?, ?)
            ''', (
                form_id,
                logistics.get('funding_status', ''),
                logistics.get('hosting_type', ''),
                logistics.get('city', '')
            ))
            
            # Insert countries if provided
            if 'countries' in logistics and logistics['countries']:
                for country in logistics['countries']:
                    cursor.execute('''
                        INSERT INTO form_countries (form_id, country)
                        VALUES (?, ?)
                    ''', (form_id, country))
        
        # Insert finance if provided
        if 'finance' in form_data:
            finance = form_data['finance']
            cursor.execute('''
                INSERT INTO form_finance (form_id, cloud_marketing_cost_center, has_spend, 
                                        total_budget, split_cost_center)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                form_id,
                finance.get('cloud_marketing_cost_center', ''),
                finance.get('has_spend', False),
                finance.get('total_budget', 0),
                finance.get('split_cost_center', False)
            ))
            
            # Insert cost center splits if provided
            if 'cost_center_split' in finance and finance['cost_center_split']:
                for split in finance['cost_center_split']:
                    if isinstance(split, dict):
                        cursor.execute('''
                            INSERT INTO form_cost_center_splits (form_id, cost_center, percentage)
                            VALUES (?, ?, ?)
                        ''', (
                            form_id,
                            split.get('cost_center', ''),
                            split.get('percentage', 0)
                        ))
        
        # Insert extras if provided
        if 'extras' in form_data:
            extras = form_data['extras']
            cursor.execute('''
                INSERT INTO form_extras (form_id, venue, registration_link, sales_kit_link)
                VALUES (?, ?, ?, ?)
            ''', (
                form_id,
                extras.get('venue', ''),
                extras.get('registration_link', ''),
                extras.get('sales_kit_link', '')
            ))
        
        # Insert partners if provided
        if 'partners' in form_data:
            partners = form_data['partners']
            cursor.execute('''
                INSERT INTO form_partners (form_id, partner_involved, partner_name, lead_followup)
                VALUES (?, ?, ?, ?)
            ''', (
                form_id,
                partners.get('partner_involved', 'No Partner Involvement'),
                partners.get('partner_name', ''),
                partners.get('lead_followup', '')
            ))
            
            # Insert partner responsibilities if provided
            if 'responsibilities' in partners and partners['responsibilities']:
                for resp in partners['responsibilities']:
                    cursor.execute('''
                        INSERT INTO form_partner_responsibilities (form_id, responsibility)
                        VALUES (?, ?)
                    ''', (form_id, resp))
        
        # Insert forecasts if provided
        if 'forecasts' in form_data:
            forecasts = form_data['forecasts']
            cursor.execute('''
                INSERT INTO form_forecasts (form_id, expected_registrations, expected_attendees)
                VALUES (?, ?, ?)
            ''', (
                form_id,
                forecasts.get('expected_registrations', 0),
                forecasts.get('expected_attendees', 0)
            ))
        
        # Insert campaign program if provided
        if 'campaign_program' in form_data:
            campaign = form_data['campaign_program']
            cursor.execute('''
                INSERT INTO form_campaign_program (form_id, tied_to_program, adopt_adapt_invent)
                VALUES (?, ?, ?)
            ''', (
                form_id,
                campaign.get('tied_to_program', False),
                campaign.get('adopt_adapt_invent', '')
            ))
            
            # Insert program splits if provided
            if 'program_splits' in campaign and campaign['program_splits']:
                for split in campaign['program_splits']:
                    if isinstance(split, dict):
                        cursor.execute('''
                            INSERT INTO form_program_splits (form_id, program, percentage)
                            VALUES (?, ?, ?)
                        ''', (
                            form_id,
                            split.get('program', ''),
                            split.get('percentage', 0)
                        ))
        
        # Insert alignments if provided
        if 'alignments' in form_data:
            alignments = form_data['alignments']
            
            # Insert account segments
            if 'account_segment' in alignments and alignments['account_segment']:
                for segment in alignments['account_segment']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, account_segment)
                        VALUES (?, ?)
                    ''', (form_id, segment))
            
            # Insert account segment types
            if 'account_segment_type' in alignments and alignments['account_segment_type']:
                for segment_type in alignments['account_segment_type']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, account_segment_type)
                        VALUES (?, ?)
                    ''', (form_id, segment_type))
            
            # Insert buyer segment rollups
            if 'buyer_segment_rollups' in alignments and alignments['buyer_segment_rollups']:
                for buyer in alignments['buyer_segment_rollups']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, buyer_segment_rollup)
                        VALUES (?, ?)
                    ''', (form_id, buyer))
            
            # Insert industries
            if 'industry' in alignments and alignments['industry']:
                for industry in alignments['industry']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, industry)
                        VALUES (?, ?)
                    ''', (form_id, industry))
            
            # Insert products
            if 'product' in alignments and alignments['product']:
                for product in alignments['product']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, product)
                        VALUES (?, ?)
                    ''', (form_id, product))
            
            # Insert customer lifecycle
            if 'customer_lifecycle' in alignments and alignments['customer_lifecycle']:
                for lifecycle in alignments['customer_lifecycle']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, customer_lifecycle)
                        VALUES (?, ?)
                    ''', (form_id, lifecycle))
            
            # Insert core messaging
            if 'core_messaging' in alignments and alignments['core_messaging']:
                for messaging in alignments['core_messaging']:
                    cursor.execute('''
                        INSERT INTO form_alignments (form_id, core_messaging)
                        VALUES (?, ?)
                    ''', (form_id, messaging))
        
        # Insert review if provided
        if 'review' in form_data:
            review = form_data['review']
            cursor.execute('''
                INSERT INTO form_review (form_id, status_basic, status_execution, ready_for_activation)
                VALUES (?, ?, ?, ?)
            ''', (
                form_id,
                review.get('status_basic', False),
                review.get('status_execution', False),
                review.get('ready_for_activation', False)
            ))
        
        conn.commit()
        conn.close()
        
        return form_id, None
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return None, str(e)

def get_form_details(form_id):
    """Get complete form details by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get main form data
        cursor.execute('SELECT * FROM forms WHERE id = ?', (form_id,))
        form = cursor.fetchone()
        
        if not form:
            conn.close()
            return None
        
        # Get basic information
        cursor.execute('SELECT * FROM form_basic WHERE form_id = ?', (form_id,))
        basic = cursor.fetchone()
        
        # Get organization
        cursor.execute('SELECT * FROM form_organization WHERE form_id = ?', (form_id,))
        organization = cursor.fetchone()
        
        # Get logistics
        cursor.execute('SELECT * FROM form_logistics WHERE form_id = ?', (form_id,))
        logistics = cursor.fetchone()
        
        # Get countries
        cursor.execute('SELECT country FROM form_countries WHERE form_id = ?', (form_id,))
        countries = [row['country'] for row in cursor.fetchall()]
        
        # Get finance
        cursor.execute('SELECT * FROM form_finance WHERE form_id = ?', (form_id,))
        finance = cursor.fetchone()
        
        # Get cost center splits
        cursor.execute('SELECT * FROM form_cost_center_splits WHERE form_id = ?', (form_id,))
        cost_center_splits = [dict(row) for row in cursor.fetchall()]
        
        # Get extras
        cursor.execute('SELECT * FROM form_extras WHERE form_id = ?', (form_id,))
        extras = cursor.fetchone()
        
        # Get partners
        cursor.execute('SELECT * FROM form_partners WHERE form_id = ?', (form_id,))
        partners = cursor.fetchone()
        
        # Get partner responsibilities
        cursor.execute('SELECT responsibility FROM form_partner_responsibilities WHERE form_id = ?', (form_id,))
        responsibilities = [row['responsibility'] for row in cursor.fetchall()]
        
        # Get forecasts
        cursor.execute('SELECT * FROM form_forecasts WHERE form_id = ?', (form_id,))
        forecasts = cursor.fetchone()
        
        # Get campaign program
        cursor.execute('SELECT * FROM form_campaign_program WHERE form_id = ?', (form_id,))
        campaign_program = cursor.fetchone()
        
        # Get program splits
        cursor.execute('SELECT * FROM form_program_splits WHERE form_id = ?', (form_id,))
        program_splits = [dict(row) for row in cursor.fetchall()]
        
        # Get alignments
        cursor.execute('SELECT * FROM form_alignments WHERE form_id = ?', (form_id,))
        alignments_rows = cursor.fetchall()
        
        # Group alignments by type
        alignments = {
            'account_segment': [],
            'account_segment_type': [],
            'buyer_segment_rollups': [],
            'industry': [],
            'product': [],
            'customer_lifecycle': [],
            'core_messaging': []
        }
        
        for row in alignments_rows:
            if row['account_segment']:
                alignments['account_segment'].append(row['account_segment'])
            if row['account_segment_type']:
                alignments['account_segment_type'].append(row['account_segment_type'])
            if row['buyer_segment_rollup']:
                alignments['buyer_segment_rollups'].append(row['buyer_segment_rollup'])
            if row['industry']:
                alignments['industry'].append(row['industry'])
            if row['product']:
                alignments['product'].append(row['product'])
            if row['customer_lifecycle']:
                alignments['customer_lifecycle'].append(row['customer_lifecycle'])
            if row['core_messaging']:
                alignments['core_messaging'].append(row['core_messaging'])
        
        # Get review
        cursor.execute('SELECT * FROM form_review WHERE form_id = ?', (form_id,))
        review = cursor.fetchone()
        
        conn.close()
        
        # Build response
        form_data = {
            'id': form['id'],
            'category': form['category'],
            'tactic_type': form['tactic_type'],
            'event_kind': form['event_kind'],
            'aligned_to_multi_event': bool(form['aligned_to_multi_event']),
            'created_at': form['created_at'],
            'updated_at': form['updated_at']
        }
        
        if basic:
            form_data['basic'] = dict(basic)
            form_data['basic'].pop('id', None)
            form_data['basic'].pop('form_id', None)
        
        if organization:
            form_data['organization'] = dict(organization)
            form_data['organization'].pop('id', None)
            form_data['organization'].pop('form_id', None)
        
        if logistics:
            logistics_dict = dict(logistics)
            logistics_dict.pop('id', None)
            logistics_dict.pop('form_id', None)
            logistics_dict['countries'] = countries
            form_data['logistics'] = logistics_dict
        
        if finance:
            finance_dict = dict(finance)
            finance_dict.pop('id', None)
            finance_dict.pop('form_id', None)
            finance_dict['cost_center_split'] = cost_center_splits
            form_data['finance'] = finance_dict
        
        if extras:
            form_data['extras'] = dict(extras)
            form_data['extras'].pop('id', None)
            form_data['extras'].pop('form_id', None)
        
        if partners:
            partners_dict = dict(partners)
            partners_dict.pop('id', None)
            partners_dict.pop('form_id', None)
            partners_dict['responsibilities'] = responsibilities
            form_data['partners'] = partners_dict
        
        if forecasts:
            form_data['forecasts'] = dict(forecasts)
            form_data['forecasts'].pop('id', None)
            form_data['forecasts'].pop('form_id', None)
        
        if campaign_program:
            campaign_dict = dict(campaign_program)
            campaign_dict.pop('id', None)
            campaign_dict.pop('form_id', None)
            campaign_dict['program_splits'] = program_splits
            form_data['campaign_program'] = campaign_dict
        
        form_data['alignments'] = alignments
        
        if review:
            form_data['review'] = dict(review)
            form_data['review'].pop('id', None)
            form_data['review'].pop('form_id', None)
        
        return form_data
        
    except Exception as e:
        if conn:
            conn.close()
        return None

def update_form_in_db(form_id, form_data):
    """Update an existing form in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if form exists
        cursor.execute('SELECT id FROM forms WHERE id = ?', (form_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Form not found"
        
        # Update main form
        if 'category' in form_data or 'tactic_type' in form_data or 'event_kind' in form_data:
            update_fields = []
            update_values = []
            
            if 'category' in form_data:
                update_fields.append('category = ?')
                update_values.append(form_data['category'])
            
            if 'tactic_type' in form_data:
                update_fields.append('tactic_type = ?')
                update_values.append(form_data['tactic_type'])
            
            if 'event_kind' in form_data:
                update_fields.append('event_kind = ?')
                update_values.append(form_data['event_kind'])
            
            if 'aligned_to_multi_event' in form_data:
                update_fields.append('aligned_to_multi_event = ?')
                update_values.append(form_data['aligned_to_multi_event'])
            
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(form_id)
            
            cursor.execute(f'''
                UPDATE forms SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)
        
        # Update other sections as needed
        # This is a simplified update - in a production system, you'd want more granular updates
        
        conn.commit()
        conn.close()
        
        return True, "Form updated successfully"
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def delete_form_from_db(form_id):
    """Delete a form from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if form exists
        cursor.execute('SELECT id FROM forms WHERE id = ?', (form_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Form not found"
        
        # Delete form (cascade will handle related tables)
        cursor.execute('DELETE FROM forms WHERE id = ?', (form_id,))
        
        conn.commit()
        conn.close()
        
        return True, "Form deleted successfully"
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

# API Endpoints

@app.route('/api/forms', methods=['POST'])
def create_form():
    """Create a new form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data
        is_valid, message = validate_form_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Create form in database
        form_id, error = create_form_in_db(data)
        
        if error:
            return jsonify({'error': f'Failed to create form: {error}'}), 500
        
        return jsonify({
            'message': 'Form created successfully',
            'form_id': form_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms/<int:form_id>', methods=['GET'])
def get_form(form_id):
    """Get form details by ID"""
    try:
        form_data = get_form_details(form_id)
        
        if not form_data:
            return jsonify({'error': 'Form not found'}), 404
        
        return jsonify(form_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms/<int:form_id>', methods=['PUT'])
def update_form(form_id):
    """Update an existing form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update form in database
        success, message = update_form_in_db(form_id, data)
        
        if not success:
            return jsonify({'error': message}), 404 if 'not found' in message.lower() else 500
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms/<int:form_id>', methods=['DELETE'])
def delete_form(form_id):
    """Delete a form"""
    try:
        # Delete form from database
        success, message = delete_form_from_db(form_id)
        
        if not success:
            return jsonify({'error': message}), 404 if 'not found' in message.lower() else 500
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms', methods=['GET'])
def list_forms():
    """List all forms (simplified)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.id, f.category, f.tactic_type, f.event_kind, 
                   fb.event_name, fb.owner_email, f.created_at
            FROM forms f
            LEFT JOIN form_basic fb ON f.id = fb.form_id
            ORDER BY f.created_at DESC
        ''')
        
        forms = []
        for row in cursor.fetchall():
            forms.append({
                'id': row['id'],
                'category': row['category'],
                'tactic_type': row['tactic_type'],
                'event_kind': row['event_kind'],
                'event_name': row['event_name'] or '',
                'owner_email': row['owner_email'] or '',
                'created_at': row['created_at']
            })
        
        conn.close()
        
        return jsonify({'forms': forms}), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Please run db_setup.py first.")
        exit(1)
    
    print("Starting SmartTactic API...")
    print("Available endpoints:")
    print("  POST   /api/forms          - Create a new form")
    print("  GET    /api/forms          - List all forms")
    print("  GET    /api/forms/<id>     - Get form details")
    print("  PUT    /api/forms/<id>     - Update form")
    print("  DELETE /api/forms/<id>     - Delete form")
    print("  GET    /health             - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
