
import re
from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def create_test_resident(app):
    """Create and persist a resident for T15 integration tests."""
    resident = Resident(
        first_name="Miguel",
        last_name="Laxamana",
        address="Biñan City, Laguna",
        contact_number="09123456789",
        email="t15@example.com",
    )

    result = app.extensions["resident_services"][
        "registration"
    ].register_resident(resident)

    assert result.success
    return result.resident


def create_test_request(app, resident_id):
    """Create and persist a pending service request."""
    repository = ServiceRequestRepository(
        app.config["DATABASE_PATH"]
    )

    request = ServiceRequest(
        resident_id=resident_id,
        service_type="Medical Assistance",
        description="T15 hardening test request",
        date_requested=date(2026, 11, 12),
    )

    return repository.save(request)


def get_residents(app):
    return app.extensions["resident_services"][
        "query"
    ].list_residents()


def get_requests(app):
    return app.extensions["service_request_services"][
        "query"
    ].list_service_requests()


def test_malformed_submission_date_returns_400_without_persistence(
    client,
    app,
):
    resident = create_test_resident(app)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Malformed date test",
            "date_requested": "not-a-date",
        },
    )

    assert response.status_code == 400
    assert get_requests(app) == []


def test_rejected_status_mutation_preserves_entire_request(
    client,
    app,
):
    resident = create_test_resident(app)
    service_request = create_test_request(app, resident.id)

    before = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": ""},
    )

    after = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert response.status_code == 302
    assert after == before
    assert after.status == "Pending"


def test_read_only_routes_preserve_resident_and_request_records(
    client,
    app,
):
    resident = create_test_resident(app)
    service_request = create_test_request(app, resident.id)

    def resident_snapshot():
        return [
            (
                record.id,
                record.first_name,
                record.last_name,
                record.address,
                record.contact_number,
                record.email,
                record.status,
            )
            for record in get_residents(app)
        ]

    def request_snapshot():
        return [
            (
                record.id,
                record.resident_id,
                record.service_type,
                record.description,
                record.date_requested,
                record.status,
            )
            for record in get_requests(app)
        ]

    residents_before = resident_snapshot()
    requests_before = request_snapshot()

    urls = [
        "/dashboard",
        "/residents",
        "/residents?q=Miguel",
        "/service-requests",
        "/service-requests?q=Medical",
        f"/service-requests/{service_request.id}",
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, url

    assert resident_snapshot() == residents_before
    assert request_snapshot() == requests_before


def test_deactivation_updates_dashboard_and_blocks_new_requests(
    client,
    app,
):
    resident = create_test_resident(app)

    deactivation_response = client.post(
        f"/residents/{resident.id}/deactivate"
    )

    assert deactivation_response.status_code == 302

    dashboard_response = client.get("/dashboard")

    assert dashboard_response.status_code == 200

    inactive_count = re.search(
        rb"Inactive Residents</span>\s*"
        rb"<strong class=\"dashboard-number\">\s*(\d+)",
        dashboard_response.data,
    )

    active_count = re.search(
        rb"Active Residents</span>\s*"
        rb"<strong class=\"dashboard-number\">\s*(\d+)",
        dashboard_response.data,
    )

    assert inactive_count is not None
    assert active_count is not None
    assert inactive_count.group(1) == b"1"
    assert active_count.group(1) == b"0"

    submission_response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Request from inactive resident",
            "date_requested": "2026-11-12",
        },
    )

    assert submission_response.status_code == 400
    assert get_requests(app) == []


def test_repeating_same_status_transition_preserves_current_record(
    client,
    app,
):
    resident = create_test_resident(app)
    service_request = create_test_request(app, resident.id)

    status_url = (
        f"/service-requests/{service_request.id}/status"
    )

    first_response = client.post(
        status_url,
        data={"target_status": "In Progress"},
    )

    assert first_response.status_code == 302

    query_service = app.extensions["service_request_services"][
        "query"
    ]

    after_first_transition = query_service.get_service_request(
        service_request.id
    )

    assert after_first_transition.status == "In Progress"

    second_response = client.post(
        status_url,
        data={"target_status": "In Progress"},
    )

    after_repeated_transition = query_service.get_service_request(
        service_request.id
    )

    assert second_response.status_code == 302
    assert after_repeated_transition == after_first_transition
    assert after_repeated_transition.status == "In Progress"
