# Smart Tactic API - TinyDB Setup Guide

This guide explains how to use TinyDB as a lightweight NoSQL database for the Smart Tactic API.

## Overview

TinyDB is a lightweight, document-oriented database that's perfect for:
- **Development and prototyping**: Quick setup, no server required
- **Small to medium applications**: Handles thousands of documents efficiently
- **Local storage**: All data stored in a single JSON file
- **Easy deployment**: No external dependencies or cloud setup required

## Prerequisites

- Python 3.7+
- pip package manager

## Quick Start

### 1. Install Dependencies

```bash
pip install tinydb flask
```

### 2. Set Up Database

```bash
python db_setup_tinydb.py
```

### 3. Run the Application

```bash
python app_tinydb.py
```

### 4. Test the API

```bash
python test_api_tinydb.py
```

## File Structure

```
Smart_Tactic_API/
├── app_tinydb.py              # Main Flask app with TinyDB
├── db_setup_tinydb.py         # TinyDB database setup
├── test_tinydb.py             # TinyDB functionality tests
├── test_api_tinydb.py         # API endpoint tests
├── check_tinydb.py            # Database inspection tool
├── smart_tactic_tinydb.json   # TinyDB data file (created automatically)
├── requirements.txt           # Dependencies
└── README_TINYDB.md          # This file
```

## API Endpoints

The API provides the same endpoints as the original SQLite version:

- `POST /api/forms` - Create a new form
- `GET /api/forms` - Get all forms
- `GET /api/forms/<id>` - Get a specific form
- `PUT /api/forms/<id>` - Update a form
- `DELETE /api/forms/<id>` - Delete a form
- `GET /api/health` - Health check

## Data Structure

### Tables (Collections)

TinyDB uses tables instead of SQL tables:

- `forms` - Main form documents
- `form_basic` - Basic information
- `form_organization` - Organization details
- `form_logistics` - Logistics information
- `form_countries` - Country associations
- `form_finance` - Financial details
- `form_cost_center_splits` - Cost center splits
- `form_extras` - Additional information
- `form_partners` - Partner information
- `form_partner_responsibilities` - Partner responsibilities
- `form_forecasts` - Forecast data
- `form_campaign_program` - Campaign program details
- `form_program_splits` - Program splits
- `form_alignments` - Alignment information
- `form_review` - Review status

### Document Structure

Each document contains:
- `form_id` - Reference to the main form (for related documents)
- `created_at` - ISO timestamp of creation
- Field-specific data

## Usage Examples

### Creating a Form

```python
import requests

form_data = {
    "category": "Event",
    "tactic_type": "Conference",
    "event_kind": "Single",
    "basic": {
        "event_name": "Tech Conference 2024",
        "description": "Annual technology conference",
        "owner_email": "organizer@example.com"
    }
}

response = requests.post("http://localhost:5000/api/forms", json=form_data)
print(response.json())
```

### Querying Forms

```python
# Get all forms
response = requests.get("http://localhost:5000/api/forms")
forms = response.json()["forms"]

# Get specific form
response = requests.get("http://localhost:5000/api/forms/1")
form = response.json()
```

### Direct Database Access

```python
from tinydb import TinyDB, Query

# Open database
db = TinyDB("smart_tactic_tinydb.json")

# Access tables
forms = db.table('forms')
basic = db.table('form_basic')

# Query data
Form = Query()
results = forms.search(Form.category == "Event")

# Insert data
form_id = forms.insert({
    "category": "Event",
    "tactic_type": "Conference",
    "created_at": "2024-01-01T00:00:00"
})
```

## Key Features

### 1. **Lightweight**
- Single file storage (`smart_tactic_tinydb.json`)
- No server process required
- Minimal memory footprint

### 2. **Easy Querying**
```python
# Simple queries
results = table.search(Query().field == "value")

# Complex queries
results = table.search(
    (Query().age > 25) & (Query().city == "New York")
)

# Range queries
results = table.search(Query().date >= "2024-01-01")
```

### 3. **Automatic IDs**
- TinyDB automatically assigns document IDs
- IDs are integers starting from 1
- Use `doc_id` to reference documents

### 4. **JSON Storage**
- Human-readable data format
- Easy to backup and restore
- Can be edited manually if needed

## Comparison: TinyDB vs SQLite vs Firestore

| Feature | TinyDB | SQLite | Firestore |
|---------|--------|--------|-----------|
| **Setup** | ✅ Instant | ✅ Simple | ❌ Complex |
| **Dependencies** | ✅ Minimal | ✅ Built-in | ❌ Many |
| **Storage** | JSON file | Binary file | Cloud |
| **Scalability** | Small-Medium | Medium-Large | Unlimited |
| **Real-time** | ❌ No | ❌ No | ✅ Yes |
| **Offline** | ✅ Yes | ✅ Yes | ❌ No |
| **Cost** | Free | Free | Pay-per-use |
| **Deployment** | ✅ Easy | ✅ Easy | ❌ Complex |

