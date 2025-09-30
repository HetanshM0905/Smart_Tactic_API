# Smart Tactics TinyDB Database Setup

This document explains how to set up the TinyDB database for the Smart Tactics application using the JSON data from the refactored form structure.

## Overview

The Smart Tactics application uses TinyDB as its primary NoSQL database for storing form structures, field options, autofill configurations, and event data. TinyDB provides a lightweight, file-based NoSQL solution that's perfect for development and small to medium-scale deployments.

## Files Created

### 1. Database Setup Scripts

- **`simple_tinydb_setup.py`** - Simple TinyDB setup (recommended)
- **`tinydb_setup.py`** - Full TinyDB setup with app integration
- **`test_simple_tinydb.py`** - Test script to verify TinyDB setup

### 2. Data Files (Created by setup)

- **`data/smart_tactic_tinydb.json`** - Main TinyDB database file
- **`data/form_structure.json`** - Form structure backup
- **`data/form_options.json`** - Form options backup
- **`data/sample_event.json`** - Sample event backup
- **`data/autofill_configs.json`** - Autofill configs backup

### 3. Client Integration

- **`app/integrations/tinydb_client.py`** - TinyDB client for data operations
- **`app/models/event_model.py`** - Updated with TinyDB methods

## Database Structure

### TinyDB Tables (Collections)

1. **`form_structures`** - Form structure definitions and field mappings
2. **`form_options`** - Field options and dependencies (170+ options)
3. **`autofill_configs`** - Autofill configuration rules
4. **`events`** - Event data storage
5. **`collections_info`** - Database schema documentation

### Form Structure

The form is organized into the following sections:

#### 1. Basic Info
- Event name and description
- Priority and owner
- Event dates and confidence
- Expected leads and inquiries

#### 2. Event Categorization
- Event ring (R1-R4)
- Event party (1st party, 3rd party)
- Event category and subcategory
- Category owners

#### 3. Logistics
- Funding status
- Hosting type (Digital, Physical, Hybrid)
- Location (City/Country)

#### 4. Financial Details
- Cost center
- Budget information
- Cost center splitting

#### 5. Partner Details
- Partner involvement
- Partner responsibilities
- Lead follow-up

#### 6. Alignments
- Account segments
- Buyer segments
- Industries and products
- Customer lifecycle
- Core messaging

#### 7. Campaign Program
- Tied to program status
- Adopt/Adapt/Invent classification

#### 8. Review & Submit
- Status tracking
- Activation readiness

## Quick Start

### 1. Install Dependencies

```bash
pip install tinydb
```

### 2. Run TinyDB Setup

```bash
# Simple setup (recommended)
python simple_tinydb_setup.py
```

This will:
- Create `data/` directory
- Initialize TinyDB database
- Load form structure from `refactored_code.json`
- Create sample data and configurations

### 3. Test the Setup

```bash
python test_simple_tinydb.py
```

## Event Model Fields

The EventModel class includes all 43 form fields:

```python
# Basic Info
eventName, eventDescription, priority, owner
eventStartDate, eventEndDate, EventDateConfidence
leads, numberOfInquiries

# Event Categorization
eventRing, eventParty, eventCategory, eventCategoryOwner
eventSubCategory, eventSubCategoryOwner

# Logistics
fundingStatus, hostingType, city, countries

# Financial Details
costCenter, hasSpend, totalBudget, splitCostCenter, costCenterSplit

# Partner Details
partnerInvolved, partnerName, responsibilities, leadFollowUp

# Alignments
account_segments, account_segment_type, buyer_segment_rollups
industries, products, customer_lifecycle, core_messaging

# Campaign Program
tiedToProgram, adoptAdaptInvent

# Review & Submit
statusBasicDetails, statusExecutionDetails, readyForActivation

# Extras
venue, registrationLink, salesKitLink
```

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

## Validation Rules

The EventModel includes comprehensive validation:

- **Required fields** - All mandatory form fields
- **Field length limits** - Text field character limits
- **Date validation** - Start date before end date
- **Conditional validation** - Fields required based on other field values
- **Business rules** - Location requirements based on hosting type
- **Budget validation** - Non-negative values

## Sample Data

The setup includes sample data:

- **Sample Event**: Google Cloud Next 2024 conference
- **Autofill Configs**: 4 rules for common field auto-population
- **Form Options**: 170+ dropdown options and dependencies
- **Form Structure**: Complete form with 8 sections and 43 fields

## Health Check

```python
from app.integrations.tinydb_client import TinyDBClient

client = TinyDBClient()
health = client.health_check()
print(health)
```

## Configuration

The TinyDB client uses the following configuration:

- **Database Path**: `data/smart_tactic_tinydb.json`
- **Storage**: JSON file with caching middleware
- **Collections**: Tables within the same database file

## Testing

Run the test script to verify setup:

```bash
python test_simple_tinydb.py
```

This will test:
- TinyDB database connection
- Basic CRUD operations
- Form structure retrieval
- Sample data access

## Performance Notes

- TinyDB is suitable for small to medium datasets
- Database file is loaded entirely into memory
- Use indexing for better query performance
- For large datasets, consider Firestore integration

## Backup and Recovery

- **Backup**: Copy `data/smart_tactic_tinydb.json`
- **Recovery**: Replace database file and restart application
- **Export**: Use TinyDB client to export data to JSON

## Next Steps

After running the TinyDB setup:

1. **Start the application**: `python -m app.main`
2. **Test API endpoints**: Use the provided sample data
3. **Create events**: Use the form structure to create new events
4. **Configure autofill**: Customize autofill rules for your needs
5. **Consider Firestore**: For cloud deployment and scaling

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Install TinyDB with `pip install tinydb`
2. **Database not found**: Run `python simple_tinydb_setup.py`
3. **JSON file not found**: Ensure `refactored_code.json` exists in `smart-tactic-test` directory
4. **Permission errors**: Check file permissions on `data/` directory

### Logs

Check application logs for detailed error information:
- Database connection issues
- Validation errors
- Form structure problems

## Migration from SQL

If migrating from SQL database:

1. Export existing data to JSON format
2. Run TinyDB setup: `python simple_tinydb_setup.py`
3. Import data using TinyDB client
4. Update application code to use TinyDB client

## Support

For issues or questions:
1. Check the application logs
2. Verify TinyDB database file exists
3. Test with sample data
4. Review form structure configuration
5. See [TINYDB_SETUP.md](TINYDB_SETUP.md) for detailed documentation