import sqlite3
import json
from datetime import datetime
import os

class SmartTacticDB:
    def __init__(self, db_path="smart_tactic.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def create_tables(self):
        """Create all necessary tables for SmartTactic forms"""
        try:
            # Main forms table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS forms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    tactic_type TEXT NOT NULL,
                    event_kind TEXT NOT NULL,
                    aligned_to_multi_event BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Basic information table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_basic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    event_name TEXT NOT NULL,
                    description TEXT,
                    priority TEXT,
                    owner_email TEXT NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    event_date_confidence TEXT,
                    leads_expected BOOLEAN DEFAULT FALSE,
                    no_of_inquiries INTEGER DEFAULT 0,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Organization table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_organization (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    ring TEXT,
                    party TEXT,
                    category TEXT,
                    subcategory TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Logistics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_logistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    funding_status TEXT,
                    hosting_type TEXT,
                    city TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Countries table (many-to-many relationship)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_countries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    country TEXT NOT NULL,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Finance table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_finance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    cloud_marketing_cost_center TEXT,
                    has_spend BOOLEAN DEFAULT FALSE,
                    total_budget DECIMAL(15,2) DEFAULT 0,
                    split_cost_center BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Cost center splits table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_cost_center_splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    cost_center TEXT NOT NULL,
                    percentage DECIMAL(5,2) NOT NULL,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Extras table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_extras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    venue TEXT,
                    registration_link TEXT,
                    sales_kit_link TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Partners table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_partners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    partner_involved TEXT DEFAULT 'No Partner Involvement',
                    partner_name TEXT,
                    lead_followup TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Partner responsibilities table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_partner_responsibilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    responsibility TEXT NOT NULL,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Forecasts table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    expected_registrations INTEGER DEFAULT 0,
                    expected_attendees INTEGER DEFAULT 0,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Campaign program table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_campaign_program (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    tied_to_program BOOLEAN DEFAULT FALSE,
                    adopt_adapt_invent TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Program splits table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_program_splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    program TEXT NOT NULL,
                    percentage DECIMAL(5,2) NOT NULL,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Alignments table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_alignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    account_segment TEXT,
                    account_segment_type TEXT,
                    buyer_segment_rollup TEXT,
                    industry TEXT,
                    product TEXT,
                    customer_lifecycle TEXT,
                    core_messaging TEXT,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Review table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_review (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    status_basic BOOLEAN DEFAULT FALSE,
                    status_execution BOOLEAN DEFAULT FALSE,
                    ready_for_activation BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_forms_category ON forms(category)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_forms_owner ON form_basic(owner_email)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_forms_dates ON form_basic(start_date, end_date)')
            
            self.conn.commit()
            print("All tables created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_sample_data(self):
        """Insert sample data from mockdata.json"""
        try:
            # Load mock data
            with open('mockdata.json', 'r') as f:
                mock_data = json.load(f)
            
            # Insert a sample form using the template structure
            template = mock_data['templates']['single_event_min']
            
            # Insert main form
            self.cursor.execute('''
                INSERT INTO forms (category, tactic_type, event_kind, aligned_to_multi_event)
                VALUES (?, ?, ?, ?)
            ''', (template['category'], template['tactic_type'], template['event_kind'], template['aligned_to_multi_event']))
            
            form_id = self.cursor.lastrowid
            
            # Insert basic info
            basic = template['basic']
            self.cursor.execute('''
                INSERT INTO form_basic (form_id, event_name, description, priority, owner_email, 
                                      start_date, end_date, event_date_confidence, leads_expected, no_of_inquiries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (form_id, basic['event_name'], basic['description'], basic['priority'], 
                  basic['owner_email'], basic['start_date'], basic['end_date'], 
                  basic['event_date_confidence'], basic['leads_expected'], basic['no_of_inquiries']))
            
            # Insert organization
            org = template['organization']
            self.cursor.execute('''
                INSERT INTO form_organization (form_id, ring, party, category, subcategory)
                VALUES (?, ?, ?, ?, ?)
            ''', (form_id, org['ring'], org['party'], org['category'], org['subcategory']))
            
            # Insert logistics
            logistics = template['logistics']
            self.cursor.execute('''
                INSERT INTO form_logistics (form_id, funding_status, hosting_type, city)
                VALUES (?, ?, ?, ?)
            ''', (form_id, logistics['funding_status'], logistics['hosting_type'], logistics['city']))
            
            # Insert countries
            for country in logistics['countries']:
                self.cursor.execute('''
                    INSERT INTO form_countries (form_id, country)
                    VALUES (?, ?)
                ''', (form_id, country))
            
            # Insert finance
            finance = template['finance']
            self.cursor.execute('''
                INSERT INTO form_finance (form_id, cloud_marketing_cost_center, has_spend, 
                                        total_budget, split_cost_center)
                VALUES (?, ?, ?, ?, ?)
            ''', (form_id, finance['cloud_marketing_cost_center'], finance['has_spend'], 
                  finance['total_budget'], finance['split_cost_center']))
            
            # Insert cost center splits
            for split in finance['cost_center_split']:
                # Assuming split is a dict with cost_center and percentage
                if isinstance(split, dict):
                    self.cursor.execute('''
                        INSERT INTO form_cost_center_splits (form_id, cost_center, percentage)
                        VALUES (?, ?, ?)
                    ''', (form_id, split.get('cost_center', ''), split.get('percentage', 0)))
            
            # Insert extras
            extras = template['extras']
            self.cursor.execute('''
                INSERT INTO form_extras (form_id, venue, registration_link, sales_kit_link)
                VALUES (?, ?, ?, ?)
            ''', (form_id, extras['venue'], extras['registration_link'], extras['sales_kit_link']))
            
            # Insert partners
            partners = template['partners']
            self.cursor.execute('''
                INSERT INTO form_partners (form_id, partner_involved, partner_name, lead_followup)
                VALUES (?, ?, ?, ?)
            ''', (form_id, partners['partner_involved'], partners['partner_name'], partners['lead_followup']))
            
            # Insert partner responsibilities
            for resp in partners['responsibilities']:
                self.cursor.execute('''
                    INSERT INTO form_partner_responsibilities (form_id, responsibility)
                    VALUES (?, ?)
                ''', (form_id, resp))
            
            # Insert forecasts
            forecasts = template['forecasts']
            self.cursor.execute('''
                INSERT INTO form_forecasts (form_id, expected_registrations, expected_attendees)
                VALUES (?, ?, ?)
            ''', (form_id, forecasts['expected_registrations'], forecasts['expected_attendees']))
            
            # Insert campaign program
            campaign = template['campaign_program']
            self.cursor.execute('''
                INSERT INTO form_campaign_program (form_id, tied_to_program, adopt_adapt_invent)
                VALUES (?, ?, ?)
            ''', (form_id, campaign['tied_to_program'], campaign['adopt_adapt_invent']))
            
            # Insert program splits
            for split in campaign['program_splits']:
                # Assuming split is a dict with program and percentage
                if isinstance(split, dict):
                    self.cursor.execute('''
                        INSERT INTO form_program_splits (form_id, program, percentage)
                        VALUES (?, ?, ?)
                    ''', (form_id, split.get('program', ''), split.get('percentage', 0)))
            
            # Insert alignments
            alignments = template['alignments']
            for segment in alignments['account_segment']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, account_segment)
                    VALUES (?, ?)
                ''', (form_id, segment))
            
            for segment_type in alignments['account_segment_type']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, account_segment_type)
                    VALUES (?, ?)
                ''', (form_id, segment_type))
            
            for buyer in alignments['buyer_segment_rollups']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, buyer_segment_rollup)
                    VALUES (?, ?)
                ''', (form_id, buyer))
            
            for industry in alignments['industry']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, industry)
                    VALUES (?, ?)
                ''', (form_id, industry))
            
            for product in alignments['product']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, product)
                    VALUES (?, ?)
                ''', (form_id, product))
            
            for lifecycle in alignments['customer_lifecycle']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, customer_lifecycle)
                    VALUES (?, ?)
                ''', (form_id, lifecycle))
            
            for messaging in alignments['core_messaging']:
                self.cursor.execute('''
                    INSERT INTO form_alignments (form_id, core_messaging)
                    VALUES (?, ?)
                ''', (form_id, messaging))
            
            # Insert review
            review = template['review']
            self.cursor.execute('''
                INSERT INTO form_review (form_id, status_basic, status_execution, ready_for_activation)
                VALUES (?, ?, ?, ?)
            ''', (form_id, review['status_basic'], review['status_execution'], review['ready_for_activation']))
            
            self.conn.commit()
            print(f"Sample data inserted successfully! Form ID: {form_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting sample data: {e}")
            self.conn.rollback()
            return False
    
    def show_tables(self):
        """Show all tables in the database"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table[0]}")
            return tables
        except Exception as e:
            print(f"Error showing tables: {e}")
            return []

def main():
    """Main function to set up the database"""
    db = SmartTacticDB()
    
    if db.connect():
        print("Setting up SmartTactic database...")
        
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
    
    db.disconnect()
    print("\nDatabase setup completed!")

if __name__ == "__main__":
    main()
