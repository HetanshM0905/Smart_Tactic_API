# Chat Service - Scalable AI Chat API

A scalable, production-ready AI chat service built with Flask, featuring form assistance capabilities powered by Google's Gemini AI.

## 🏗️ Architecture

The application follows a clean, layered architecture with proper separation of concerns:

```
chat_service/
├── models/                 # Data models and schemas
├── repositories/          # Data access layer
├── services/             # Business logic layer
├── utils/               # Utilities (logging, etc.)
├── config.py           # Configuration management
├── exceptions.py       # Custom exceptions
├── dependency_injection.py # DI container
├── chatbot_api.py     # API endpoints
└── app.py            # Application factory
```

## ✨ Features

- **Scalable Architecture**: Clean separation of concerns with dependency injection
- **Input Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Logging**: Structured logging with configurable levels
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **CORS Support**: Configurable CORS for cross-origin requests
- **Configuration Management**: Environment-based configuration
- **Database Abstraction**: Repository pattern for data access
- **Async Support**: Async version of services for better performance
- **Health Checks**: Built-in health check endpoint

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository and navigate to the chat service:
```bash
cd chat_service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python app.py
```

The service will start on `http://localhost:5001`

## 🔧 Configuration

Configure the application using environment variables:

### Required Variables
- `GEMINI_API_KEY`: Your Google Gemini API key

### Optional Variables
- `DB_PATH`: Database file path (default: smart_tactic_tinydb.json)
- `PORT`: Server port (default: 5001)
- `HOST`: Server host (default: 0.0.0.0)
- `LOG_LEVEL`: Logging level (default: INFO)
- `RATE_LIMIT_PER_MINUTE`: Rate limit per minute (default: 60)

See `.env.example` for all available configuration options.

## 📡 API Endpoints

### POST /api/ai-chat
Process a chat request with AI assistance.

**Request Body:**
```json
{
  "session_id": "user123",
  "question": "What is the event name?",
  "workflow_id": "workflow1"
}
```

**Response:**
```json
{
  "response": "I can help with that. Based on the information I have, the event is named 'Innovate AI Summit 2024'. Is that correct?",
  "field_data": {
    "f1": "Innovate AI Summit 2024"
  },
  "suggested_buttons": [
    {
      "title": "Yes, that's correct",
      "action": "confirm",
      "id": "f1"
    },
    {
      "title": "No, I want to change it",
      "action": "chat",
      "id": "chat1"
    }
  ],
  "session_id": "user123"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "chat_service"
}
```

## 🏛️ Architecture Components

### Models
- **Pydantic models** for request/response validation
- **Type safety** with proper data validation
- **Enum support** for action types

### Repositories
- **Abstract base classes** for repository interfaces
- **TinyDB implementation** with proper error handling
- **Easy to extend** for other database systems

### Services
- **Business logic separation** from API layer
- **Dependency injection** for loose coupling
- **Async support** for better performance

### Configuration
- **Environment-based** configuration
- **Type-safe** configuration classes
- **Validation** of required settings

## 🔒 Security Features

- **Rate limiting** to prevent abuse
- **Input validation** to prevent injection attacks
- **Error handling** that doesn't leak sensitive information
- **CORS configuration** for secure cross-origin requests

## 📊 Monitoring & Logging

- **Structured logging** with timestamps and context
- **Configurable log levels** (DEBUG, INFO, WARNING, ERROR)
- **Request/response logging** for debugging
- **Error tracking** with proper exception handling

## 🚀 Performance Features

- **Async support** for I/O-bound operations
- **Connection pooling** ready architecture
- **Caching** ready with repository pattern
- **Rate limiting** to manage load

## 🐳 Docker Support

Create a `Dockerfile` for containerization:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "app.py"]
```

## 🧪 Testing

The architecture supports easy testing with:
- **Mock services** for unit testing
- **Repository mocks** for database testing
- **Dependency injection** for test isolation

## 📈 Scaling Considerations

### Horizontal Scaling
- **Stateless design** allows multiple instances
- **Database abstraction** supports distributed databases
- **Configuration management** supports different environments

### Performance Optimization
- **Async services** for I/O-bound operations
- **Connection pooling** ready
- **Caching layer** can be added at repository level

### Monitoring
- **Health checks** for load balancer integration
- **Structured logging** for centralized log management
- **Error tracking** with proper exception handling

## 🔄 Migration from Legacy Code

The new architecture maintains API compatibility while providing:
- **Better error handling**
- **Input validation**
- **Proper logging**
- **Configuration management**
- **Scalable structure**

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add proper error handling and logging
3. Include input validation for new endpoints
4. Update documentation for new features
5. Add tests for new functionality

## 📝 License

This project is part of the Smart Tactic API suite.
