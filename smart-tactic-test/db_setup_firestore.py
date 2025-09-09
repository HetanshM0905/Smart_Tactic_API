import json
from datetime import datetime
import os
from google.cloud import firestore
from google.oauth2 import service_account

class SmartTacticFirestoreDB:
    def __init__(self, credentials_path=None):
        """
        Initialize Firestore database connection
        
        Args:
            credentials_path: Path to Google Cloud service account JSON file
                            If None, will use default credentials
        """
        try:
            if credentials_path and os.path.exists(credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.db = firestore.Client(credentials=credentials)
                print(f"Connected to Firestore using service account: {credentials_path}")
            else:
                # Use default credentials (for local development or GCP environment)
                self.db = firestore.Client()
                print("Connected to Firestore using default credentials")
            
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
    
    def create_collections(self):
        """Create all necessary collections in Firestore"""
        try:
            # Firestore collections are created automatically when documents are added
            # We'll create a test document in each collection to ensure they exist
            for collection_name, collection_ref in self.collections.items():
                # Create a test document that we'll delete immediately
                test_doc = collection_ref.document('_test')
                test_doc.set({'created_at': datetime.now(), 'test': True})
                test_doc.delete()  # Delete the test document
                print(f"Collection '{collection_name}' verified/created")
            
            print("All collections created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating collections: {e}")
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
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Add to forms collection
            form_ref = self.collections['forms'].add(form_data)[1]
            form_id = form_ref.id
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
                    'created_at': datetime.now()
                }
                self.collections['form_basic'].add(basic_data)
            
            # Insert organization
            if 'organization' in template:
                org = template['organization']
                org_data = {
                    'form_id': form_id,
                    'ring': org['ring'],
                    'party': org['party'],
                    'category': org['category'],
                    'subcategory': org['subcategory'],
                    'created_at': datetime.now()
                }
                self.collections['form_organization'].add(org_data)
            
            # Insert logistics
            if 'logistics' in template:
                logistics = template['logistics']
                logistics_data = {
                    'form_id': form_id,
                    'funding_status': logistics['funding_status'],
                    'hosting_type': logistics['hosting_type'],
                    'city': logistics['city'],
                    'created_at': datetime.now()
                }
                self.collections['form_logistics'].add(logistics_data)
                
                # Insert countries
                if 'countries' in logistics and logistics['countries']:
                    for country in logistics['countries']:
                        country_data = {
                            'form_id': form_id,
                            'country': country,
                            'created_at': datetime.now()
                        }
                        self.collections['form_countries'].add(country_data)
            
            # Insert finance
            if 'finance' in template:
                finance = template['finance']
                finance_data = {
                    'form_id': form_id,
                    'cloud_marketing_cost_center': finance['cloud_marketing_cost_center'],
                    'has_spend': finance['has_spend'],
                    'total_budget': float(finance['total_budget']),
                    'split_cost_center': finance['split_cost_center'],
                    'created_at': datetime.now()
                }
                self.collections['form_finance'].add(finance_data)
                
                # Insert cost center splits
                if 'cost_center_split' in finance and finance['cost_center_split']:
                    for split in finance['cost_center_split']:
                        if isinstance(split, dict):
                            split_data = {
                                'form_id': form_id,
                                'cost_center': split.get('cost_center', ''),
                                'percentage': float(split.get('percentage', 0)),
                                'created_at': datetime.now()
                            }
                            self.collections['form_cost_center_splits'].add(split_data)
            
            # Insert extras
            if 'extras' in template:
                extras = template['extras']
                extras_data = {
                    'form_id': form_id,
                    'venue': extras['venue'],
                    'registration_link': extras['registration_link'],
                    'sales_kit_link': extras['sales_kit_link'],
                    'created_at': datetime.now()
                }
                self.collections['form_extras'].add(extras_data)
            
            # Insert partners
            if 'partners' in template:
                partners = template['partners']
                partners_data = {
                    'form_id': form_id,
                    'partner_involved': partners['partner_involved'],
                    'partner_name': partners['partner_name'],
                    'lead_followup': partners['lead_followup'],
                    'created_at': datetime.now()
                }
                self.collections['form_partners'].add(partners_data)
                
                # Insert partner responsibilities
                if 'responsibilities' in partners and partners['responsibilities']:
                    for resp in partners['responsibilities']:
                        resp_data = {
                            'form_id': form_id,
                            'responsibility': resp,
                            'created_at': datetime.now()
                        }
                        self.collections['form_partner_responsibilities'].add(resp_data)
            
            # Insert forecasts
            if 'forecasts' in template:
                forecasts = template['forecasts']
                forecasts_data = {
                    'form_id': form_id,
                    'expected_registrations': forecasts['expected_registrations'],
                    'expected_attendees': forecasts['expected_attendees'],
                    'created_at': datetime.now()
                }
                self.collections['form_forecasts'].add(forecasts_data)
            
            # Insert campaign program
            if 'campaign_program' in template:
                campaign = template['campaign_program']
                campaign_data = {
                    'form_id': form_id,
                    'tied_to_program': campaign['tied_to_program'],
                    'adopt_adapt_invent': campaign['adopt_adapt_invent'],
                    'created_at': datetime.now()
                }
                self.collections['form_campaign_program'].add(campaign_data)
                
                # Insert program splits
                if 'program_splits' in campaign and campaign['program_splits']:
                    for split in campaign['program_splits']:
                        if isinstance(split, dict):
                            split_data = {
                                'form_id': form_id,
                                'program': split.get('program', ''),
                                'percentage': float(split.get('percentage', 0)),
                                'created_at': datetime.now()
                            }
                            self.collections['form_program_splits'].add(split_data)
            
            # Insert alignments
            if 'alignments' in template:
                alignments = template['alignments']
                
                # Account segments
                if 'account_segment' in alignments and alignments['account_segment']:
                    for segment in alignments['account_segment']:
                        segment_data = {
                            'form_id': form_id,
                            'account_segment': segment,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(segment_data)
                
                # Account segment types
                if 'account_segment_type' in alignments and alignments['account_segment_type']:
                    for segment_type in alignments['account_segment_type']:
                        segment_type_data = {
                            'form_id': form_id,
                            'account_segment_type': segment_type,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(segment_type_data)
                
                # Buyer segments
                if 'buyer_segment_rollups' in alignments and alignments['buyer_segment_rollups']:
                    for buyer in alignments['buyer_segment_rollups']:
                        buyer_data = {
                            'form_id': form_id,
                            'buyer_segment_rollup': buyer,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(buyer_data)
                
                # Industries
                if 'industry' in alignments and alignments['industry']:
                    for industry in alignments['industry']:
                        industry_data = {
                            'form_id': form_id,
                            'industry': industry,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(industry_data)
                
                # Products
                if 'product' in alignments and alignments['product']:
                    for product in alignments['product']:
                        product_data = {
                            'form_id': form_id,
                            'product': product,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(product_data)
                
                # Customer lifecycle
                if 'customer_lifecycle' in alignments and alignments['customer_lifecycle']:
                    for lifecycle in alignments['customer_lifecycle']:
                        lifecycle_data = {
                            'form_id': form_id,
                            'customer_lifecycle': lifecycle,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(lifecycle_data)
                
                # Core messaging
                if 'core_messaging' in alignments and alignments['core_messaging']:
                    for messaging in alignments['core_messaging']:
                        messaging_data = {
                            'form_id': form_id,
                            'core_messaging': messaging,
                            'created_at': datetime.now()
                        }
                        self.collections['form_alignments'].add(messaging_data)
            
            # Insert review
            if 'review' in template:
                review = template['review']
                review_data = {
                    'form_id': form_id,
                    'status_basic': review['status_basic'],
                    'status_execution': review['status_execution'],
                    'ready_for_activation': review['ready_for_activation'],
                    'created_at': datetime.now()
                }
                self.collections['form_review'].add(review_data)
            
            print(f"Sample data inserted successfully! Form ID: {form_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting sample data: {e}")
            return False
    
    def show_collections(self):
        """Show all collections in the database"""
        try:
            print("\nCollections in Firestore database:")
            for collection_name in self.collections.keys():
                print(f"- {collection_name}")
            return list(self.collections.keys())
        except Exception as e:
            print(f"Error showing collections: {e}")
            return []
    
    def get_form_by_id(self, form_id):
        """Get a complete form by ID"""
        try:
            # Get main form
            form_doc = self.collections['forms'].document(form_id).get()
            if not form_doc.exists:
                return None
            
            form_data = form_doc.to_dict()
            form_data['id'] = form_id
            
            # Get all related data
            collections_to_fetch = [
                'form_basic', 'form_organization', 'form_logistics', 
                'form_finance', 'form_extras', 'form_partners', 
                'form_forecasts', 'form_campaign_program', 'form_review'
            ]
            
            for collection_name in collections_to_fetch:
                docs = self.collections[collection_name].where('form_id', '==', form_id).stream()
                form_data[collection_name] = [doc.to_dict() for doc in docs]
            
            # Get arrays (countries, cost center splits, etc.)
            countries = self.collections['form_countries'].where('form_id', '==', form_id).stream()
            form_data['countries'] = [doc.to_dict()['country'] for doc in countries]
            
            cost_splits = self.collections['form_cost_center_splits'].where('form_id', '==', form_id).stream()
            form_data['cost_center_splits'] = [doc.to_dict() for doc in cost_splits]
            
            partner_resps = self.collections['form_partner_responsibilities'].where('form_id', '==', form_id).stream()
            form_data['partner_responsibilities'] = [doc.to_dict()['responsibility'] for doc in partner_resps]
            
            program_splits = self.collections['form_program_splits'].where('form_id', '==', form_id).stream()
            form_data['program_splits'] = [doc.to_dict() for doc in program_splits]
            
            return form_data
            
        except Exception as e:
            print(f"Error getting form by ID: {e}")
            return None

def main():
    """Main function to set up the Firestore database"""
    # You can specify a path to your service account JSON file here
    # credentials_path = "path/to/your/service-account-key.json"
    credentials_path = None  # Will use default credentials
    
    try:
        db = SmartTacticFirestoreDB(credentials_path)
        print("Setting up SmartTactic Firestore database...")
        
        # Create collections
        if db.create_collections():
            print("Collections created successfully!")
            
            # Show collections
            db.show_collections()
            
            # Insert sample data
            print("\nInserting sample data...")
            db.insert_sample_data()
            
        else:
            print("Failed to create collections!")
    
    except Exception as e:
        print(f"Failed to initialize Firestore database: {e}")
        print("\nMake sure you have:")
        print("1. Google Cloud project set up")
        print("2. Firestore database created")
        print("3. Service account credentials configured")
        print("4. Or running in a GCP environment with default credentials")
    
    print("\nFirestore database setup completed!")

if __name__ == "__main__":
    main()
