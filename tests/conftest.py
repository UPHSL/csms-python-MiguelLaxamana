import pytest
from flask import Flask
from flask.testing import FlaskClient

from csms import create_app


@pytest.fixture()
def app(tmp_path) -> Flask:
    database_path = tmp_path / "csms-test.sqlite"

    application = create_app({
        "TESTING": True,
        "DEBUG": False,
        "SECRET_KEY": "test-secret-key",
        "DATABASE_PATH": str(database_path),
    })

    yield application


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()