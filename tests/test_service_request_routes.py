
from datetime import date

import pytest

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


RESIDENT_DATA = {
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "address": "Biñan City, Laguna",
    "contact_number": "09123456789",
    "email": "juan@example.com",
}


def create_resident(app, data=None):
    """Create a resident using the registered service."""
    resident_data = data or RESIDENT_DATA

    resident = Resident(**resident_data)

    result = app.extensions["resident_services"][
        "registration"
    ].register_resident(resident)

    assert result.success
    return result.resident


def create_request(
    app,
    resident_id,
    service_type="Barangay Clearance",
    description="Request for barangay clearance",
    requested_date=date(2026, 11, 10),
    status="Pending",
):
    """Create a persisted Service Request for route tests."""
    repository = ServiceRequestRepository(
        app.config["DATABASE_PATH"]
    )

    service_request = ServiceRequest(
        resident_id=resident_id,
        service_type=service_type,
        description=description,
        date_requested=requested_date,
    )

    saved_request = repository.save(service_request)

    if status != "Pending":
        result = app.extensions["service_request_services"][
            "status"
        ].update_status(saved_request.id, "In Progress")

        assert result.success

        if status in {"Completed", "Cancelled"}:
            result = app.extensions["service_request_services"][
                "status"
            ].update_status(saved_request.id, status)

            assert result.success

    return saved_request


def test_service_request_list_page_loads(client):
    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"Service Request Management" in response.data


def test_service_request_list_displays_saved_requests(client, app):
    resident = create_resident(app)
    create_request(app, resident.id)

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"Barangay Clearance" in response.data
    assert b"Request for barangay clearance" not in response.data


def test_service_request_list_shows_empty_state(client):
    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"No service requests available yet." in response.data


def test_service_request_search_matches_service_type(client, app):
    resident = create_resident(app)
    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
    )

    response = client.get(
        "/service-requests?q=Medical"
    )

    assert response.status_code == 200
    assert b"Medical Assistance" in response.data


def test_service_request_search_matches_description(client, app):
    resident = create_resident(app)
    create_request(
        app,
        resident.id,
        service_type="General Assistance",
        description="Request for emergency medical support",
    )

    response = client.get(
        "/service-requests?q=emergency"
    )

    assert response.status_code == 200
    assert b"General Assistance" in response.data


def test_service_request_search_is_case_insensitive(client, app):
    resident = create_resident(app)
    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
    )

    response = client.get(
        "/service-requests?q=MEDICAL"
    )

    assert response.status_code == 200
    assert b"Medical Assistance" in response.data


def test_service_request_list_filters_by_status(client, app):
    resident = create_resident(app)
    create_request(app, resident.id, status="Pending")
    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
        status="In Progress",
    )

    response = client.get(
        "/service-requests?status=In+Progress"
    )

    assert response.status_code == 200
    assert b"Medical Assistance" in response.data
    assert b"Barangay Clearance" not in response.data


def test_service_request_list_combines_search_and_status(client, app):
    resident = create_resident(app)

    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
        status="Pending",
    )

    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
        description="Another medical request",
        status="Completed",
    )

    response = client.get(
        "/service-requests?q=Medical&status=Pending"
    )

    assert response.status_code == 200
    assert b"Medical Assistance" in response.data
    assert b"Another medical request" not in response.data


def test_service_request_list_preserves_search_and_status(client, app):
    resident = create_resident(app)
    create_request(app, resident.id)

    response = client.get(
        "/service-requests?q=Clearance&status=Pending"
    )

    assert response.status_code == 200
    assert b'value="Clearance"' in response.data
    assert b'value="Pending" selected' in response.data


def test_service_request_list_rejects_unsupported_status(client):
    response = client.get(
        "/service-requests?status=Unknown"
    )

    assert response.status_code == 400


def test_new_service_request_form_loads(client):
    response = client.get("/service-requests/new")

    assert response.status_code == 200
    assert b"Submit Service Request" in response.data


