# SmartTactic API

A Flask-based API for managing SmartTactic marketing forms with SQLite database backend.

## Project Structure

```
Smart_Tactic_API/
├── db_setup.py          # Database setup script
├── app.py               # Flask API application
├── test_api.py          # API testing script
├── requirements.txt     # Python dependencies
├── mockdata.json        # Sample data structure
├── smart_tactic.db      # SQLite database (created after setup)
└── README.md            # This file
```

## Features

- **Database Setup**: Creates SQLite database with normalized tables for form data
- **RESTful API**: Full CRUD operations for marketing forms
- **Data Validation**: Input validation and error handling
- **Comprehensive Form Structure**: Supports all fields from the mockdata.json template
- **Testing**: Complete test suite for all API endpoints

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/forms` | Create a new form |
| `GET` | `/api/forms` | List all forms |
| `GET` | `/api/forms/<id>` | Get form details by ID |
| `PUT` | `/api/forms/<id>` | Update an existing form |
| `DELETE` | `/api/forms/<id>` | Delete a form |
| `GET` | `/health` | Health check endpoint |

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

Run the database setup script to create the SQLite database and tables:

```bash
python db_setup.py
```

This will:
- Create a `smart_tactic.db` file
- Set up all necessary tables with proper relationships
- Insert sample data from `mockdata.json`

### 3. Start the API

```bash
python app.py
```

The API will start on `http://localhost:5000`

## Database Schema

The database uses a normalized structure with the following main tables:

- **forms**: Main form information
- **form_basic**: Basic event details
- **form_organization**: Organizational structure
- **form_logistics**: Event logistics and location
- **form_finance**: Financial information
- **form_partners**: Partner involvement details
- **form_alignments**: Target audience and product alignments
- **form_review**: Review status information

## Usage Examples

### Create a New Form

```bash
curl -X POST http://localhost:5000/api/forms \
  -H "Content-Type: application/json" \
  -d '{
    "category": "promote",
    "tactic_type": "Events & Experiences",
    "event_kind": "Single",
    "basic": {
      "event_name": "Marketing Summit 2024",
      "owner_email": "user@example.com"
    }
  }'
```

### Get Form Details

```bash
curl http://localhost:5000/api/forms/1
```

### Update Form

```bash
curl -X PUT http://localhost:5000/api/forms/1 \
  -H "Content-Type: application/json" \
  -d '{
    "category": "build_manage",
    "basic": {
      "event_name": "Updated Event Name"
    }
  }'
```

### Delete Form

```bash
curl -X DELETE http://localhost:5000/api/forms/1
```

## Testing

Run the comprehensive test suite to verify all endpoints:

```bash
python test_api.py
```

The test script will:
1. Check API health
2. Create a test form
3. Retrieve form details
4. List all forms
5. Update the form
6. Delete the form
7. Verify deletion

## Form Data Structure

Forms follow the structure defined in `mockdata.json` with these main sections:

- **Basic**: Event name, description, dates, owner
- **Organization**: Ring, party, category, subcategory
- **Logistics**: Funding, hosting type, location
- **Finance**: Budget, cost centers, spending
- **Partners**: Partner involvement and responsibilities
- **Alignments**: Target segments, industries, products
- **Review**: Status tracking

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Form doesn't exist
- **500 Internal Server Error**: Server-side errors

All errors return JSON responses with descriptive messages.

## Development

### Adding New Fields

To add new fields to forms:

1. Update the database schema in `db_setup.py`
2. Modify the API functions in `app.py`
3. Update the test data in `test_api.py`

### Database Migrations

For production use, consider implementing proper database migrations instead of the current setup script.

## Production Considerations

- Use a production WSGI server (e.g., Gunicorn)
- Implement proper authentication and authorization
- Add rate limiting and request validation
- Use environment variables for configuration
- Implement logging and monitoring
- Consider using PostgreSQL for larger datasets

## Troubleshooting

### Common Issues

1. **Database not found**: Run `python db_setup.py` first
2. **Port already in use**: Change port in `app.py` or kill existing process
3. **Import errors**: Ensure all dependencies are installed

### Debug Mode

The API runs in debug mode by default. For production, set `debug=False` in `app.py`.

## License

This project is for demonstration purposes. Modify as needed for your specific use case.
