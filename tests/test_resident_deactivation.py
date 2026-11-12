from csms.database import initialize_database
from csms.models.resident import Resident
from csms.repositories.resident_repository import (
    ResidentRepository,
)
from csms.services.resident_deactivation_service import (
    ResidentDeactivationService,
)
from csms.services.resident_query_service import (
    ResidentQueryService,
)


def make_repository(
    tmp_path,
) -> ResidentRepository:
    database_path = (
        tmp_path / "t07-residents.sqlite"
    )

    initialize_database(
        database_path
    )

    return ResidentRepository(
        str(database_path)
    )


def make_deactivation_service(
    repository: ResidentRepository,
) -> ResidentDeactivationService:
    return ResidentDeactivationService(
        repository
    )


def make_resident(
    first_name="Juan",
    last_name="Cruz",
    address="Barangay Santo Tomas",
    contact_number="09171234567",
    email="juan@example.com",
    status="Active",
) -> Resident:
    return Resident(
        first_name=first_name,
        last_name=last_name,
        address=address,
        contact_number=contact_number,
        email=email,
        status=status,
    )


def test_active_resident_can_be_deactivated(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None
    assert result.not_found is False
    assert result.already_inactive is False


def test_resident_status_becomes_inactive_in_persistence(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None
    assert stored_resident.status == "Inactive"


def test_resident_id_is_preserved(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    original_id = resident.id

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None

    assert result.resident.id == original_id

    stored_resident = repository.find_by_id(
        original_id
    )

    assert stored_resident is not None
    assert stored_resident.id == original_id


def test_resident_information_is_preserved(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident(
            first_name="Juan",
            last_name="Dela Cruz",
            address="Barangay Santo Tomas",
            contact_number="09171234567",
            email="juan@example.com",
        )
    )

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None

    assert stored_resident.id == resident.id
    assert stored_resident.first_name == "Juan"
    assert stored_resident.last_name == "Dela Cruz"
    assert stored_resident.address == "Barangay Santo Tomas"
    assert stored_resident.contact_number == "09171234567"
    assert stored_resident.email == "juan@example.com"
    assert stored_resident.status == "Inactive"


def test_deactivated_resident_remains_persisted_and_retrievable(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None
    assert stored_resident.id == resident.id
    assert stored_resident.status == "Inactive"


def test_deactivated_resident_remains_available_through_t05(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    deactivation_service = (
        make_deactivation_service(
            repository
        )
    )

    query_service = ResidentQueryService(
        repository
    )

    resident = repository.save(
        make_resident(
            first_name="Miguel",
            last_name="Santos",
        )
    )

    result = (
        deactivation_service.deactivate_resident(
            resident.id
        )
    )

    assert result.success is True

    search_results = (
        query_service.search_residents(
            "Miguel"
        )
    )

    assert len(search_results) == 1
    assert search_results[0].id == resident.id
    assert search_results[0].first_name == "Miguel"
    assert search_results[0].last_name == "Santos"
    assert search_results[0].status == "Inactive"


def test_already_inactive_resident_is_handled_safely(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident(
            first_name="Maria",
            last_name="Santos",
            address="Barangay San Isidro",
            contact_number="09181234567",
            email="maria@example.com",
            status="Inactive",
        )
    )

    original_id = resident.id

    result = service.deactivate_resident(
        resident.id
    )

    assert result.success is True
    assert result.resident is not None
    assert result.not_found is False
    assert result.already_inactive is True

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None

    assert stored_resident.id == original_id
    assert stored_resident.first_name == "Maria"
    assert stored_resident.last_name == "Santos"
    assert stored_resident.address == "Barangay San Isidro"
    assert stored_resident.contact_number == "09181234567"
    assert stored_resident.email == "maria@example.com"
    assert stored_resident.status == "Inactive"


def test_nonexistent_resident_is_handled_safely(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    result = service.deactivate_resident(
        999999
    )

    assert result.success is False
    assert result.resident is None
    assert result.not_found is True
    assert result.already_inactive is False


def test_nonexistent_deactivation_does_not_create_or_delete_records(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    residents_before = repository.find_all()

    result = service.deactivate_resident(
        999999
    )

    residents_after = repository.find_all()

    assert result.success is False
    assert result.not_found is True

    assert len(residents_after) == len(
        residents_before
    )

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None
    assert stored_resident.id == resident.id
    assert stored_resident.status == "Active"


def test_deactivating_one_resident_does_not_affect_another(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_deactivation_service(
        repository
    )

    resident_one = repository.save(
        make_resident(
            first_name="Juan",
            last_name="Cruz",
            contact_number="09171234567",
            email="juan@example.com",
        )
    )

    resident_two = repository.save(
        make_resident(
            first_name="Maria",
            last_name="Santos",
            contact_number="09181234567",
            email="maria@example.com",
        )
    )

    result = service.deactivate_resident(
        resident_one.id
    )

    assert result.success is True

    stored_resident_one = repository.find_by_id(
        resident_one.id
    )

    stored_resident_two = repository.find_by_id(
        resident_two.id
    )

    assert stored_resident_one is not None
    assert stored_resident_two is not None

    assert stored_resident_one.status == "Inactive"
    assert stored_resident_two.status == "Active"

    assert stored_resident_two.id == resident_two.id
    assert stored_resident_two.first_name == "Maria"
    assert stored_resident_two.last_name == "Santos"
    assert stored_resident_two.address == "Barangay Santo Tomas"
    assert stored_resident_two.contact_number == "09181234567"
    assert stored_resident_two.email == "maria@example.com"