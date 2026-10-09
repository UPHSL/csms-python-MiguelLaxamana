from datetime import date

import pytest

from src.csms.database import get_connection, initialize_database
from src.csms.models.resident import Resident
from src.csms.models.service_request import ServiceRequest
from src.csms.repositories.resident_repository import ResidentRepository
from src.csms.repositories.service_request_repository import ServiceRequestRepository
from src.csms.services.service_request_status_service import (
    ServiceRequestStatusService,
)


@pytest.fixture
def repositories(tmp_path, monkeypatch):
    database_path = tmp_path / "test_csms.db"

    monkeypatch.setattr(
        "src.csms.repositories.resident_repository.get_connection",
        lambda: get_connection(database_path),
    )
    monkeypatch.setattr(
        "src.csms.repositories.service_request_repository.get_connection",
        lambda: get_connection(database_path),
    )

    initialize_database(database_path)

    with get_connection(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        print("Test database tables:", [row["name"] for row in tables])

    resident_repository = ResidentRepository()
    resident = resident_repository.save(
        Resident(
            first_name="Test",
            last_name="Resident",
            address="Biñan",
            contact_number="09123456789",
            email="test@example.com",
            status="Active",
        )
    )

    request_repository = ServiceRequestRepository()
    request = request_repository.save(
        ServiceRequest(
            resident_id=resident.id,
            service_type="Barangay Clearance",
            description="Test request",
            date_requested=date(2026, 6, 1),
        )
    )

    return resident_repository, request_repository, request


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        ("Pending", "In Progress"),
        ("Pending", "Cancelled"),
        ("In Progress", "Completed"),
        ("In Progress", "Cancelled"),
    ],
)
def test_allowed_status_transitions_succeed(
    repositories, current_status, target_status
):
    _, repository, request = repositories
    repository.update_status(request.id, current_status)

    service = ServiceRequestStatusService(repository)
    result = service.update_status(request.id, target_status)

    assert result.success is True
    assert result.service_request.status == target_status


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        ("Pending", "Completed"),
        ("In Progress", "Pending"),
        ("Completed", "Cancelled"),
        ("Cancelled", "In Progress"),
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
    ],
)
def test_invalid_status_transitions_do_not_change_status(
    repositories, current_status, target_status
):
    _, repository, request = repositories
    repository.update_status(request.id, current_status)

    service = ServiceRequestStatusService(repository)
    result = service.update_status(request.id, target_status)

    assert result.success is False
    persisted = repository.find_by_id(request.id)
    assert persisted.status == current_status


def test_unsupported_target_status_does_not_change_status(repositories):
    _, repository, request = repositories
    service = ServiceRequestStatusService(repository)

    result = service.update_status(request.id, "Approved")

    assert result.success is False
    assert result.error_message == "Unsupported target status"
    assert repository.find_by_id(request.id).status == "Pending"


def test_missing_request_returns_not_found(repositories):
    _, repository, _ = repositories
    service = ServiceRequestStatusService(repository)

    result = service.update_status(999999, "In Progress")

    assert result.success is False
    assert result.error_message == "Service request not found"


def test_valid_transition_preserves_other_request_fields(repositories):
    _, repository, request = repositories
    service = ServiceRequestStatusService(repository)

    result = service.update_status(request.id, "In Progress")

    assert result.success is True
    updated = repository.find_by_id(request.id)
    assert updated.id == request.id
    assert updated.resident_id == request.resident_id
    assert updated.service_type == request.service_type
    assert updated.description == request.description
    assert updated.date_requested == request.date_requested
    assert updated.status == "In Progress"


def test_existing_request_can_be_updated_after_resident_is_deactivated(
    repositories,
):
    resident_repository, request_repository, request = repositories
    resident = resident_repository.find_by_id(request.resident_id)
    resident.status = "Inactive"
    resident_repository.update(resident)

    service = ServiceRequestStatusService(request_repository)
    result = service.update_status(request.id, "In Progress")

    assert result.success is True
    assert result.service_request.status == "In Progress"