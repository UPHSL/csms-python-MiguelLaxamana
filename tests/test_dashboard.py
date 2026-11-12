
from datetime import date

import pytest

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.services.service_request_status_service import (
    ServiceRequestStatusService,
)


@pytest.fixture
def dashboard_repositories(app):
    dashboard_service = app.extensions["dashboard_service"]

    return (
        dashboard_service.resident_repository,
        dashboard_service.service_request_repository,
    )


def create_resident(
    repository,
    first_name="Juan",
    last_name="Cruz",
    status="Active",
):
    return repository.save(
        Resident(
            first_name=first_name,
            last_name=last_name,
            address="Barangay Santo Tomas",
            contact_number="09171234567",
            email=f"{first_name.lower()}@example.com",
            status=status,
        )
    )


def create_request(
    repository,
    resident_id,
    service_type="Medical Assistance",
    request_date=date(2026, 6, 1),
    status="Pending",
):
    request = repository.save(
        ServiceRequest(
            resident_id=resident_id,
            service_type=service_type,
            description="Dashboard test request",
            date_requested=request_date,
        )
    )

    if status != "Pending":
        repository.update_status(request.id, status)

    return request


# ---------------------------------------------------------
# Dashboard loading and empty-state tests
# ---------------------------------------------------------


def test_dashboard_page_loads_successfully(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_dashboard_displays_resident_statistics(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Total Residents" in response.data
    assert b"Active Residents" in response.data
    assert b"Inactive Residents" in response.data


def test_dashboard_displays_service_request_statistics(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Total Requests" in response.data
    assert b"Pending" in response.data
    assert b"In Progress" in response.data
    assert b"Completed" in response.data
    assert b"Cancelled" in response.data


def test_dashboard_displays_zero_counts_when_database_is_empty(
    client,
):
    response = client.get("/dashboard")

    assert response.status_code == 200

    dashboard_text = response.get_data(as_text=True)

    assert "Total Residents" in dashboard_text
    assert "Total Requests" in dashboard_text
    assert "No service requests have been submitted yet." in dashboard_text


# ---------------------------------------------------------
# Resident statistics tests
# ---------------------------------------------------------


def test_dashboard_counts_all_residents(dashboard_repositories, client):
    resident_repository, _ = dashboard_repositories

    create_resident(resident_repository, "Juan")
    create_resident(resident_repository, "Maria")
    create_resident(
        resident_repository,
        "Pedro",
        status="Inactive",
    )

    response = client.get("/dashboard")
    dashboard_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Total Residents" in dashboard_text


def test_dashboard_counts_active_residents(
    dashboard_repositories,
    client,
):
    resident_repository, _ = dashboard_repositories

    create_resident(resident_repository, "Juan")
    create_resident(resident_repository, "Maria")
    create_resident(
        resident_repository,
        "Pedro",
        status="Inactive",
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"2" in response.data


def test_dashboard_counts_inactive_residents(
    dashboard_repositories,
    client,
):
    resident_repository, _ = dashboard_repositories

    create_resident(
        resident_repository,
        "Juan",
        status="Inactive",
    )
    create_resident(
        resident_repository,
        "Maria",
        status="Inactive",
    )
    create_resident(resident_repository, "Pedro")

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"2" in response.data


def test_resident_total_equals_active_plus_inactive(
    dashboard_repositories,
):
    resident_repository, _ = dashboard_repositories

    create_resident(resident_repository, "Juan")
    create_resident(resident_repository, "Maria")
    create_resident(
        resident_repository,
        "Pedro",
        status="Inactive",
    )

    counts = resident_repository.get_dashboard_counts()

    assert counts["total"] == (
        counts["active"] + counts["inactive"]
    )


def test_deactivated_resident_is_counted_as_inactive(
    dashboard_repositories,
):
    resident_repository, _ = dashboard_repositories

    resident = create_resident(resident_repository)

    resident.status = "Inactive"
    resident_repository.update(resident)

    counts = resident_repository.get_dashboard_counts()

    assert counts["total"] == 1
    assert counts["active"] == 0
    assert counts["inactive"] == 1


# ---------------------------------------------------------
# Service request statistics tests
# ---------------------------------------------------------


def test_dashboard_counts_all_service_request_statuses(
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(
        request_repository,
        resident.id,
        status="Pending",
    )
    create_request(
        request_repository,
        resident.id,
        status="In Progress",
    )
    create_request(
        request_repository,
        resident.id,
        status="Completed",
    )
    create_request(
        request_repository,
        resident.id,
        status="Cancelled",
    )

    counts = request_repository.get_dashboard_counts()

    assert counts["total"] == 4
    assert counts["pending"] == 1
    assert counts["in_progress"] == 1
    assert counts["completed"] == 1
    assert counts["cancelled"] == 1


def test_service_request_total_equals_status_counts(
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(request_repository, resident.id)
    create_request(
        request_repository,
        resident.id,
        status="In Progress",
    )
    create_request(
        request_repository,
        resident.id,
        status="Completed",
    )
    create_request(
        request_repository,
        resident.id,
        status="Cancelled",
    )

    counts = request_repository.get_dashboard_counts()

    status_total = (
        counts["pending"]
        + counts["in_progress"]
        + counts["completed"]
        + counts["cancelled"]
    )

    assert counts["total"] == status_total


def test_open_requests_equals_pending_plus_in_progress(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(request_repository, resident.id)
    create_request(request_repository, resident.id)
    create_request(
        request_repository,
        resident.id,
        status="In Progress",
    )
    create_request(
        request_repository,
        resident.id,
        status="Completed",
    )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["open_requests"] == 3
    assert data["open_requests"] == (
        data["request_counts"]["pending"]
        + data["request_counts"]["in_progress"]
    )


def test_completed_and_cancelled_requests_are_not_open(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(
        request_repository,
        resident.id,
        status="Completed",
    )
    create_request(
        request_repository,
        resident.id,
        status="Cancelled",
    )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["open_requests"] == 0


# ---------------------------------------------------------
# Recent service request tests
# ---------------------------------------------------------


def test_recent_requests_are_limited_to_five(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    for day in range(1, 8):
        create_request(
            request_repository,
            resident.id,
            service_type=f"Service {day}",
            request_date=date(2026, 6, day),
        )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert len(data["recent_requests"]) == 5


def test_recent_requests_are_ordered_by_date_descending(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(
        request_repository,
        resident.id,
        service_type="Older Request",
        request_date=date(2026, 6, 1),
    )
    create_request(
        request_repository,
        resident.id,
        service_type="Newer Request",
        request_date=date(2026, 6, 10),
    )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["recent_requests"][0].service_type == "Newer Request"
    assert data["recent_requests"][1].service_type == "Older Request"


def test_recent_requests_use_id_descending_when_dates_are_equal(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)
    request_date = date(2026, 6, 1)

    first = create_request(
        request_repository,
        resident.id,
        service_type="First Request",
        request_date=request_date,
    )
    second = create_request(
        request_repository,
        resident.id,
        service_type="Second Request",
        request_date=request_date,
    )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["recent_requests"][0].id == second.id
    assert data["recent_requests"][1].id == first.id


def test_recent_requests_include_terminal_statuses(
    app,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    create_request(
        request_repository,
        resident.id,
        service_type="Completed Request",
        status="Completed",
    )
    create_request(
        request_repository,
        resident.id,
        service_type="Cancelled Request",
        status="Cancelled",
    )

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    statuses = {
        request.status
        for request in data["recent_requests"]
    }

    assert "Completed" in statuses
    assert "Cancelled" in statuses


def test_recent_requests_have_working_detail_links(
    client,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    request = create_request(
        request_repository,
        resident.id,
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert (
        f'/service-requests/{request.id}'
        in response.get_data(as_text=True)
    )

    detail_response = client.get(
        f"/service-requests/{request.id}"
    )

    assert detail_response.status_code == 200


# ---------------------------------------------------------
# Status transition and read-only tests
# ---------------------------------------------------------


@pytest.mark.parametrize(
    ("initial_status", "target_status", "expected_open"),
    [
        ("Pending", "In Progress", 1),
        ("In Progress", "Completed", 0),
        ("Pending", "Cancelled", 0),
    ],
)
def test_dashboard_reflects_valid_status_transitions(
    app,
    dashboard_repositories,
    initial_status,
    target_status,
    expected_open,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    request = create_request(
        request_repository,
        resident.id,
        status=initial_status,
    )

    status_service = ServiceRequestStatusService(request_repository)

    result = status_service.update_status(
        request.id,
        target_status,
    )

    assert result.success is True

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["open_requests"] == expected_open
    assert data["request_counts"][target_status.lower().replace(" ", "_")] == 1


@pytest.mark.parametrize(
    "terminal_status",
    ["Completed", "Cancelled"],
)
def test_terminal_status_requests_remain_terminal(
    app,
    dashboard_repositories,
    terminal_status,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    request = create_request(
        request_repository,
        resident.id,
        status=terminal_status,
    )

    status_service = ServiceRequestStatusService(request_repository)

    result = status_service.update_status(
        request.id,
        "In Progress",
    )

    assert result.success is False
    assert request_repository.find_by_id(request.id).status == terminal_status

    dashboard_service = app.extensions["dashboard_service"]
    data = dashboard_service.get_dashboard_data()

    assert data["open_requests"] == 0
    assert data["request_counts"][
        terminal_status.lower()
    ] == 1


def test_dashboard_get_request_does_not_modify_database(
    client,
    dashboard_repositories,
):
    resident_repository, request_repository = dashboard_repositories

    resident = create_resident(resident_repository)

    request = create_request(
        request_repository,
        resident.id,
    )

    residents_before = resident_repository.get_dashboard_counts()
    requests_before = request_repository.get_dashboard_counts()
    stored_request_before = request_repository.find_by_id(request.id)

    response = client.get("/dashboard")

    residents_after = resident_repository.get_dashboard_counts()
    requests_after = request_repository.get_dashboard_counts()
    stored_request_after = request_repository.find_by_id(request.id)

    assert response.status_code == 200
    assert residents_after == residents_before
    assert requests_after == requests_before
    assert stored_request_after.status == stored_request_before.status