def test_new_service_request_form_has_no_id_or_status_fields(client):
    response = client.get("/service-requests/new")

    assert response.status_code == 200
    assert b'name="resident_id"' in response.data
    assert b'name="service_type"' in response.data
    assert b'name="description"' in response.data
    assert b'name="date_requested"' in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data


def test_valid_submission_redirects_to_detail(client, app):
    resident = create_resident(app)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    assert response.status_code == 302
    assert "/service-requests/" in response.headers["Location"]

    detail_response = client.get(response.headers["Location"])

    assert detail_response.status_code == 200
    assert b"Medical Assistance" in detail_response.data


def test_valid_submission_creates_pending_request(client, app):
    resident = create_resident(app)

    client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    records = app.extensions["service_request_services"][
        "query"
    ].list_service_requests()

    assert len(records) == 1
    assert records[0].status == "Pending"


def test_submission_rejects_invalid_resident_id(client):
    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": "invalid",
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    assert response.status_code == 400
    assert b"valid Resident ID" in response.data


def test_submission_rejects_missing_resident(client):
    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": "9999",
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    assert response.status_code == 400
    assert b"Resident not found" in response.data


def test_submission_rejects_inactive_resident(client, app):
    resident = create_resident(app)

    result = app.extensions["resident_services"][
        "deactivation"
    ].deactivate_resident(resident.id)

    assert result.success

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    assert response.status_code == 400
    assert b"Inactive" in response.data


def test_submission_validation_errors_preserve_form_data(client, app):
    resident = create_resident(app)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "",
            "description": "Request for medical support",
            "date_requested": "2026-11-11",
        },
    )

    assert response.status_code == 400
    assert b"Service type is required" in response.data
    assert b"Request for medical support" in response.data


def test_service_request_detail_displays_request(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.get(
        f"/service-requests/{service_request.id}"
    )

    assert response.status_code == 200
    assert b"Barangay Clearance" in response.data
    assert b"Request for barangay clearance" in response.data
    assert b"Pending" in response.data


def test_missing_service_request_detail_returns_404(client):
    response = client.get("/service-requests/9999")

    assert response.status_code == 404


def test_pending_request_can_be_started(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "In Progress"},
    )

    assert response.status_code == 302

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == "In Progress"


def test_pending_request_can_be_cancelled(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "Cancelled"},
    )

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == "Cancelled"


def test_in_progress_request_can_be_completed(client, app):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status="In Progress",
    )

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "Completed"},
    )

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == "Completed"


def test_in_progress_request_can_be_cancelled(client, app):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status="In Progress",
    )

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "Cancelled"},
    )

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == "Cancelled"


@pytest.mark.parametrize(
    ("initial_status", "target_status"),
    [
        ("Pending", "Completed"),
        ("Completed", "Pending"),
        ("Completed", "Cancelled"),
        ("Cancelled", "In Progress"),
        ("Cancelled", "Completed"),
    ],
)
def test_invalid_status_transitions_do_not_change_status(
    client,
    app,
    initial_status,
    target_status,
):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status=initial_status,
    )

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": target_status},
    )

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == initial_status


def test_unsupported_status_target_does_not_change_status(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "Archived"},
    )

    updated = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert updated.status == "Pending"


@pytest.mark.parametrize("status", ["Completed", "Cancelled"])
def test_terminal_requests_do_not_show_status_actions(
    client,
    app,
    status,
):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status=status,
    )

    response = client.get(
        f"/service-requests/{service_request.id}"
    )

    assert response.status_code == 200
    assert b"no further status changes are available" in (
        response.data.lower()
    )
    assert b'name="target_status"' not in response.data


def test_status_update_for_missing_request_returns_404(client):
    response = client.post(
        "/service-requests/9999/status",
        data={"target_status": "In Progress"},
    )

    assert response.status_code == 404


def test_status_update_route_rejects_get(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.get(
        f"/service-requests/{service_request.id}/status"
    )

    assert response.status_code == 405

    unchanged = app.extensions["service_request_services"][
        "query"
    ].get_service_request(service_request.id)

    assert unchanged.status == "Pending"
