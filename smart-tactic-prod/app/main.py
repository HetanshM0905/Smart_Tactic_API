"""
Main entry point for the Smart Tactics Flask application
"""

import os
from app import create_app
from app.config import get_config

# Get configuration based on environment
config = get_config()
app = create_app(config)

if __name__ == '__main__':
    # For development only
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
