
from datetime import date

import pytest

from src.csms.database import initialize_database
from src.csms.models.resident import Resident
from src.csms.models.service_request import ServiceRequest
from src.csms.repositories.resident_repository import ResidentRepository
from src.csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from src.csms.services.service_request_query_service import (
    ServiceRequestQueryService,
)


@pytest.fixture
def query_setup(tmp_path):
    database_path = tmp_path / "test_csms.db"
    initialize_database(database_path)

    resident_repository = ResidentRepository(database_path)

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

    repository = ServiceRequestRepository(database_path)
    service = ServiceRequestQueryService(repository)

    return repository, service, resident.id


def add_request(
    repository,
    resident_id,
    service_type,
    description,
    requested_date,
    status="Pending",
):
    return repository.save(
        ServiceRequest(
            resident_id=resident_id,
            service_type=service_type,
            description=description,
            date_requested=requested_date,
            status=status,
        )
    )


def test_list_service_requests_returns_empty_list_when_none_exist(
    query_setup,
):
    _, service, _ = query_setup

    assert service.list_service_requests() == []


def test_list_service_requests_returns_all_requests_in_date_order(
    query_setup,
):
    repository, service, resident_id = query_setup

    older = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Clearance request",
        date(2026, 5, 1),
    )
    newer = add_request(
        repository,
        resident_id,
        "Certificate of Residency",
        "Residency request",
        date(2026, 6, 1),
    )

    results = service.list_service_requests()

    assert [request.id for request in results] == [
        newer.id,
        older.id,
    ]


def test_same_date_requests_are_ordered_by_id_descending(query_setup):
    repository, service, resident_id = query_setup

    first = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "First request",
        date(2026, 6, 1),
    )
    second = add_request(
        repository,
        resident_id,
        "Certificate",
        "Second request",
        date(2026, 6, 1),
    )

    results = service.list_service_requests()

    assert [request.id for request in results] == [
        second.id,
        first.id,
    ]


def test_get_service_request_returns_existing_request(query_setup):
    repository, service, resident_id = query_setup

    created = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Document request",
        date(2026, 6, 1),
    )

    result = service.get_service_request(created.id)

    assert result == created


def test_get_service_request_returns_none_when_missing(query_setup):
    _, service, _ = query_setup

    assert service.get_service_request(999999) is None


def test_search_matches_service_type_case_insensitively(query_setup):
    repository, service, resident_id = query_setup

    created = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Document request",
        date(2026, 6, 1),
    )

    results = service.list_service_requests(search_term="CLEARANCE")

    assert [request.id for request in results] == [created.id]


def test_search_matches_description_case_insensitively(query_setup):
    repository, service, resident_id = query_setup

    created = add_request(
        repository,
        resident_id,
        "Other Service",
        "Request for financial assistance",
        date(2026, 6, 1),
    )

    results = service.list_service_requests(search_term="FINANCIAL")

    assert [request.id for request in results] == [created.id]


def test_search_checks_service_type_or_description_without_duplicates(
    query_setup,
):
    repository, service, resident_id = query_setup

    created = add_request(
        repository,
        resident_id,
        "Financial Assistance",
        "Financial assistance application",
        date(2026, 6, 1),
    )

    results = service.list_service_requests(search_term="financial")

    assert len(results) == 1
    assert results[0].id == created.id


def test_blank_search_returns_all_requests(query_setup):
    repository, service, resident_id = query_setup

    add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Clearance request",
        date(2026, 6, 1),
    )

    results = service.list_service_requests(search_term="   ")

    assert len(results) == 1


def test_search_with_no_matches_returns_empty_list(query_setup):
    repository, service, resident_id = query_setup

    add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Clearance request",
        date(2026, 6, 1),
    )

    assert service.list_service_requests(
        search_term="nonexistent"
    ) == []


def test_status_filter_returns_only_matching_requests(query_setup):
    repository, service, resident_id = query_setup

    pending = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Pending request",
        date(2026, 6, 1),
        "Pending",
    )
    add_request(
        repository,
        resident_id,
        "Certificate",
        "Completed request",
        date(2026, 6, 2),
        "Completed",
    )

    results = service.list_service_requests(status="Pending")

    assert [request.id for request in results] == [pending.id]


def test_unsupported_status_is_rejected(query_setup):
    _, service, _ = query_setup

    with pytest.raises(ValueError, match="Unsupported service request status"):
        service.list_service_requests(status="Approved")


def test_search_and_status_filters_are_combined(query_setup):
    repository, service, resident_id = query_setup

    matching = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Clearance request",
        date(2026, 6, 1),
        "Pending",
    )
    add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Another clearance",
        date(2026, 6, 2),
        "Completed",
    )
    add_request(
        repository,
        resident_id,
        "Certificate",
        "Certificate request",
        date(2026, 6, 3),
        "Pending",
    )

    results = service.list_service_requests(
        search_term="clearance",
        status="Pending",
    )

    assert [request.id for request in results] == [matching.id]


def test_query_preserves_all_fields_and_does_not_modify_records(
    query_setup,
):
    repository, service, resident_id = query_setup

    created = add_request(
        repository,
        resident_id,
        "Barangay Clearance",
        "Document request",
        date(2026, 6, 1),
        "Pending",
    )

    results = service.list_service_requests()

    assert len(results) == 1

    result = results[0]
    assert result.id == created.id
    assert result.resident_id == resident_id
    assert result.service_type == "Barangay Clearance"
    assert result.description == "Document request"
    assert result.date_requested == date(2026, 6, 1)
    assert result.status == "Pending"

    persisted = repository.find_by_id(created.id)
    assert persisted == created
