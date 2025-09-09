# Smart Tactics AI Backend

A production-ready, scalable Flask application for AI-powered event management with intelligent form generation, fallback processing, and comprehensive monitoring.

## 🚀 Features

- **AI-Powered Event Processing**: Uses Gemini Pro for intelligent form field generation and data correction
- **Modular Architecture**: Clean separation of concerns with services, integrations, and utilities
- **Dual Database Support**: Firestore for unstructured data, AlloyDB for structured metadata
- **Intelligent Fallback**: Automatic error recovery and data correction
- **Autofill Engine**: Rule-based and AI-powered form field population
- **Comprehensive Monitoring**: Langfuse tracing, Google Cloud Logging, and performance metrics
- **Production Ready**: Docker containerization, Gunicorn WSGI server, and Cloud Run deployment

## 📁 Project Structure

```
smart_tactic_backend/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── main.py                     # Application entry point
│   ├── config.py                   # Configuration management
│   ├── routes/                     # API route definitions
│   │   ├── __init__.py
│   │   └── event_routes.py
│   ├── services/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── event_handler.py
│   │   ├── fallback_engine.py
│   │   ├── autofill_engine.py
│   │   └── orchestrator.py
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   └── event_model.py
│   ├── integrations/               # External service integrations
│   │   ├── __init__.py
│   │   ├── firestore_client.py
│   │   ├── sql_client.py
│   │   ├── gemini_llm.py
│   │   └── langfuse_logger.py
│   └── utils/                      # Utilities and helpers
│       ├── __init__.py
│       ├── validators.py
│       ├── logger.py
│       └── config_loader.py
├── Dockerfile                      # Container configuration
├── requirements.txt                # Python dependencies
├── gunicorn_config.py              # Production WSGI configuration
├── env.example                     # Environment variables template
├── .dockerignore                   # Docker ignore patterns
├── .gitignore                      # Git ignore patterns
└── README.md                       # This file
```

## 🛠 Installation

### Prerequisites

- Python 3.11+
- Google Cloud Platform account
- Gemini API key
- AlloyDB instance (optional)
- Firestore database

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-tactic-prod
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app/main.py
   ```

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t smart-tactics-backend .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 --env-file .env smart-tactics-backend
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Required |
| `GEMINI_API_KEY` | Gemini API key | Required |
| `ALLOYDB_HOST` | AlloyDB host | Optional |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | Optional |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | Optional |

See `env.example` for complete configuration options.

### Google Cloud Setup

1. **Enable APIs**
   ```bash
   gcloud services enable firestore.googleapis.com
   gcloud services enable alloydb.googleapis.com
   gcloud services enable logging.googleapis.com
   ```

2. **Create service account**
   ```bash
   gcloud iam service-accounts create smart-tactics-backend
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:smart-tactics-backend@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/firestore.user"
   ```

3. **Download credentials**
   ```bash
   gcloud iam service-accounts keys create service-account.json \
     --iam-account=smart-tactics-backend@PROJECT_ID.iam.gserviceaccount.com
   ```

## 🚀 Deployment

### Google Cloud Run

1. **Build and push image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/smart-tactics-backend
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy smart-tactics-backend \
     --image gcr.io/PROJECT_ID/smart-tactics-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="FLASK_ENV=production"
   ```

### Kubernetes

1. **Create deployment**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: smart-tactics-backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: smart-tactics-backend
     template:
       metadata:
         labels:
           app: smart-tactics-backend
       spec:
         containers:
         - name: smart-tactics-backend
           image: gcr.io/PROJECT_ID/smart-tactics-backend
           ports:
           - containerPort: 8080
           env:
           - name: FLASK_ENV
             value: "production"
   ```

## 📚 API Documentation

### Endpoints

#### Health Check
```http
GET /ping
```

#### Create Event
```http
POST /api/events/create
Content-Type: application/json

{
  "title": "AI Conference 2024",
  "event_type": "conference",
  "description": "Annual AI conference",
  "date": "2024-06-15T09:00:00Z",
  "capacity": 500
}
```

#### Update Event
```http
PUT /api/events/update/{event_id}
Content-Type: application/json

{
  "title": "Updated AI Conference 2024",
  "capacity": 600
}
```

#### Update Layout
```http
POST /api/events/layout/update
Content-Type: application/json

{
  "event_id": "event-123",
  "layout_requirements": {
    "sections": 3,
    "theme": "modern"
  }
}
```

#### Trigger Fallback
```http
POST /api/events/fallback/trigger
Content-Type: application/json

{
  "title": "Incomplete Event",
  "event_type": "workshop"
}
```

### Response Format

```json
{
  "success": true,
  "event_id": "event-123",
  "form_fields": {
    "fields": [
      {
        "name": "name",
        "type": "text",
        "label": "Full Name",
        "required": true
      }
    ]
  },
  "autofill_applied": true
}
```

## 🔍 Monitoring

### Logging

The application uses structured JSON logging with the following loggers:

- `app`: Application logs
- `performance`: Performance metrics
- `business`: Business events
- `security`: Security events
- `llm`: LLM interactions
- `database`: Database operations
- `api`: API calls

### Tracing

Langfuse integration provides:

- LLM call tracing
- Performance monitoring
- Error tracking
- Request/response logging

### Health Checks

- `/ping`: Basic health check
- Database connectivity
- External service availability

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Coverage
```bash
pytest --cov=app tests/
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8080
```

## 🔒 Security

### Security Features

- Input validation and sanitization
- CORS configuration
- Rate limiting
- Secure headers
- Non-root container user
- Secret management

### Best Practices

- Use environment variables for secrets
- Enable HTTPS in production
- Regular dependency updates
- Security scanning
- Access logging

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check credentials and network connectivity
   - Verify service account permissions

2. **LLM API Errors**
   - Verify API key and quota
   - Check request format and size

3. **Memory Issues**
   - Monitor worker memory usage
   - Adjust Gunicorn worker settings

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export FLASK_ENV=development
```

## 📈 Performance

### Optimization Tips

- Use connection pooling for databases
- Enable response caching
- Optimize LLM prompts
- Monitor memory usage
- Use CDN for static assets

### Scaling

- Horizontal scaling with multiple workers
- Database read replicas
- Load balancing
- Caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 app/
black app/

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Core event management functionality
- AI-powered form generation
- Fallback and autofill engines
- Comprehensive monitoring
- Production deployment support
