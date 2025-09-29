import os
from tinydb import TinyDB

# Define the path to the data directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
DB_PATH = os.path.join(DATA_DIR, 'form_db.json')

def verify_database():
    """
    Connects to the TinyDB database and prints its structure and content.
    """
    print(f"Verifying Database at: {DB_PATH} ---\n")

    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found. Please run 'database_setup.py' first.")
        return

    # Connect to the database
    db = TinyDB(DB_PATH)

    # 1. Get all table names (like SHOW TABLES in SQL)
    table_names = db.tables()
    print(f"Found Tables (Collections): {table_names}\n")

    # 2. Verify the 'form_structure' table
    print("--- Verifying 'form_structure' Table ---")
    if 'form_structure' in table_names:
        structure_table = db.table('form_structure')
        all_structures = structure_table.all()
        print(f"Found {len(all_structures)} document(s) in 'form_structure'.")
        # Print the first document to inspect its content
        if all_structures:
            print("Content of first document:")
            # The nested structure here IS the "tree" you're looking for
            print(all_structures[0])
    else:
        print("'form_structure' table not found.")

    print("\n" + "="*40 + "\n")

    # Verify the 'form_options' table
    print("--- Verifying 'form_options' Table ---")
    if 'form_options' in table_names:
        options_table = db.table('form_options')
        all_options = options_table.all()
        print(f"Found {len(all_options)} document(s) in 'form_options'.")
        # Print the first document to inspect its content
        if all_options:
            print("Content of first document:")
            print(all_options[0])
    else:
        print("'form_options' table not found.")

if __name__ == '__main__':
    verify_database()