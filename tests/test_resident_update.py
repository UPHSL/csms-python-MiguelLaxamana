from csms.database import initialize_database
from csms.models.resident import Resident
from csms.repositories.resident_repository import (
    ResidentRepository,
)
from csms.services.resident_query_service import (
    ResidentQueryService,
)
from csms.services.resident_update_service import (
    ResidentUpdateService,
)
from csms.services.resident_validator import (
    ResidentValidator,
)


def make_repository(
    tmp_path,
) -> ResidentRepository:
    database_path = (
        tmp_path / "t06-residents.sqlite"
    )

    initialize_database(
        database_path
    )

    return ResidentRepository(
        str(database_path)
    )


def make_update_service(
    repository: ResidentRepository,
) -> ResidentUpdateService:
    validator = ResidentValidator()

    return ResidentUpdateService(
        validator,
        repository,
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


def test_valid_resident_update_succeeds(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel@example.com",
    )

    assert result.success is True
    assert result.resident is not None
    assert result.errors == []
    assert result.not_found is False


def test_resident_id_is_preserved(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    original_id = resident.id

    result = service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel@example.com",
    )

    assert result.success is True
    assert result.resident is not None

    assert result.resident.id == original_id


def test_permitted_resident_information_is_persisted(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel.santos@example.com",
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None

    assert stored_resident.id == resident.id
    assert stored_resident.first_name == "Miguel"
    assert stored_resident.last_name == "Santos"
    assert stored_resident.address == "Barangay San Isidro"
    assert stored_resident.contact_number == "09181234567"
    assert stored_resident.email == "miguel.santos@example.com"


def test_resident_status_is_preserved(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident(
            status="Inactive"
        )
    )

    original_status = resident.status

    result = service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel.santos@example.com",
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None
    assert stored_resident.status == original_status
    assert stored_resident.status == "Inactive"


def test_invalid_resident_update_fails(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.update_resident(
        resident.id,
        "",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel.santos@example.com",
    )

    assert result.success is False
    assert result.resident is None
    assert result.not_found is False

    assert "first_name" in result.errors


def test_invalid_resident_update_does_not_modify_persisted_information(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    result = service.update_resident(
        resident.id,
        "",
        "UpdatedLastName",
        "Updated Address",
        "09181234567",
        "updated@example.com",
    )

    assert result.success is False
    assert result.resident is None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None

    assert stored_resident.id == resident.id
    assert stored_resident.first_name == "Juan"
    assert stored_resident.last_name == "Cruz"
    assert stored_resident.address == "Barangay Santo Tomas"
    assert stored_resident.contact_number == "09171234567"
    assert stored_resident.email == "juan@example.com"


def test_updating_nonexistent_resident_is_handled_safely(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    result = service.update_resident(
        999999,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel@example.com",
    )

    assert result.success is False
    assert result.resident is None
    assert result.errors == []
    assert result.not_found is True


def test_nonexistent_update_does_not_create_resident(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    residents_before = repository.find_all()

    result = service.update_resident(
        999999,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel@example.com",
    )

    residents_after = repository.find_all()

    assert result.success is False
    assert result.not_found is True

    assert len(residents_after) == len(
        residents_before
    )


def test_updated_resident_is_visible_through_search(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    update_service = make_update_service(
        repository
    )

    query_service = ResidentQueryService(
        repository
    )

    resident = repository.save(
        make_resident(
            first_name="Juan",
            last_name="Cruz",
        )
    )

    result = update_service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel.santos@example.com",
    )

    assert result.success is True

    results = query_service.search_residents(
        "Miguel"
    )

    assert len(results) == 1
    assert results[0].id == resident.id
    assert results[0].first_name == "Miguel"
    assert results[0].last_name == "Santos"


def test_updated_information_and_contact_number_are_preserved(
    tmp_path,
):
    repository = make_repository(
        tmp_path
    )

    service = make_update_service(
        repository
    )

    resident = repository.save(
        make_resident()
    )

    original_id = resident.id
    original_status = resident.status

    result = service.update_resident(
        resident.id,
        "Miguel",
        "Santos",
        "Barangay San Isidro",
        "09181234567",
        "miguel.santos@example.com",
    )

    assert result.success is True
    assert result.resident is not None

    stored_resident = repository.find_by_id(
        resident.id
    )

    assert stored_resident is not None

    assert stored_resident.id == original_id
    assert stored_resident.first_name == "Miguel"
    assert stored_resident.last_name == "Santos"
    assert stored_resident.address == "Barangay San Isidro"
    assert stored_resident.contact_number == "09181234567"
    assert stored_resident.email == "miguel.santos@example.com"
    assert stored_resident.status == original_status
    assert stored_resident.contact_number == "09181234567"