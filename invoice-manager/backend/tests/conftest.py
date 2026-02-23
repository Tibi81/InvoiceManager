"""Shared pytest fixtures for backend API tests."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as app_module
from extensions import db
from services.recurring_scheduler import reset_recurring_run_status


@pytest.fixture()
def app(tmp_path: Path):
    """Create an isolated app instance with in-memory database."""

    class TestConfig:
        DEBUG = False
        TESTING = True
        SECRET_KEY = "test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        CORS_ORIGINS = ["http://localhost:5173"]
        PDF_STORAGE_PATH = str(tmp_path / "invoices")
        TEMP_PATH = str(tmp_path / "temp")
        GMAIL_CLIENT_ID = None
        GMAIL_CLIENT_SECRET = None
        GMAIL_OAUTH_MODE = "desktop"
        GMAIL_SCOPES = []
        GMAIL_REDIRECT_URI = "http://localhost:5000/api/accounts/oauth/callback"
        GMAIL_SYNC_MAX_RESULTS = 50
        FRONTEND_BASE_URL = "http://localhost:5173"
        MAX_GMAIL_ACCOUNTS = 2
        TIMEZONE = "Europe/Budapest"
        RECURRING_SCHEDULER_ENABLED = False
        RECURRING_SCHEDULER_INTERVAL_SECONDS = 300

    app_module.config["test"] = TestConfig
    test_app = app_module.create_app("test")

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_recurring_state():
    """Keep recurring run-state isolated between tests."""
    reset_recurring_run_status()
    yield
    reset_recurring_run_status()
