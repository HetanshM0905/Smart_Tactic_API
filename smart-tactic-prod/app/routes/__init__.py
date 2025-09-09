"""
Route blueprints registration
"""

from flask import Blueprint
from .event_routes import event_bp

def register_blueprints(app):
    """Register all application blueprints"""
    
    # API routes
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api_bp.register_blueprint(event_bp, url_prefix='/events')
    
    # Health check route
    @app.route('/ping')
    def health_check():
        return {'status': 'healthy', 'service': 'smart-tactics-backend'}, 200
    
    app.register_blueprint(api_bp)
