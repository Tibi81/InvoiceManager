"""
Flask extensions - initialized without app to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
