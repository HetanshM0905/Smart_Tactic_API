import json
from datetime import datetime
import os
from tinydb import TinyDB, Query

class SmartTacticTinyDB:
    def __init__(self, db_path="smart_tactic_tinydb.json"):
        """
        Initialize TinyDB database connection
        
        Args:
            db_path: Path to the TinyDB JSON file
        """
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
            
            print(f"Connected to TinyDB: {db_path}")
            
        except Exception as e:
            print(f"Error connecting to TinyDB: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables in TinyDB"""
        try:
            # TinyDB tables are created automatically when first accessed
            # We'll create a test document in each table to ensure they exist
            for table_name, table in self.tables.items():
                # Create a test document that we'll delete immediately
                test_doc = {
                    'created_at': datetime.now().isoformat(),
                    'test': True
                }
                doc_id = table.insert(test_doc)
                table.remove(doc_ids=[doc_id])  # Delete the test document
                print(f"Table '{table_name}' verified/created")
            
            print("All tables created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample data from mockdata.json"""
        try:
            # Load mock data
            with open('mockdata.json', 'r') as f:
                mock_data = json.load(f)
            
            # Insert a sample form using the template structure
            template = mock_data['templates']['single_event_min']
            
            # Create main form document
            form_data = {
                'category': template['category'],
                'tactic_type': template['tactic_type'],
                'event_kind': template['event_kind'],
                'aligned_to_multi_event': template['aligned_to_multi_event'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Add to forms table
            form_id = self.tables['forms'].insert(form_data)
            print(f"Created form with ID: {form_id}")
            
            # Insert basic info
            if 'basic' in template:
                basic = template['basic']
                basic_data = {
                    'form_id': form_id,
                    'event_name': basic['event_name'],
                    'description': basic['description'],
                    'priority': basic['priority'],
                    'owner_email': basic['owner_email'],
                    'start_date': basic['start_date'],
                    'end_date': basic['end_date'],
                    'event_date_confidence': basic['event_date_confidence'],
                    'leads_expected': basic['leads_expected'],
                    'no_of_inquiries': basic['no_of_inquiries'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_basic'].insert(basic_data)
            
            # Insert organization
            if 'organization' in template:
                org = template['organization']
                org_data = {
                    'form_id': form_id,
                    'ring': org['ring'],
                    'party': org['party'],
                    'category': org['category'],
                    'subcategory': org['subcategory'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_organization'].insert(org_data)
            
            # Insert logistics
            if 'logistics' in template:
                logistics = template['logistics']
                logistics_data = {
                    'form_id': form_id,
                    'funding_status': logistics['funding_status'],
                    'hosting_type': logistics['hosting_type'],
                    'city': logistics['city'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_logistics'].insert(logistics_data)
                
                # Insert countries
                if 'countries' in logistics and logistics['countries']:
                    for country in logistics['countries']:
                        country_data = {
                            'form_id': form_id,
                            'country': country,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_countries'].insert(country_data)
            
            # Insert finance
            if 'finance' in template:
                finance = template['finance']
                finance_data = {
                    'form_id': form_id,
                    'cloud_marketing_cost_center': finance['cloud_marketing_cost_center'],
                    'has_spend': finance['has_spend'],
                    'total_budget': float(finance['total_budget']),
                    'split_cost_center': finance['split_cost_center'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_finance'].insert(finance_data)
                
                # Insert cost center splits
                if 'cost_center_split' in finance and finance['cost_center_split']:
                    for split in finance['cost_center_split']:
                        if isinstance(split, dict):
                            split_data = {
                                'form_id': form_id,
                                'cost_center': split.get('cost_center', ''),
                                'percentage': float(split.get('percentage', 0)),
                                'created_at': datetime.now().isoformat()
                            }
                            self.tables['form_cost_center_splits'].insert(split_data)
            
            # Insert extras
            if 'extras' in template:
                extras = template['extras']
                extras_data = {
                    'form_id': form_id,
                    'venue': extras['venue'],
                    'registration_link': extras['registration_link'],
                    'sales_kit_link': extras['sales_kit_link'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_extras'].insert(extras_data)
            
            # Insert partners
            if 'partners' in template:
                partners = template['partners']
                partners_data = {
                    'form_id': form_id,
                    'partner_involved': partners['partner_involved'],
                    'partner_name': partners['partner_name'],
                    'lead_followup': partners['lead_followup'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_partners'].insert(partners_data)
                
                # Insert partner responsibilities
                if 'responsibilities' in partners and partners['responsibilities']:
                    for resp in partners['responsibilities']:
                        resp_data = {
                            'form_id': form_id,
                            'responsibility': resp,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_partner_responsibilities'].insert(resp_data)
            
            # Insert forecasts
            if 'forecasts' in template:
                forecasts = template['forecasts']
                forecasts_data = {
                    'form_id': form_id,
                    'expected_registrations': forecasts['expected_registrations'],
                    'expected_attendees': forecasts['expected_attendees'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_forecasts'].insert(forecasts_data)
            
            # Insert campaign program
            if 'campaign_program' in template:
                campaign = template['campaign_program']
                campaign_data = {
                    'form_id': form_id,
                    'tied_to_program': campaign['tied_to_program'],
                    'adopt_adapt_invent': campaign['adopt_adapt_invent'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_campaign_program'].insert(campaign_data)
                
                # Insert program splits
                if 'program_splits' in campaign and campaign['program_splits']:
                    for split in campaign['program_splits']:
                        if isinstance(split, dict):
                            split_data = {
                                'form_id': form_id,
                                'program': split.get('program', ''),
                                'percentage': float(split.get('percentage', 0)),
                                'created_at': datetime.now().isoformat()
                            }
                            self.tables['form_program_splits'].insert(split_data)
            
            # Insert alignments
            if 'alignments' in template:
                alignments = template['alignments']
                
                # Account segments
                if 'account_segment' in alignments and alignments['account_segment']:
                    for segment in alignments['account_segment']:
                        segment_data = {
                            'form_id': form_id,
                            'account_segment': segment,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(segment_data)
                
                # Account segment types
                if 'account_segment_type' in alignments and alignments['account_segment_type']:
                    for segment_type in alignments['account_segment_type']:
                        segment_type_data = {
                            'form_id': form_id,
                            'account_segment_type': segment_type,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(segment_type_data)
                
                # Buyer segments
                if 'buyer_segment_rollups' in alignments and alignments['buyer_segment_rollups']:
                    for buyer in alignments['buyer_segment_rollups']:
                        buyer_data = {
                            'form_id': form_id,
                            'buyer_segment_rollup': buyer,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(buyer_data)
                
                # Industries
                if 'industry' in alignments and alignments['industry']:
                    for industry in alignments['industry']:
                        industry_data = {
                            'form_id': form_id,
                            'industry': industry,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(industry_data)
                
                # Products
                if 'product' in alignments and alignments['product']:
                    for product in alignments['product']:
                        product_data = {
                            'form_id': form_id,
                            'product': product,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(product_data)
                
                # Customer lifecycle
                if 'customer_lifecycle' in alignments and alignments['customer_lifecycle']:
                    for lifecycle in alignments['customer_lifecycle']:
                        lifecycle_data = {
                            'form_id': form_id,
                            'customer_lifecycle': lifecycle,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(lifecycle_data)
                
                # Core messaging
                if 'core_messaging' in alignments and alignments['core_messaging']:
                    for messaging in alignments['core_messaging']:
                        messaging_data = {
                            'form_id': form_id,
                            'core_messaging': messaging,
                            'created_at': datetime.now().isoformat()
                        }
                        self.tables['form_alignments'].insert(messaging_data)
            
            # Insert review
            if 'review' in template:
                review = template['review']
                review_data = {
                    'form_id': form_id,
                    'status_basic': review['status_basic'],
                    'status_execution': review['status_execution'],
                    'ready_for_activation': review['ready_for_activation'],
                    'created_at': datetime.now().isoformat()
                }
                self.tables['form_review'].insert(review_data)
            
            print(f"Sample data inserted successfully! Form ID: {form_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting sample data: {e}")
            return False
    
    def show_tables(self):
        """Show all tables in the database"""
        try:
            print("\nTables in TinyDB database:")
            for table_name in self.tables.keys():
                count = len(self.tables[table_name])
                print(f"- {table_name} ({count} documents)")
            return list(self.tables.keys())
        except Exception as e:
            print(f"Error showing tables: {e}")
            return []
    
    def get_form_by_id(self, form_id):
        """Get a complete form by ID"""
        try:
            # Get main form
            form_docs = self.tables['forms'].search(Query().doc_id == form_id)
            if not form_docs:
                return None
            
            form_data = form_docs[0]
            form_data['id'] = form_id
            
            # Get all related data
            collections_to_fetch = [
                'form_basic', 'form_organization', 'form_logistics', 
                'form_finance', 'form_extras', 'form_partners', 
                'form_forecasts', 'form_campaign_program', 'form_review'
            ]
            
            for collection_name in collections_to_fetch:
                docs = self.tables[collection_name].search(Query().form_id == form_id)
                form_data[collection_name] = docs
            
            # Get arrays (countries, cost center splits, etc.)
            countries = self.tables['form_countries'].search(Query().form_id == form_id)
            form_data['countries'] = [doc['country'] for doc in countries]
            
            cost_splits = self.tables['form_cost_center_splits'].search(Query().form_id == form_id)
            form_data['cost_center_splits'] = cost_splits
            
            partner_resps = self.tables['form_partner_responsibilities'].search(Query().form_id == form_id)
            form_data['partner_responsibilities'] = [doc['responsibility'] for doc in partner_resps]
            
            program_splits = self.tables['form_program_splits'].search(Query().form_id == form_id)
            form_data['program_splits'] = program_splits
            
            return form_data
            
        except Exception as e:
            print(f"Error getting form by ID: {e}")
            return None
    
    def get_all_forms(self):
        """Get all forms"""
        try:
            forms = self.tables['forms'].all()
            for form in forms:
                form['id'] = form.doc_id
            return forms
        except Exception as e:
            print(f"Error getting all forms: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
            print("TinyDB connection closed")

def main():
    """Main function to set up the TinyDB database"""
    try:
        db = SmartTacticTinyDB()
        print("Setting up SmartTactic TinyDB database...")
        
        # Create tables
        if db.create_tables():
            print("Tables created successfully!")
            
            # Show tables
            db.show_tables()
            
            # Insert sample data
            print("\nInserting sample data...")
            db.insert_sample_data()
            
        else:
            print("Failed to create tables!")
        
        db.close()
    
    except Exception as e:
        print(f"Failed to initialize TinyDB database: {e}")
    
    print("\nTinyDB database setup completed!")

if __name__ == "__main__":
    main()
