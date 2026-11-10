
from datetime import date

from csms.database import initialize_database
from csms.repositories.resident_repository import ResidentRepository

from src.csms.models.resident import Resident
from src.csms.models.service_request import ServiceRequest
from src.csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from src.csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from src.csms.services.service_request_validator import ServiceRequestValidator


def make_repositories(database_path):
    """Create isolated repositories using a temporary database."""
    initialize_database(database_path)

    resident_repository = ResidentRepository(str(database_path))
    service_request_repository = ServiceRequestRepository(database_path)

    return resident_repository, service_request_repository


def test_valid_service_request_submission_succeeds(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Juan",
            last_name="Dela Cruz",
            address="Santa Rosa",
            contact_number="09123456789",
            email="juan@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 6, 1),
    )

    result = service.submit(request)

    assert result.success is True
    assert result.service_request is not None


def test_submitted_service_request_receives_generated_id(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Maria",
            last_name="Santos",
            address="Santa Rosa",
            contact_number="09187654321",
            email="maria@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Certificate Request",
        description="Residency certificate",
        date_requested=date(2026, 6, 2),
    )

    result = service.submit(request)

    assert result.success is True
    assert result.service_request.id is not None

    retrieved = sr_repo.find_by_id(result.service_request.id)

    assert retrieved is not None
    assert retrieved.id == result.service_request.id
    assert retrieved.service_type == "Certificate Request"


def test_submitted_service_request_defaults_to_pending(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Pedro",
            last_name="Penduko",
            address="Santa Rosa",
            contact_number="09111222333",
            email="pedro@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Community Assistance",
        description="Medical aid",
        date_requested=date(2026, 6, 3),
    )

    result = service.submit(request)

    assert result.success is True
    assert result.service_request.status == "Pending"


def test_blank_service_type_fails_validation():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="   ",
        description="Valid description",
        date_requested=date(2026, 6, 1),
    )

    errors = validator.validate(request)

    assert "service_type" in errors


def test_blank_description_fails_validation():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="Barangay Clearance",
        description="",
        date_requested=date(2026, 6, 1),
    )

    errors = validator.validate(request)

    assert "description" in errors


def test_nonexistent_resident_prevents_submission(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=99999,
        service_type="Permit Request",
        description="Business permit",
        date_requested=date(2026, 6, 4),
    )

    result = service.submit(request)

    assert result.success is False
    assert result.error_message == "Resident not found"


def test_inactive_resident_cannot_submit_request(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Inactive",
            last_name="Resident",
            address="Santa Rosa",
            contact_number="09998887777",
            email="inactive@example.com",
            status="Inactive",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Clearance request",
        date_requested=date(2026, 6, 5),
    )

    result = service.submit(request)

    assert result.success is False
    assert result.error_message == "Resident is Inactive"


def test_submission_does_not_modify_resident(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Unchanged",
            last_name="Resident",
            address="Santa Rosa",
            contact_number="09444333222",
            email="unchanged@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Check resident fields",
        date_requested=date(2026, 6, 6),
    )

    service.submit(request)

    updated_resident = res_repo.find_by_id(resident.id)

    assert updated_resident.first_name == "Unchanged"
    assert updated_resident.last_name == "Resident"
    assert updated_resident.status == "Active"


def test_service_request_id_must_be_unassigned():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        id=1,
        resident_id=1,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested=date(2026, 6, 7),
    )

    errors = validator.validate(request)

    assert "id" in errors


def test_resident_id_zero_is_invalid():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=0,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested=date(2026, 6, 8),
    )

    errors = validator.validate(request)

    assert "resident_id" in errors


def test_negative_resident_id_is_invalid():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=-1,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested=date(2026, 6, 8),
    )

    errors = validator.validate(request)

    assert "resident_id" in errors


def test_missing_date_requested_fails_validation():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested=None,
    )

    errors = validator.validate(request)

    assert "date_requested" in errors


def test_invalid_date_requested_fails_validation():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested="not-a-valid-date",
    )

    errors = validator.validate(request)

    assert "date_requested" in errors


def test_non_pending_status_fails_validation():
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="Barangay Clearance",
        description="Valid description",
        date_requested=date(2026, 6, 9),
        status="Approved",
    )

    errors = validator.validate(request)

    assert "status" in errors


def test_validation_failure_does_not_reach_persistence(tmp_path):
    class FailingRepository:
        def save(self, request):
            raise AssertionError(
                "save() should not be called for invalid requests"
            )

    res_repo, _ = make_repositories(tmp_path / "test.sqlite")

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(),
        res_repo,
        FailingRepository(),
    )

    request = ServiceRequest(
        resident_id=1,
        service_type="   ",
        description="Valid description",
        date_requested=date(2026, 6, 10),
    )

    result = service.submit(request)

    assert result.success is False
    assert "service_type" in result.errors


def test_service_request_persists_across_repository_instances(tmp_path):
    database_path = tmp_path / "test.sqlite"
    res_repo, first_repository = make_repositories(database_path)

    resident = res_repo.save(
        Resident(
            first_name="Persistent",
            last_name="Resident",
            address="Santa Rosa",
            contact_number="09112223344",
            email="persistent@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(),
        res_repo,
        first_repository,
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Document Request",
        description="Persistent request",
        date_requested=date(2026, 6, 11),
    )

    result = service.submit(request)

    assert result.success is True

    second_repository = ServiceRequestRepository(database_path)
    retrieved = second_repository.find_by_id(result.service_request.id)

    assert retrieved is not None
    assert retrieved.id == result.service_request.id
    assert retrieved.resident_id == resident.id
    assert retrieved.service_type == "Document Request"
    assert retrieved.description == "Persistent request"
    assert retrieved.date_requested == date(2026, 6, 11)
    assert retrieved.status == "Pending"


def test_service_request_fields_are_preserved(tmp_path):
    res_repo, sr_repo = make_repositories(tmp_path / "test.sqlite")

    resident = res_repo.save(
        Resident(
            first_name="Fields",
            last_name="Preserved",
            address="Santa Rosa",
            contact_number="09556667788",
            email="fields@example.com",
            status="Active",
        )
    )

    service = ServiceRequestSubmissionService(
        ServiceRequestValidator(), res_repo, sr_repo
    )

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Community Assistance",
        description="Assistance request details",
        date_requested=date(2026, 6, 12),
    )

    result = service.submit(request)

    assert result.success is True
    assert result.service_request.resident_id == resident.id
    assert result.service_request.service_type == "Community Assistance"
    assert result.service_request.description == "Assistance request details"
    assert result.service_request.date_requested == date(2026, 6, 12)
    assert result.service_request.status == "Pending"
