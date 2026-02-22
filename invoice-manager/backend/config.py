"""
Configuration management for the Flask application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///invoices.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gmail API
    GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
    GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_OAUTH_MODE = os.getenv('GMAIL_OAUTH_MODE', 'desktop')  # desktop | web
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    GMAIL_REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/api/accounts/oauth/callback')
    GMAIL_SYNC_MAX_RESULTS = int(os.getenv('GMAIL_SYNC_MAX_RESULTS', 50))
    FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
    
    # Application
    MAX_GMAIL_ACCOUNTS = int(os.getenv('MAX_GMAIL_ACCOUNTS', 2))
    PDF_STORAGE_PATH = os.getenv('PDF_STORAGE_PATH', 'invoices/')
    TEMP_PATH = os.getenv('TEMP_PATH', 'temp/')
    
    # Timezone
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Budapest')
    
    # CORS (for React frontend)
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
