import pytest

from csms.database import initialize_database
from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


@pytest.fixture
def repository(tmp_path):
    database_path = tmp_path / "test_residents.db"

    initialize_database(database_path)

    return ResidentRepository(database_path)


def make_valid_resident():
    return Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Barangay Santo Tomas",
        contact_number="09171234567",
        email="juan@example.com",
        status="Active",
    )


def test_save_resident(repository):
    resident = make_valid_resident()

    assert resident.id is None

    saved_resident = repository.save(resident)

    assert saved_resident.id is not None
    assert isinstance(saved_resident.id, int)
    assert saved_resident.id > 0


def test_find_resident_by_id(repository):
    resident = make_valid_resident()

    saved_resident = repository.save(resident)
    retrieved_resident = repository.find_by_id(saved_resident.id)

    assert retrieved_resident is not None
    assert retrieved_resident.id == saved_resident.id
    assert retrieved_resident.first_name == resident.first_name
    assert retrieved_resident.last_name == resident.last_name
    assert retrieved_resident.address == resident.address
    assert retrieved_resident.contact_number == resident.contact_number
    assert retrieved_resident.email == resident.email
    assert retrieved_resident.status == resident.status


def test_resident_information_is_preserved(repository):
    resident = Resident(
        first_name="Maria",
        last_name="Santos",
        address="Barangay San Isidro",
        contact_number="09181234567",
        email="maria@example.com",
        status="Inactive",
    )

    saved_resident = repository.save(resident)
    retrieved_resident = repository.find_by_id(saved_resident.id)

    assert retrieved_resident is not None
    assert retrieved_resident.first_name == "Maria"
    assert retrieved_resident.last_name == "Santos"
    assert retrieved_resident.address == "Barangay San Isidro"
    assert retrieved_resident.contact_number == "09181234567"
    assert retrieved_resident.email == "maria@example.com"
    assert retrieved_resident.status == "Inactive"


def test_active_status_is_preserved(repository):
    resident = Resident(
        first_name="Pedro",
        last_name="Reyes",
        address="Barangay San Antonio",
        contact_number="09191234567",
        email="pedro@example.com",
        status="Active",
    )

    saved_resident = repository.save(resident)
    retrieved_resident = repository.find_by_id(saved_resident.id)

    assert retrieved_resident is not None
    assert retrieved_resident.status == "Active"


def test_find_missing_resident_returns_none(repository):
    retrieved_resident = repository.find_by_id(999999)

    assert retrieved_resident is None


def test_resident_persists_across_repository_instances(tmp_path):
    database_path = tmp_path / "test_residents.db"

    initialize_database(database_path)

    first_repository = ResidentRepository(database_path)

    resident = make_valid_resident()
    saved_resident = first_repository.save(resident)

    second_repository = ResidentRepository(database_path)

    retrieved_resident = second_repository.find_by_id(
        saved_resident.id
    )

    assert retrieved_resident is not None
    assert retrieved_resident.id == saved_resident.id
    assert retrieved_resident.first_name == "Juan"
    assert retrieved_resident.contact_number == "09171234567"
    assert retrieved_resident.status == "Active"

def test_multiple_residents_are_persisted_as_separate_records(repository):
    first_resident = Resident(
        first_name="Ana",
        last_name="Garcia",
        address="Barangay Maligaya",
        contact_number="09182345678",
        email="ana@example.com",
        status="Active",
    )

    second_resident = Resident(
        first_name="Mark",
        last_name="Dela Cruz",
        address="Barangay San Jose",
        contact_number="09193456789",
        email="mark@example.com",
        status="Inactive",
    )

    saved_first = repository.save(first_resident)
    saved_second = repository.save(second_resident)

    retrieved_first = repository.find_by_id(saved_first.id)
    retrieved_second = repository.find_by_id(saved_second.id)

    assert retrieved_first is not None
    assert retrieved_second is not None
    assert retrieved_first.id != retrieved_second.id
    assert retrieved_first.first_name == "Ana"
    assert retrieved_second.first_name == "Mark"
    assert retrieved_first.status == "Active"
    assert retrieved_second.status == "Inactive"