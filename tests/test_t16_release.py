from datetime import date

from csms.models.resident import Resident
from csms.services.service_request_query_service import (
    ServiceRequestQueryService,
)
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def test_t16_resident_to_completed_request_workflow(client, app):
    """Verify registration, submission, workflow, and persistence."""

    registration = app.extensions["resident_services"][
        "registration"
    ].register_resident(
        Resident(
            first_name="Miguel",
            last_name="ReleaseTest",
            address="Biñan City, Laguna",
            contact_number="09123456789",
            email="t16-release@example.com",
        )
    )

    assert registration.success
    resident = registration.resident
    assert resident.id is not None

    submission = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "T16 release integration test",
            "date_requested": date.today().isoformat(),
        },
    )

    assert submission.status_code == 302

    repository = ServiceRequestRepository(
        app.config["DATABASE_PATH"]
    )
    query_service = ServiceRequestQueryService(repository)

    requests = query_service.list_service_requests()
    assert len(requests) == 1

    service_request = requests[0]
    assert service_request.resident_id == resident.id
    assert service_request.status == "Pending"

    status_response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "In Progress"},
    )

    assert status_response.status_code == 302

    completed_response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"target_status": "Completed"},
    )

    assert completed_response.status_code == 302

    persisted = query_service.get_service_request(
        service_request.id
    )

    assert persisted is not None
    assert persisted.resident_id == resident.id
    assert persisted.service_type == "Medical Assistance"
    assert persisted.status == "Completed"

    stored_resident = app.extensions["resident_services"][
        "query"
    ].get_resident(resident.id)

    assert stored_resident is not None
    assert stored_resident.status == "Active"
