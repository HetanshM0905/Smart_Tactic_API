# Smart Tactic API - Firestore Migration Guide

This guide explains how to migrate from SQLite to Google Cloud Firestore for the Smart Tactic API.

## Overview

We've migrated from SQLite to Firestore to provide:
- **Scalability**: Handle larger datasets and concurrent users
- **Real-time updates**: Built-in real-time synchronization
- **Cloud-native**: Automatic backups, security, and global distribution
- **NoSQL flexibility**: Better handling of complex, nested data structures

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account
2. **Google Cloud Project**: Create a new project or use an existing one
3. **Firestore Database**: Enable Firestore in your project
4. **Service Account**: Create a service account with Firestore permissions

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt now includes:
- `google-cloud-firestore==2.11.1`
- `google-auth==2.23.4`
- `google-auth-oauthlib==1.1.0`
- `google-auth-httplib2==0.1.1`

### 2. Google Cloud Setup

#### Create a Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

#### Enable Firestore
1. In the Cloud Console, go to Firestore
2. Click "Create Database"
3. Choose a location (select the closest to your users)
4. Start in production mode (recommended)

#### Create Service Account
1. Go to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Give it a name (e.g., "smart-tactic-api")
4. Grant the "Cloud Datastore User" role
5. Create and download the JSON key file

### 3. Environment Configuration

Set the following environment variables:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_CLOUD_PROJECT_ID="your-project-id"
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"
```

**Linux/Mac:**
```bash
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

**Or create a .env file:**
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
FIRESTORE_DATABASE_ID=(default)
```

### 4. Database Setup

Run the Firestore setup script:

```bash
python db_setup_firestore.py
```

This will:
- Connect to your Firestore database
- Create all necessary collections
- Insert sample data from mockdata.json

### 5. Run the Application

Use the new Firestore-enabled app:

```bash
python app_firestore.py
```

## File Structure

```
Smart_Tactic_API/
├── app_firestore.py          # Main Flask app with Firestore
├── db_setup_firestore.py     # Firestore database setup
├── firestore_config.py       # Firestore configuration
├── requirements.txt          # Updated dependencies
├── mockdata.json            # Sample data
├── README_FIRESTORE.md      # This file
└── README.md                # Original README
```

## API Endpoints

The API endpoints remain the same, but now use Firestore:

- `POST /api/forms` - Create a new form
- `GET /api/forms` - Get all forms
- `GET /api/forms/<id>` - Get a specific form
- `PUT /api/forms/<id>` - Update a form
- `DELETE /api/forms/<id>` - Delete a form
- `GET /api/health` - Health check

## Data Structure

### Collections

Firestore uses collections instead of tables:

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
- `form_id` - Reference to the main form
- `created_at` - Timestamp of creation
- Field-specific data

## Key Differences from SQLite

| Aspect | SQLite | Firestore |
|--------|--------|-----------|
| **Structure** | Tables with schemas | Collections with documents |
| **Relationships** | Foreign keys | Document references |
| **Queries** | SQL | Firestore queries |
| **Scalability** | Single file, local | Cloud-based, distributed |
| **Real-time** | No | Built-in support |
| **Backups** | Manual | Automatic |

## Query Examples

### Get Forms by Category
```python
# Firestore query
docs = db.collections['forms'].where('category', '==', 'Event').stream()
```

### Get Forms by Date Range
```python
# Firestore query
docs = db.collections['form_basic'].where('start_date', '>=', '2024-01-01').stream()
```

### Complex Queries
```python
# Get forms with specific criteria
docs = db.collections['forms'].where('category', '==', 'Event').where('tactic_type', '==', 'Conference').stream()
```

## Security Considerations

1. **Service Account**: Keep your service account key secure
2. **IAM Roles**: Use least-privilege access
3. **Firestore Rules**: Configure security rules in Firestore console
4. **Environment Variables**: Don't commit credentials to version control

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Check service account key path
   - Verify IAM permissions
   - Ensure project ID is correct

2. **Collection Not Found**
   - Run `db_setup_firestore.py` first
   - Check collection names in code

3. **Permission Denied**
   - Verify service account has proper roles
   - Check Firestore security rules

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Tips

1. **Indexes**: Create composite indexes for complex queries
2. **Batch Operations**: Use batch writes for multiple operations
3. **Pagination**: Implement pagination for large result sets
4. **Caching**: Consider Redis for frequently accessed data

## Migration Checklist

- [ ] Install new dependencies
- [ ] Set up Google Cloud project
- [ ] Enable Firestore
- [ ] Create service account
- [ ] Set environment variables
- [ ] Run database setup
- [ ] Test API endpoints
- [ ] Update deployment scripts
- [ ] Monitor performance

## Support

For issues related to:
- **Firestore**: Check [Firestore documentation](https://firebase.google.com/docs/firestore)
- **Google Cloud**: Visit [Google Cloud Console](https://console.cloud.google.com/)
- **API Issues**: Check logs and verify configuration

## Next Steps

After successful migration:
1. **Monitor**: Watch Firestore usage and costs
2. **Optimize**: Implement indexes and optimize queries
3. **Scale**: Consider additional Firestore features like real-time listeners
4. **Backup**: Verify automatic backups are working
