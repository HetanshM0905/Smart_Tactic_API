import json
from tinydb import TinyDB
import os

# Define paths to make the script runnable from anywhere
print("--- Starting Database Setup ---")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
SOURCE_JSON_PATH = os.path.join(DATA_DIR, 'refactored_code.json')
DB_PATH = os.path.join(DATA_DIR, 'form_db.json')

# 1. Check if the data directory exists 
if not os.path.exists(DATA_DIR):
    print(f"Error: The 'data' directory does not exist at {DATA_DIR}")
    exit()
print(f"Data directory found at: {DATA_DIR}")  

# 2. Load the JSON data from your file
try:
    with open(SOURCE_JSON_PATH, 'r') as f:
        data = json.load(f)
    print(f"Successfully loaded source JSON from: {SOURCE_JSON_PATH}")
except FileNotFoundError:
    print(f"Error: Source JSON file not found at {SOURCE_JSON_PATH}. Please make sure 'refactored_code.json' is in the 'data' folder.")
    exit()
except json.JSONDecodeError:
    print(f"Error: The file at {SOURCE_JSON_PATH} is not valid JSON. Please check its contents.")
    exit()

# 3. Initialize the TinyDB Database
# This will create a file named 'form_db.json' inside the 'data' directory
db = TinyDB(DB_PATH)

# 4. Create/Clear the two tables
structure_table = db.table('form_structure')
options_table = db.table('form_options')

# Clear any existing data
structure_table.truncate()
options_table.truncate()
print(f"Cleared existing tables in the database at: {DB_PATH}")

# 5. Insert the data into the respective tables
# We insert each document with a specific, queryable ID.

# Separate lookups from pages for better architecture
if 'lookups' in data:
    # Insert lookups into form_options table
    options_table.insert({'id': 'all_lookups', 'data': data['lookups']})
    print("-> Successfully inserted lookups into form_options with id 'all_lookups'.")
    
    # Create structure without lookups
    structure_data = {k: v for k, v in data.items() if k != 'lookups'}
    structure_table.insert({'id': 'main_form', 'data': structure_data})
    print("-> Successfully inserted form structure (without lookups) with id 'main_form'.")
else:
    # Fallback: insert entire JSON if no lookups found
    structure_table.insert({'id': 'main_form', 'data': data})
    print("-> Successfully inserted complete form structure with id 'main_form'.")

db.close()
print("\n--- Database setup is complete! ---")
print(f"The database file '{os.path.basename(DB_PATH)}' is ready inside the 'data' folder.")

