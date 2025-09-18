# Smart Tactic API - Complete Guide

A comprehensive Flask-based API for managing SmartTactic marketing forms with multiple database backend options.

## Table of Contents

1. [Overview](#overview)
2. [Database Options](#database-options)
3. [Quick Start](#quick-start)
4. [Installation & Setup](#installation--setup)
5. [API Endpoints](#api-endpoints)
6. [Database Implementations](#database-implementations)
7. [Usage Examples](#usage-examples)
8. [Testing](#testing)
9. [Migration Guide](#migration-guide)
10. [Performance & Scaling](#performance--scaling)
11. [Production Considerations](#production-considerations)
12. [Troubleshooting](#troubleshooting)
13. [Support](#support)

## Overview

The Smart Tactic API is a flexible, multi-database solution for managing marketing forms. It supports three different database backends, each optimized for different use cases:

- **SQLite**: Traditional relational database for complex queries and ACID compliance
- **Firestore**: Cloud NoSQL database for scalability and real-time features
- **TinyDB**: Lightweight local NoSQL database for development and prototyping

## Database Options

### 🗄️ **SQLite** (Original)
- **File**: `app.py`, `db_setup.py`
- **Database**: `smart_tactic.db`
- **Type**: Relational SQL database
- **Best for**: Traditional applications, complex queries, ACID compliance

### 🔥 **Firestore** (Cloud NoSQL)
- **File**: `app_firestore.py`, `db_setup_firestore.py`
- **Database**: Google Cloud Firestore
- **Type**: Cloud NoSQL document database
- **Best for**: Scalable applications, real-time features, global distribution

### 📄 **TinyDB** (Lightweight NoSQL)
- **File**: `app_tinydb.py`, `db_setup_tinydb.py`
- **Database**: `smart_tactic_tinydb.json`
- **Type**: Local NoSQL document database
- **Best for**: Development, prototyping, small applications

### Quick Comparison

| Feature | SQLite | Firestore | TinyDB |
|---------|--------|-----------|--------|
| **Setup Time** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Dependencies** | Built-in | Many | Minimal |
| **Scalability** | Medium | Unlimited | Small |
| **Real-time** | ❌ | ✅ | ❌ |
| **Offline** | ✅ | ❌ | ✅ |
| **Cost** | Free | Pay-per-use | Free |
| **Deployment** | Easy | Complex | Very Easy |
| **Learning Curve** | Medium | High | Low |

## Quick Start

### Choose Your Database

**For Development/Prototyping:**
```bash
# TinyDB - Fastest setup
pip install tinydb
python db_setup_tinydb.py
python app_tinydb.py
```

**For Traditional Applications:**
```bash
# SQLite - Already set up
python app.py
```

**For Scalable Cloud Applications:**
```bash
# Firestore - Requires Google Cloud setup
pip install -r requirements.txt
# Follow Firestore setup guide below
python app_firestore.py
```

## Installation & Setup

### Prerequisites

- Python 3.7+
- pip package manager

### 1. Install Dependencies

```bash
# For all databases
pip install -r requirements.txt

# Or install specific packages
pip install flask tinydb  # For TinyDB
pip install flask         # For SQLite (built-in)
pip install -r requirements.txt  # For Firestore (includes all)
```

### 2. Database Setup

#### SQLite Setup
```bash
python db_setup.py
```
This creates:
- `smart_tactic.db` file
- All necessary tables with relationships
- Sample data from `mockdata.json`

#### TinyDB Setup
```bash
python db_setup_tinydb.py
```
This creates:
- `smart_tactic_tinydb.json` file
- All necessary tables (collections)
- Sample data from `mockdata.json`

#### Firestore Setup
```bash
# 1. Set up Google Cloud project
# 2. Enable Firestore
# 3. Create service account
# 4. Set environment variables
python db_setup_firestore.py
```

### 3. Start the API

```bash
# SQLite
python app.py

# TinyDB
python app_tinydb.py

# Firestore
python app_firestore.py
```

All APIs run on `http://localhost:5000`

## API Endpoints

All implementations provide identical RESTful API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/forms` | Create a new form |
| `GET` | `/api/forms` | List all forms |
| `GET` | `/api/forms/<id>` | Get form details by ID |
| `PUT` | `/api/forms/<id>` | Update an existing form |
| `DELETE` | `/api/forms/<id>` | Delete a form |
| `GET` | `/api/health` | Health check endpoint |

## Database Implementations

### SQLite Implementation

**Files:**
- `app.py` - Flask application
- `db_setup.py` - Database setup script
- `smart_tactic.db` - SQLite database file

**Database Schema:**
- **forms**: Main form information
- **form_basic**: Basic event details
- **form_organization**: Organizational structure
- **form_logistics**: Event logistics and location
- **form_finance**: Financial information
- **form_partners**: Partner involvement details
- **form_alignments**: Target audience and product alignments
- **form_review**: Review status information

**Features:**
- ACID compliance
- Complex relational queries
- Foreign key relationships
- Built-in Python support

### TinyDB Implementation

**Files:**
- `app_tinydb.py` - Flask application
- `db_setup_tinydb.py` - Database setup script
- `test_tinydb.py` - Functionality tests
- `test_api_tinydb.py` - API tests
- `smart_tactic_tinydb.json` - JSON database file

**Collections:**
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

**Features:**
- Single JSON file storage
- No server required
- Easy querying with Query objects
- Automatic document IDs
- Human-readable data format

### Firestore Implementation

**Files:**
- `app_firestore.py` - Flask application
- `db_setup_firestore.py` - Database setup script
- `firestore_config.py` - Configuration management
- `test_firestore.py` - Connection tests

**Collections:**
Same as TinyDB collections, but stored in Google Cloud Firestore.

**Features:**
- Cloud-based storage
- Real-time synchronization
- Automatic scaling
- Global distribution
- Built-in security

## Usage Examples

### Creating a Form

```bash
curl -X POST http://localhost:5000/api/forms \
  -H "Content-Type: application/json" \
  -d '{
    "category": "promote",
    "tactic_type": "Events & Experiences",
    "event_kind": "Single",
    "basic": {
      "event_name": "Marketing Summit 2024",
      "description": "Annual marketing conference",
      "owner_email": "user@example.com",
      "start_date": "2024-06-01",
      "end_date": "2024-06-03"
    },
    "organization": {
      "ring": "Ring 1",
      "party": "Marketing",
      "category": "Technology"
    }
  }'
```

### Python API Usage

```python
import requests

# Create a form
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
form_id = response.json()["form_id"]

# Get form details
response = requests.get(f"http://localhost:5000/api/forms/{form_id}")
form = response.json()

# Update form
update_data = {"category": "Updated Event"}
response = requests.put(f"http://localhost:5000/api/forms/{form_id}", json=update_data)

# Delete form
response = requests.delete(f"http://localhost:5000/api/forms/{form_id}")
```

### Direct Database Access

#### SQLite
```python
import sqlite3

conn = sqlite3.connect('smart_tactic.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM forms WHERE category = ?', ('Event',))
forms = cursor.fetchall()
conn.close()
```

#### TinyDB
```python
from tinydb import TinyDB, Query

db = TinyDB('smart_tactic_tinydb.json')
forms = db.table('forms')
Form = Query()
results = forms.search(Form.category == "Event")
```

#### Firestore
```python
from google.cloud import firestore

db = firestore.Client()
forms = db.collection('forms')
docs = forms.where('category', '==', 'Event').stream()
```

## Testing

### Run All Tests

#### SQLite
```bash
python test_api.py
```

#### TinyDB
```bash
python test_tinydb.py        # Database functionality
python test_api_tinydb.py    # API endpoints
```

#### Firestore
```bash
python test_firestore.py     # Connection test
python test_api.py           # API endpoints (after setup)
```

### Test Results

All implementations should pass the same test suite:

```
🚀 Testing API...
✓ Health check passed
✓ Get all forms: X forms found
✓ Created form with ID: X
✓ Retrieved form: [form details]
✓ Updated form successfully
✓ Deleted form successfully
🎉 API testing completed!
```

## Migration Guide

### SQLite → TinyDB

```python
import sqlite3
from tinydb import TinyDB

# Read from SQLite
conn = sqlite3.connect('smart_tactic.db')
cursor = conn.cursor()
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

### TinyDB → Firestore

```python
from tinydb import TinyDB
from google.cloud import firestore

# Read from TinyDB
tinydb = TinyDB('smart_tactic_tinydb.json')
forms = tinydb.table('forms').all()

# Write to Firestore
firestore_db = firestore.Client()
for form in forms:
    firestore_db.collection('forms').add(form)
```

### Backup and Restore

#### SQLite
```bash
# Backup
copy smart_tactic.db backup_$(Get-Date -Format "yyyyMMdd").db

# Restore
copy backup_20240101.db smart_tactic.db
```

#### TinyDB
```bash
# Backup
copy smart_tactic_tinydb.json backup_$(Get-Date -Format "yyyyMMdd").json

# Restore
copy backup_20240101.json smart_tactic_tinydb.json
```

#### Firestore
```bash
# Use Google Cloud Console or gcloud CLI
gcloud firestore export gs://your-bucket/backup
gcloud firestore import gs://your-bucket/backup
```

## Performance & Scaling

### Small Dataset (< 1,000 forms)
- **TinyDB**: Fastest setup, good performance
- **SQLite**: Good performance, more features
- **Firestore**: Overkill, network latency

### Medium Dataset (1,000 - 100,000 forms)
- **SQLite**: Best performance, good features
- **TinyDB**: Good performance, simple
- **Firestore**: Good for real-time features

### Large Dataset (> 100,000 forms)
- **Firestore**: Best scalability
- **SQLite**: Good with proper indexing
- **TinyDB**: Not recommended

### Performance Tips

#### SQLite
```python
# Create indexes
cursor.execute('CREATE INDEX idx_category ON forms(category)')
cursor.execute('CREATE INDEX idx_owner ON form_basic(owner_email)')
```

#### TinyDB
```python
# Create indexes
db.table('forms').create_index('category')
db.table('form_basic').create_index('owner_email')

# Batch operations
documents = [{"name": f"Item {i}"} for i in range(100)]
table.insert_multiple(documents)
```

#### Firestore
```python
# Use batch operations
batch = db.batch()
for doc in documents:
    batch.set(db.collection('forms').document(), doc)
batch.commit()
```

## Production Considerations

### Security

1. **Authentication**: Implement proper authentication and authorization
2. **Rate Limiting**: Add request rate limiting
3. **Input Validation**: Validate all input data
4. **Environment Variables**: Use environment variables for sensitive data

### Deployment

#### SQLite/TinyDB
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Firestore
```bash
# Deploy to Google Cloud Run or App Engine
gcloud run deploy smart-tactic-api --source .
```

### Monitoring

```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Health checks
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    })
```

### Backup Strategy

```bash
# Daily backup script
@echo off
set BACKUP_DIR=backups
mkdir %BACKUP_DIR% 2>nul
copy smart_tactic.db %BACKUP_DIR%\smart_tactic_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
copy smart_tactic_tinydb.json %BACKUP_DIR%\smart_tactic_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**SQLite:**
```
sqlite3.OperationalError: no such table: forms
```
**Solution**: Run `python db_setup.py`

**TinyDB:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'smart_tactic_tinydb.json'
```
**Solution**: Run `python db_setup_tinydb.py`

**Firestore:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```
**Solution**: Set up service account and environment variables

#### 2. Import Errors

```
ModuleNotFoundError: No module named 'tinydb'
```
**Solution**: `pip install tinydb`

```
ModuleNotFoundError: No module named 'google.cloud'
```
**Solution**: `pip install google-cloud-firestore`

#### 3. Port Already in Use

```
OSError: [Errno 98] Address already in use
```
**Solution**: 
```bash
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
app.run(port=5001)
```

#### 4. Permission Errors

```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file permissions, ensure no other process is using the database

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In Flask app
app.run(debug=True)
```

### Database Inspection

#### SQLite
```python
import sqlite3
conn = sqlite3.connect('smart_tactic.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)
```

#### TinyDB
```python
from tinydb import TinyDB
db = TinyDB('smart_tactic_tinydb.json')
for table_name in db.tables():
    count = len(db.table(table_name))
    print(f"{table_name}: {count} documents")
```

#### Firestore
```python
from google.cloud import firestore
db = firestore.Client()
collections = db.collections()
for collection in collections:
    docs = collection.stream()
    count = len(list(docs))
    print(f"{collection.id}: {count} documents")
```

## LLM Observability with Langfuse

The Smart Tactic API includes integrated LLM observability and monitoring through Langfuse, providing comprehensive insights into AI assistant performance, user interactions, and system behavior.

### Features

- **LLM Tracing**: Automatic tracing of all LLM calls with input/output logging
- **Session Management**: Track user sessions and conversation flows
- **Performance Metrics**: Monitor response times, token usage, and model performance
- **User Feedback**: Capture and analyze user feedback on AI responses
- **State Monitoring**: Track form state changes and completion rates
- **Error Tracking**: Log validation errors and system issues
- **Analytics Dashboard**: Comprehensive insights and reporting

### Setup

1. **Install Dependencies**:
   ```bash
   pip install langfuse>=2.0.0
   ```

2. **Configure Environment Variables**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Add your Langfuse credentials
   LANGFUSE_PUBLIC_KEY=pk_your_public_key_here
   LANGFUSE_SECRET_KEY=sk_your_secret_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud
   ```

3. **Langfuse is automatically enabled** when both public and secret keys are provided.

### Configuration

The Langfuse integration is configured in `config.py`:

```python
@dataclass
class LangfuseConfig:
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    host: str = "https://cloud.langfuse.com"
    enabled: bool = False  # Auto-enabled when keys are provided
```

### What Gets Tracked

#### LLM Generations
- **Input Prompt**: Complete prompt sent to the LLM
- **Model**: Model name and version (e.g., gemini-1.5-pro-latest)
- **Output**: Full LLM response including markdown and field data
- **Metadata**: Session ID, workflow ID, user question
- **Performance**: Response time, token usage, cost estimation

#### User Sessions
- **Session Traces**: Complete conversation flows
- **User Questions**: All user inputs and questions
- **State Changes**: Form field updates and completions
- **Validation Events**: Field validation results and errors

#### System Events
- **Form Completions**: Track when forms are fully completed
- **State Updates**: Monitor form state changes over time
- **Error Events**: Capture and categorize system errors
- **User Feedback**: Collect user ratings and feedback

### Usage Examples

#### Viewing Traces in Langfuse Dashboard

1. **Navigate to your Langfuse project**
2. **View Traces**: See all conversation sessions
3. **Analyze Performance**: Monitor response times and costs
4. **Review Conversations**: Examine user interactions and AI responses

#### Custom Analytics Queries

```python
# Example: Get completion rates by workflow
from services.langfuse_service import LangfuseService

langfuse = LangfuseService()
completion_metrics = langfuse.get_form_completion_analytics(
    workflow_id="workflow_123",
    date_range="last_30_days"
)
```

### Integration Architecture

The Langfuse integration is implemented through:

1. **LangfuseService**: Core service handling all Langfuse operations
2. **ChatService Integration**: Automatic tracing in synchronous chat processing
3. **AsyncChatService Integration**: Async-compatible tracing for concurrent operations
4. **Dependency Injection**: Seamless integration through the DI container

### Privacy and Security

- **Data Encryption**: All data transmitted to Langfuse is encrypted in transit
- **Configurable Logging**: Control what data gets logged (disable PII if needed)
- **Optional Integration**: Langfuse can be completely disabled by not providing keys
- **Local Development**: Works offline when Langfuse is disabled

### Monitoring Best Practices

1. **Set Up Alerts**: Configure alerts for high error rates or slow responses
2. **Regular Reviews**: Weekly review of conversation quality and completion rates
3. **Performance Optimization**: Use metrics to identify and fix bottlenecks
4. **User Feedback**: Actively collect and analyze user feedback for improvements

### Troubleshooting

#### Common Issues

**Langfuse Not Connecting**:
```bash
# Check environment variables
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Verify network connectivity
curl -I https://cloud.langfuse.com
```

**Missing Traces**:
- Ensure both public and secret keys are set
- Check that `langfuse_service.is_enabled()` returns `True`
- Verify no network connectivity issues

**Performance Impact**:
- Langfuse calls are made asynchronously to minimize impact
- Consider disabling in high-throughput scenarios if needed
- Monitor application performance metrics

## Support

### Documentation Links

- **SQLite**: [SQLite Documentation](https://www.sqlite.org/docs.html)
- **Firestore**: [Firestore Documentation](https://firebase.google.com/docs/firestore)
- **TinyDB**: [TinyDB Documentation](https://tinydb.readthedocs.io/)
- **Flask**: [Flask Documentation](https://flask.palletsprojects.com/)
- **Langfuse**: [Langfuse Documentation](https://langfuse.com/docs)

### Getting Help

1. **Check logs**: Look at console output for error messages
2. **Verify setup**: Ensure all dependencies are installed
3. **Test connectivity**: Use health check endpoints
4. **Check documentation**: Refer to specific database documentation

### File Structure <- Needs to be modified based on the architecture and flow discussion>

```
Smart_Tactic_API/
├── # SQLite Implementation
├── app.py                    # SQLite Flask app
├── db_setup.py              # SQLite database setup
├── smart_tactic.db          # SQLite database file
│
├── # Firestore Implementation
├── app_firestore.py         # Firestore Flask app
├── db_setup_firestore.py    # Firestore database setup
├── firestore_config.py      # Firestore configuration
├── README_FIRESTORE.md      # Firestore documentation
│
├── # TinyDB Implementation
├── app_tinydb.py            # TinyDB Flask app
├── db_setup_tinydb.py       # TinyDB database setup
├── test_tinydb.py           # TinyDB tests
├── test_api_tinydb.py       # TinyDB API tests
├── smart_tactic_tinydb.json # TinyDB database file
├── README_TINYDB.md         # TinyDB documentation
│
├── # Shared Files
├── requirements.txt         # All dependencies
├── mockdata.json           # Sample data
├── test_api.py             # API tests
├── README.md               # Original README
├── README_COMPLETE.md      # This comprehensive guide
└── DATABASE_OPTIONS.md     # Database comparison
```

## Conclusion

The Smart Tactic API provides three complete database implementations, each optimized for different use cases:

1. **SQLite** - Traditional, reliable, feature-rich for complex applications
2. **Firestore** - Scalable, cloud-native, real-time for large-scale applications  
3. **TinyDB** - Simple, lightweight, developer-friendly for prototyping and small applications

Choose the implementation that best fits your needs, or use different ones for different environments (TinyDB for development, SQLite for testing, Firestore for production).

All implementations provide the same API interface, ensuring compatibility and easy migration between database backends as your needs evolve.
