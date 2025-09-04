import os
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreConfig:
    """Configuration class for Firestore database"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.database_id = os.getenv('FIRESTORE_DATABASE_ID', '(default)')
        
    def get_client(self):
        """Get Firestore client with appropriate configuration"""
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account credentials from file
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                client = firestore.Client(
                    project=self.project_id,
                    credentials=credentials,
                    database=self.database_id
                )
                print(f"Connected to Firestore using service account: {self.credentials_path}")
            else:
                # Use default credentials (for local development or GCP environment)
                client = firestore.Client(
                    project=self.project_id,
                    database=self.database_id
                )
                print("Connected to Firestore using default credentials")
            
            return client
            
        except Exception as e:
            print(f"Error creating Firestore client: {e}")
            raise
    
    def get_collections(self, client):
        """Get collection references"""
        return {
            'forms': client.collection('forms'),
            'form_basic': client.collection('form_basic'),
            'form_organization': client.collection('form_organization'),
            'form_logistics': client.collection('form_logistics'),
            'form_countries': client.collection('form_countries'),
            'form_finance': client.collection('form_finance'),
            'form_cost_center_splits': client.collection('form_cost_center_splits'),
            'form_extras': client.collection('form_extras'),
            'form_partners': client.collection('form_partners'),
            'form_partner_responsibilities': client.collection('form_partner_responsibilities'),
            'form_forecasts': client.collection('form_forecasts'),
            'form_campaign_program': client.collection('form_campaign_program'),
            'form_program_splits': client.collection('form_program_splits'),
            'form_alignments': client.collection('form_alignments'),
            'form_review': client.collection('form_review')
        }

# Environment variables that should be set:
# GOOGLE_CLOUD_PROJECT_ID=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
# FIRESTORE_DATABASE_ID=your-database-id (optional, defaults to '(default)')

def setup_environment():
    """Setup environment variables for Firestore"""
    print("Firestore Environment Setup:")
    print(f"Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'Not set')}")
    print(f"Credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'Using default')}")
    print(f"Database ID: {os.getenv('FIRESTORE_DATABASE_ID', '(default)')}")
    
    if not os.getenv('GOOGLE_CLOUD_PROJECT_ID'):
        print("\nWARNING: GOOGLE_CLOUD_PROJECT_ID not set!")
        print("Please set this environment variable to your Google Cloud project ID")
    
    print("\nTo set environment variables:")
    print("Windows (PowerShell):")
    print("  $env:GOOGLE_CLOUD_PROJECT_ID='your-project-id'")
    print("  $env:GOOGLE_APPLICATION_CREDENTIALS='path/to/key.json'")
    print("\nLinux/Mac:")
    print("  export GOOGLE_CLOUD_PROJECT_ID='your-project-id'")
    print("  export GOOGLE_APPLICATION_CREDENTIALS='path/to/key.json'")

if __name__ == "__main__":
    setup_environment()
