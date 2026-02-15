"""
Invoice Manager - Flask Backend
Main application entry point.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
import os

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Create necessary directories
    os.makedirs(app.config['PDF_STORAGE_PATH'], exist_ok=True)
    os.makedirs(app.config['TEMP_PATH'], exist_ok=True)
    
    # Register blueprints (will add these later)
    # from api.invoices import invoices_bp
    # from api.accounts import accounts_bp
    # from api.recurring import recurring_bp
    # app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    # app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
    # app.register_blueprint(recurring_bp, url_prefix='/api/recurring')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "version": "0.1.0-dev"
        })
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            "message": "Invoice Manager API",
            "version": "0.1.0-dev",
            "endpoints": {
                "health": "/health",
                "invoices": "/api/invoices",
                "accounts": "/api/accounts",
                "recurring": "/api/recurring"
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "data": None,
            "error": "Resource not found"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "data": None,
            "error": "Internal server error"
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # Run the application
    print("🚀 Starting Invoice Manager API...")
    print(f"📍 Running on http://localhost:5000")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
