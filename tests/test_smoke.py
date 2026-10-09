"""Smoke tests for the Sprint 0 Flask application."""
from flask.testing import FlaskClient
from src.csms.models.resident import Resident


def test_home_page_is_available(client: FlaskClient) -> None:
    """The home page should load successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Community Services Management System" in response.data
    assert b"Sprint 0 - Developer Onboarding" in response.data
    assert b"Python with Flask" in response.data


def test_health_endpoint_returns_ok(client: FlaskClient) -> None:
    """The health endpoint should report an operational application."""
    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"


def test_unknown_page_returns_not_found(client: FlaskClient) -> None:
    """An unknown route should return HTTP 404."""
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_resident_can_be_created_with_required_information():
    resident = Resident(
        id=1,
        first_name="Juan",
        last_name="Dela Cruz",
        address="Barangay Santo Tomas",
        contact_number="09171234567",
        email="juan@example.com",
        status="Active",
    )

    assert resident.id == 1
    assert resident.first_name == "Juan"
    assert resident.last_name == "Dela Cruz"
    assert resident.address == "Barangay Santo Tomas"
    assert resident.contact_number == "09171234567"
    assert resident.email == "juan@example.com"
    assert resident.status == "Active"


def test_resident_information_can_be_accessed_and_updated():
    resident = Resident(
        first_name="Maria",
        last_name="Santos",
        address="Barangay Santo Tomas",
        contact_number="09181234567",
        email="maria@example.com",
    )

    resident.contact_number = "09991234567"
    resident.email = "maria.santos@example.com"

    assert resident.first_name == "Maria"
    assert resident.last_name == "Santos"
    assert resident.address == "Barangay Santo Tomas"
    assert resident.contact_number == "09991234567"
    assert resident.email == "maria.santos@example.com"


def test_resident_defaults_to_active_status():
    resident = Resident(
        first_name="Pedro",
        last_name="Reyes",
        address="Barangay Santo Tomas",
        contact_number="09191234567",
        email="pedro@example.com",
    )

    assert resident.status == "Active"


def test_resident_defaults_to_none_id_before_persistence():
    resident = Resident(
        first_name="Ana",
        last_name="Cruz",
        address="Barangay Santo Tomas",
        contact_number="09171230000",
        email="ana@example.com",
    )

    assert resident.id is None