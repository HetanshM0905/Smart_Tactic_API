# TinyDB Database Setup

This document explains how to set up and use the TinyDB database for the Smart Tactics application.

## Overview

The Smart Tactics application uses TinyDB as its primary NoSQL database for storing:
- Form structures and field mappings
- Form options and dependencies
- Autofill configurations
- Event data
- Collections metadata

## Quick Start

### 1. Install Dependencies

```bash
pip install tinydb
```

### 2. Run Database Setup

```bash
python simple_tinydb_setup.py
```

This will:
- Create a `data/` directory
- Initialize TinyDB database at `data/smart_tactic_tinydb.json`
- Load form structure from `refactored_code.json`
- Create sample data and configurations

### 3. Test the Setup

```bash
python test_simple_tinydb.py
```

## Database Structure

The TinyDB database contains the following tables:

### `form_structures`
- **Purpose**: Form structure definitions and field mappings
- **Key Document**: `smart_tactic_form`
- **Fields**: `form_name`, `form_mapping`, `sections`

### `form_options`
- **Purpose**: Field options and dependencies
- **Key Field**: `field_id` (e.g., "f1", "f2", etc.)
- **Fields**: `field_id`, `field_name`, `options`

### `autofill_configs`
- **Purpose**: Autofill configuration rules
- **Key Field**: `_id` (e.g., "autofill_001")
- **Fields**: `event_type`, `field_name`, `autofill_rule`, `priority`

### `events`
- **Purpose**: Event data storage
- **Key Field**: `event_id`
- **Fields**: All event model fields (43 total)

### `collections_info`
- **Purpose**: Database schema documentation
- **Key Document**: `collections_info`

## Usage Examples

### Using TinyDB Client

```python
from app.integrations.tinydb_client import TinyDBClient

# Initialize client
client = TinyDBClient()

# Store an event
event_data = {
    "event_id": "event_001",
    "eventName": "My Conference",
    "priority": "P0 - In budget",
    # ... other fields
}
result = client.store_event(event_data)

# Get an event
event = client.get_event("event_001")

# Get form structure
form_structure = client.get_form_structure()

# Get form options
form_options = client.get_form_options()
```

### Using Event Model

```python
from app.models.event_model import EventModel

# Create event
event = EventModel.create_draft(
    event_id="event_002",
    event_name="Another Conference",
    event_description="Description here"
)

# Save to TinyDB
result = event.save_to_tinydb()

# Load from TinyDB
loaded_event = EventModel.load_from_tinydb("event_002")
```

## Database Files

- **`data/smart_tactic_tinydb.json`**: Main TinyDB database file
- **`data/form_structure.json`**: Form structure backup
- **`data/form_options.json`**: Form options backup
- **`data/autofill_configs.json`**: Autofill configs backup
- **`data/sample_event.json`**: Sample event backup

## Configuration

The TinyDB client uses the following configuration:

- **Database Path**: `data/smart_tactic_tinydb.json`
- **Storage**: JSON file with caching middleware
- **Collections**: Tables within the same database file

## Health Check

```python
from app.integrations.tinydb_client import TinyDBClient

client = TinyDBClient()
health = client.health_check()
print(health)
```

## Troubleshooting

### Database Not Found
- Ensure `data/` directory exists
- Run `python simple_tinydb_setup.py` to create database

### Permission Errors
- Check file permissions on `data/` directory
- Ensure write access to database file

### Import Errors
- Install TinyDB: `pip install tinydb`
- Check Python path includes `app/` directory

## Migration from SQL

If migrating from SQL database:

1. Export existing data to JSON format
2. Run TinyDB setup: `python simple_tinydb_setup.py`
3. Import data using TinyDB client
4. Update application code to use TinyDB client

## Performance Notes

- TinyDB is suitable for small to medium datasets
- For large datasets, consider Firestore integration
- Database file is loaded entirely into memory
- Use indexing for better query performance

## Backup and Recovery

- Backup: Copy `data/smart_tactic_tinydb.json`
- Recovery: Replace database file and restart application
- Export: Use TinyDB client to export data to JSON

## Next Steps

1. **Production**: Consider Firestore for cloud storage
2. **Scaling**: Implement data partitioning for large datasets
3. **Monitoring**: Add database performance metrics
4. **Backup**: Implement automated backup strategy

