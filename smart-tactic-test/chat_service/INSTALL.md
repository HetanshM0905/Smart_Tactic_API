# Installation Guide

## Step-by-Step Package Installation

Due to complex dependency conflicts, install packages individually:

### 1. Core Flask packages
```bash
pip install Flask
pip install flask-cors
pip install flask-limiter
```

### 2. Essential packages
```bash
pip install google-generativeai
pip install tinydb
pip install pydantic
pip install python-dotenv
pip install requests
```

### 3. Langfuse (optional - for LLM monitoring)
```bash
pip install langfuse
```

If Langfuse installation fails, the application will work without it.

## Alternative: Virtual Environment Setup

```bash
# Create fresh virtual environment
python -m venv venv_clean
source venv_clean/bin/activate  # On Windows: venv_clean\Scripts\activate

# Install packages one by one
pip install Flask flask-cors flask-limiter
pip install google-generativeai tinydb pydantic python-dotenv requests
pip install langfuse  # Optional
```

## Running Without Langfuse

If Langfuse installation continues to fail, you can run the application without it:

1. Comment out Langfuse imports temporarily
2. The application will detect missing Langfuse and disable monitoring
3. All core functionality will work normally

## Troubleshooting

- If you get dependency conflicts, try installing in a fresh virtual environment
- Langfuse is optional - the app works without it
- Check Python version compatibility (Python 3.8+ recommended)