## Performance Tips

### 1. **Indexing**
```python
# Create indexes for frequently queried fields
db.table('forms').create_index('category')
db.table('form_basic').create_index('owner_email')
```

### 2. **Batch Operations**
```python
# Insert multiple documents at once
documents = [{"name": f"Item {i}"} for i in range(100)]
table.insert_multiple(documents)
```

### 3. **Memory Management**
```python
# Close database when done
db.close()

# Use context manager
with TinyDB('data.json') as db:
    # Database operations
    pass
```

## Testing

### Run All Tests
```bash
# Test TinyDB functionality
python test_tinydb.py

# Test API endpoints
python test_api_tinydb.py

# Check database contents
python check_tinydb.py
```

### Test Results
```
🚀 Starting TinyDB Tests...
✓ TinyDB dependencies imported successfully
✓ Connected to TinyDB: test_tinydb.json
✓ Created test document with ID: 1
✓ Read test document: test_value
✓ Updated test document
✓ Update verified
✓ Deleted test document
✓ Query result: 2 documents with age > 25
✓ Complex query result: 1 documents
✓ Field search working correctly
✓ Batch insert completed
✓ Batch created 3 documents
✓ Batch update completed
✓ Batch update verified
🎉 All tests passed! TinyDB is working correctly.
```

## Troubleshooting

### Common Issues

1. **Import Error**
   ```
   ModuleNotFoundError: No module named 'tinydb'
   ```
   **Solution**: `pip install tinydb`

2. **Permission Error**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Check file permissions, ensure no other process is using the database

3. **JSON Decode Error**
   ```
   json.decoder.JSONDecodeError
   ```
   **Solution**: Database file is corrupted, restore from backup or recreate

4. **Form Not Found (404)**
   ```
   GET /api/forms/999 HTTP/1.1" 404
   ```
   **Solution**: Check if form ID exists using `python check_tinydb.py`

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Data Migration

### From SQLite to TinyDB
```python
import sqlite3
from tinydb import TinyDB

# Read from SQLite
sqlite_conn = sqlite3.connect('smart_tactic.db')
cursor = sqlite_conn.cursor()
cursor.execute('SELECT * FROM forms')
forms = cursor.fetchall()

# Write to TinyDB
tinydb = TinyDB('smart_tactic_tinydb.json')
forms_table = tinydb.table('forms')
for form in forms:
    forms_table.insert({
        'id': form[0],
        'category': form[1],
        'tactic_type': form[2],
        # ... map other fields
    })
```

### Backup and Restore
```bash
# Backup
copy smart_tactic_tinydb.json backup_$(Get-Date -Format "yyyyMMdd").json

# Restore
copy backup_20240101.json smart_tactic_tinydb.json
```

## Production Considerations

### 1. **File Locking**
- TinyDB uses file locking to prevent corruption
- Multiple processes can read simultaneously
- Only one process can write at a time

### 2. **Performance Limits**
- Recommended: < 10,000 documents per table
- For larger datasets, consider SQLite or PostgreSQL

### 3. **Backup Strategy**
```bash
# Daily backup script
@echo off
set BACKUP_DIR=backups
mkdir %BACKUP_DIR% 2>nul
copy smart_tactic_tinydb.json %BACKUP_DIR%\smart_tactic_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json
```

### 4. **Monitoring**
```python
# Check database size
import os
size = os.path.getsize('smart_tactic_tinydb.json')
print(f"Database size: {size / 1024:.2f} KB")

# Count documents
from tinydb import TinyDB
db = TinyDB('smart_tactic_tinydb.json')
for table_name in db.tables():
    count = len(db.table(table_name))
    print(f"{table_name}: {count} documents")
```

## Next Steps

After successful setup:

1. **Customize**: Modify the data structure for your needs
2. **Scale**: Monitor performance and consider migration if needed
3. **Backup**: Implement regular backup procedures
4. **Monitor**: Set up logging and monitoring
5. **Deploy**: Use a production WSGI server like Gunicorn

## Support

For issues related to:
- **TinyDB**: Check [TinyDB documentation](https://tinydb.readthedocs.io/)
- **API Issues**: Check logs and verify database file
- **Performance**: Consider indexing and query optimization

## Summary

TinyDB provides a perfect balance of simplicity and functionality for the Smart Tactic API:

✅ **Easy Setup**: No external dependencies or cloud configuration  
✅ **Fast Development**: Instant database creation and testing  
✅ **Portable**: Single JSON file can be easily moved and backed up  
✅ **Flexible**: NoSQL structure adapts to changing requirements  
✅ **Reliable**: File-based storage with automatic locking  

Perfect for development, testing, and small to medium production applications!
