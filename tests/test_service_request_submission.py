from datetime import date

from src.csms.models.resident import Resident
from src.csms.models.service_request import ServiceRequest
from src.csms.repositories.resident_repository import ResidentRepository
from src.csms.repositories.service_request_repository import ServiceRequestRepository
from src.csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from src.csms.services.service_request_validator import ServiceRequestValidator


def test_valid_service_request_submission_succeeds():
    """Test 1: Valid Service Request submission succeeds for an active resident."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 6, 1),
    )

    result = service.submit(request)
    assert result.success is True
    assert result.service_request is not None


def test_submitted_service_request_receives_generated_id():
    """Test 2 & 3: Submitted request receives a generated ID and is retrievable by ID."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

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


def test_submitted_service_request_defaults_to_pending():
    """Test 5: Submitted service request preserves Pending status."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

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
    """Test 6: Blank or whitespace service type fails validation and doesn't persist."""
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
    """Test 7: Blank or whitespace description fails validation."""
    validator = ServiceRequestValidator()

    request = ServiceRequest(
        resident_id=1,
        service_type="Barangay Clearance",
        description="",
        date_requested=date(2026, 6, 1),
    )

    errors = validator.validate(request)

    assert "description" in errors


def test_nonexistent_resident_prevents_submission():
    """Test 9: Nonexistent resident prevents submission and returns correct error message."""
    res_repo = ResidentRepository()
    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

    request = ServiceRequest(
        resident_id=99999,
        service_type="Permit Request",
        description="Business permit",
        date_requested=date(2026, 6, 4),
    )

    result = service.submit(request)

    assert result.success is False
    assert result.error_message == "Resident not found"


def test_inactive_resident_cannot_submit_request():
    """Test 10: Inactive resident cannot submit a service request."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

    request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Clearance request",
        date_requested=date(2026, 6, 5),
    )

    result = service.submit(request)

    assert result.success is False
    assert result.error_message == "Resident is Inactive"


def test_submission_does_not_modify_resident():
    """Test 13: Submitting a request does not modify the resident's data."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()
    service = ServiceRequestSubmissionService(validator, res_repo, sr_repo)

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
    """Test 4: Service Request ID must be unassigned before submission."""
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
    """Test 8: Resident ID of zero is invalid."""
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
    """Test 8: Negative Resident ID is invalid."""
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
    """Test 11: Missing date requested fails validation."""
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
    """Test 11: Invalid date requested fails validation."""
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
    """Test 12: New Service Request must have Pending status."""
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


def test_validation_failure_does_not_reach_persistence():
    """Test 14: Invalid Service Request must not be persisted."""

    class FailingRepository:
        def save(self, request):
            raise AssertionError("save() should not be called for invalid requests")

    validator = ServiceRequestValidator()
    res_repo = ResidentRepository()

    service = ServiceRequestSubmissionService(
        validator,
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


def test_service_request_persists_across_repository_instances():
    """Test 15: Persisted Service Request can be retrieved by a new repository instance."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    first_repository = ServiceRequestRepository()

    service = ServiceRequestSubmissionService(
        validator,
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

    second_repository = ServiceRequestRepository()
    retrieved = second_repository.find_by_id(result.service_request.id)

    assert retrieved is not None
    assert retrieved.id == result.service_request.id
    assert retrieved.resident_id == resident.id
    assert retrieved.service_type == "Document Request"
    assert retrieved.description == "Persistent request"
    assert retrieved.date_requested == date(2026, 6, 11)
    assert retrieved.status == "Pending"


def test_service_request_fields_are_preserved():
    """Test 16: Submitted Service Request fields are preserved after persistence."""
    res_repo = ResidentRepository()
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

    validator = ServiceRequestValidator()
    sr_repo = ServiceRequestRepository()

    service = ServiceRequestSubmissionService(
        validator,
        res_repo,
        sr_repo,
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