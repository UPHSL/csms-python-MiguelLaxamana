"""Shared pytest fixtures for the CSMS application."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from csms import create_app
from src.csms.database import initialize_database


@pytest.fixture()
def app() -> Flask:
    """Create a configured application for testing."""
    application = create_app(
        {
            "TESTING": True,
            "DEBUG": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    # Initialize database tables for the test application
    with application.app_context():
        initialize_database()

    yield application


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Create a Flask test client."""
    return app.test_client()