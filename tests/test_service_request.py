from datetime import date
from src.csms.models.service_request import ServiceRequest


def test_service_request_can_be_created():
    """Test 1: Service Request can be created using sensible information."""
    request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Request for employment requirement",
        date_requested=date(2026, 6, 1),
    )
    assert request is not None


def test_service_request_information_is_accessible():
    """Test 2: Service Request information is fully accessible."""
    request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Request for employment requirement",
        date_requested=date(2026, 6, 1),
    )
    assert request.resident_id == 25
    assert request.service_type == "Barangay Clearance"
    assert request.description == "Request for employment requirement"
    assert request.date_requested == date(2026, 6, 1)


def test_resident_id_is_preserved():
    """Test 3: Resident ID is correctly preserved without alteration."""
    request = ServiceRequest(
        resident_id=25,
        service_type="Certificate Request",
        description="Residency certificate",
        date_requested=date(2026, 6, 2),
    )
    assert request.resident_id == 25


def test_new_service_request_has_unassigned_id():
    """Test 4: A new Service Request has an unassigned ID (None)."""
    request = ServiceRequest(
        resident_id=10,
        service_type="Community Assistance",
        description="Medical assistance",
        date_requested=date(2026, 6, 3),
    )
    assert request.id is None


def test_new_service_request_defaults_to_pending():
    """Test 5: A new Service Request automatically defaults to Pending status."""
    request = ServiceRequest(
        resident_id=5,
        service_type="Permit Request",
        description="Business permit",
        date_requested=date(2026, 6, 4),
    )
    assert request.status == "Pending"


def test_service_request_information_is_independent():
    """Test 6: Multiple Service Request objects preserve independent information."""
    req_one = ServiceRequest(
        resident_id=1,
        service_type="Type A",
        description="Desc A",
        date_requested=date(2026, 6, 1),
    )
    req_two = ServiceRequest(
        resident_id=2,
        service_type="Type B",
        description="Desc B",
        date_requested=date(2026, 6, 2),
    )

    assert req_one.resident_id == 1
    assert req_one.service_type == "Type A"
    assert req_one.description == "Desc A"
    assert req_one.status == "Pending"

    assert req_two.resident_id == 2
    assert req_two.service_type == "Type B"
    assert req_two.description == "Desc B"
    assert req_two.status == "Pending"