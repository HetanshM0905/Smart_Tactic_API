# Smart Tactics POC - Dynamic Form System

A proof-of-concept for a dynamic form system that renders forms based on JSON configuration, built with Flask backend and TinyDB storage.

## Project Overview

This POC demonstrates a flexible, data-driven form system where:
- Forms are defined in JSON configuration
- Backend serves form structure and options via REST API
- Frontend can dynamically render any form without code changes
- Supports complex features like cascading dropdowns, conditional visibility, and field grouping

## Architecture

### Backend Stack
- **Flask** - REST API server
- **TinyDB** - JSON-based database
- **Python 3** - Backend language

### Database Structure
- **`form_structure` table** - Form pages, fields, validation rules
- **`form_options` table** - Dropdown options and lookup data

### API Endpoints
- `GET /api/form-structure` - Returns form layout and field definitions
- `GET /api/form-options` - Returns dropdown/lookup data
- `GET /api/form-config` - Returns combined structure + options
- `GET /healthz` - Health check endpoint

## 📁 Project Structure

```
Smart_Tactics_POC/
├── backend/
│   ├── app.py              # Flask API server
│   ├── database_setup.py   # Database initialization script
│   └── verify_db.py        # Database verification utility
├── data/
│   ├── refactored_code.json # Source form configuration
│   └── form_db.json        # TinyDB database file
├── commands/
│   └── run.txt             # Quick reference commands
├── venv/                   # Python virtual environment
└── README.md               # This file
```

## Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Initialize database from JSON configuration
python backend/database_setup.py
```

### 3. Start Server
```bash
# Run Flask development server
python backend/app.py
```

### 4. Test Endpoints
- Form Structure: http://127.0.0.1:5000/api/form-structure
- Form Options: http://127.0.0.1:5000/api/form-options
- Combined Config: http://127.0.0.1:5000/api/form-config
- Health Check: http://127.0.0.1:5000/healthz

## Form Configuration Features

### Implemented Features

**Field Types:**
- Text fields (`textField`, `textArea`)
- Select dropdowns (`select`)
- Date pickers (`datePicker`)
- Toggle switches (`toggle`)
- Selection cards (`selectionCards`)
- Async search lists (`asyncSearchList`)

**Layout Features:**
- Field grouping for side-by-side layouts
- Grid-based field positioning
- Responsive design considerations
- Section-based organization

**Dynamic Behavior:**
- Conditional field visibility (`isVisible`)
- Field dependencies (`dependsOn`)
- Cascading dropdowns with parent-child relationships
- Dynamic validation rules

**Validation:**
- Required field validation
- Min/max length validation
- Pattern matching
- Custom validation messages

### Form Structure Highlights

**Multi-page Workflow:**
- Page 1: Category selection and tactic type identification
- Page 2-3: Smart tactic creation flow
- Page 4+: Detailed workflow sections (Basic Details, Event Categorization, Location Details, Budget Hierarchy)

**Complex Field Relationships:**
- Event Ring → First/Third Party → Event Category → Event Sub-Category
- Budget Level 1 → Level 2 → Level 3 → Level 4 hierarchy
- Global Campaign → Adapt/Adopt/Invent options

**Field Grouping Examples:**
- Priority + Owner (side-by-side)
- Start Date + End Date (side-by-side)
- Hierarchical budget selection

## Database Operations

### Verify Database
```bash
python backend/verify_db.py
```

### Database Schema
```json
{
  "form_structure": [
    {
      "id": "main_form",
      "data": {
        "pages": [...],
        // Form structure without lookups
      }
    }
  ],
  "form_options": [
    {
      "id": "all_lookups", 
      "data": {
        "categoryOptions": [...],
        "priorityOptions": [...],
        // All dropdown options
      }
    }
  ]
}
```

## 🎨 Dynamic Form Capabilities

### Conditional Logic
- Fields show/hide based on other field values
- Cascading dropdown filtering
- Dynamic validation rule application

### Field Layout Types
- **Single**: Standard single-column layout
- **Row**: Side-by-side field arrangement
- **Cascading**: Parent-child dropdown relationships
- **Grid**: Custom grid positioning

### Validation Features
- Real-time field validation
- Cross-field validation (date comparisons)
- Percentage sum validation for budget fields
- Custom error messaging

## 🌟 Key Achievements

1. **✅ JSON-to-Database Pipeline** - Successfully converts complex form JSON to structured database
2. **✅ API Architecture** - Clean separation of form structure and options data
3. **✅ Dynamic Configuration** - Forms can be modified by updating JSON without code changes
4. **✅ Complex Field Relationships** - Supports cascading dropdowns and conditional visibility
5. **✅ Flexible Layout System** - Handles various field grouping and positioning requirements
6. **✅ Comprehensive Validation** - Rich validation rule system with custom messaging

## Development Workflow

1. **Modify Form**: Update `data/refactored_code.json`
2. **Rebuild Database**: Run `python backend/database_setup.py`
3. **Test Changes**: Use API endpoints to verify updates
4. **Frontend Integration**: Consume APIs to render dynamic forms

## Notes

- **Port Configuration**: Default port 5000 (may conflict with macOS AirPlay)
- **Database**: TinyDB stores data in `data/form_db.json`
- **Environment**: Requires Python virtual environment activation
- **Development**: Flask runs in debug mode for development

---

**Status**: Backend Complete - Ready for Frontend Integration

**Last Updated**: 2025-09-29