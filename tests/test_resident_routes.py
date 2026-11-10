import pytest


VALID_RESIDENT_DATA = {
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "address": "Biñan City, Laguna",
    "contact_number": "09123456789",
    "email": "juan@example.com",
}


def create_resident(client, app, data=None):
    """Register a resident and return the persisted record."""
    resident_data = data or VALID_RESIDENT_DATA

    response = client.post(
        "/residents/register",
        data=resident_data,
        follow_redirects=True,
    )

    assert response.status_code == 200

    residents = app.extensions[
        "resident_services"
    ]["query"].list_residents()

    return next(
        resident
        for resident in residents
        if resident.email == resident_data["email"]
    )


def test_resident_list_page_is_available(client):
    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Resident Management" in response.data
    assert b"Resident Records" in response.data


def test_resident_list_displays_persisted_residents(client, app):
    create_resident(client, app)

    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Dela Cruz" in response.data
    assert b"Bi\xc3\xb1an City" in response.data
    assert b"09123456789" in response.data
    assert b"juan@example.com" in response.data
    assert b"Active" in response.data


def test_search_residents_by_first_name(client, app):
    create_resident(client, app)

    response = client.get("/residents?q=juA")

    assert response.status_code == 200
    assert b"Juan" in response.data


def test_search_residents_by_last_name(client, app):
    create_resident(client, app)

    response = client.get("/residents?q=DELA")

    assert response.status_code == 200
    assert b"Dela Cruz" in response.data


def test_blank_search_displays_all_residents(client, app):
    create_resident(client, app)

    second_resident = {
        "first_name": "Maria",
        "last_name": "Santos",
        "address": "Cabuyao, Laguna",
        "contact_number": "09987654321",
        "email": "maria@example.com",
    }

    create_resident(client, app, second_resident)

    response = client.get("/residents?q=%20%20")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Maria" in response.data
    assert b"Total matching residents: 2" in response.data


def test_registration_form_is_available(client):
    response = client.get("/residents/register")

    assert response.status_code == 200
    assert b"Register Resident" in response.data
    assert b'name="first_name"' in response.data
    assert b'name="last_name"' in response.data
    assert b'name="address"' in response.data
    assert b'name="contact_number"' in response.data
    assert b'name="email"' in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data


def test_valid_registration_saves_resident(client, app):
    response = client.post(
        "/residents/register",
        data=VALID_RESIDENT_DATA,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Resident successfully registered" in response.data

    residents = app.extensions[
        "resident_services"
    ]["query"].list_residents()

    assert len(residents) == 1
    assert residents[0].first_name == "Juan"
    assert residents[0].status == "Active"
    assert residents[0].id is not None


def test_invalid_registration_displays_validation_errors(client, app):
    invalid_data = {
        **VALID_RESIDENT_DATA,
        "first_name": "",
        "contact_number": "12345",
        "email": "invalid-email",
    }

    response = client.post(
        "/residents/register",
        data=invalid_data,
    )

    assert response.status_code == 400
    assert b"Please correct the following" in response.data
    assert b"Contact number" in response.data
    assert b"valid email" in response.data
    assert b'value="12345"' in response.data

    residents = app.extensions[
        "resident_services"
    ]["query"].list_residents()

    assert len(residents) == 0


def test_edit_form_displays_existing_resident_details(client, app):
    resident = create_resident(client, app)

    response = client.get(
        f"/residents/{resident.id}/edit"
    )

    assert response.status_code == 200
    assert b"Edit Resident" in response.data
    assert b"Juan" in response.data
    assert b"Dela Cruz" in response.data
    assert b"Bi\xc3\xb1an City" in response.data
    assert b"09123456789" in response.data
    assert b"juan@example.com" in response.data
    assert f"Resident ID".encode() in response.data
    assert b"Active" in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data


def test_valid_edit_updates_resident(client, app):
    resident = create_resident(client, app)

    updated_data = {
        "first_name": "Juan Miguel",
        "last_name": "Dela Cruz",
        "address": "Poblacion, Biñan City",
        "contact_number": "09111222333",
        "email": "juan.miguel@example.com",
    }

    response = client.post(
        f"/residents/{resident.id}/edit",
        data=updated_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Resident information successfully updated" in response.data

    updated_resident = app.extensions[
        "resident_services"
    ]["query"].get_resident(resident.id)

    assert updated_resident.first_name == "Juan Miguel"
    assert updated_resident.address == "Poblacion, Biñan City"
    assert updated_resident.contact_number == "09111222333"
    assert updated_resident.email == "juan.miguel@example.com"
    assert updated_resident.id == resident.id
    assert updated_resident.status == "Active"


def test_invalid_edit_does_not_modify_resident(client, app):
    resident = create_resident(client, app)

    invalid_data = {
        "first_name": "",
        "last_name": "Changed",
        "address": "Changed Address",
        "contact_number": "123",
        "email": "invalid-email",
    }

    response = client.post(
        f"/residents/{resident.id}/edit",
        data=invalid_data,
    )

    assert response.status_code == 400
    assert b"Please correct the following" in response.data

    unchanged_resident = app.extensions[
        "resident_services"
    ]["query"].get_resident(resident.id)

    assert unchanged_resident.first_name == "Juan"
    assert unchanged_resident.last_name == "Dela Cruz"
    assert unchanged_resident.address == "Biñan City, Laguna"
    assert unchanged_resident.contact_number == "09123456789"
    assert unchanged_resident.email == "juan@example.com"


def test_edit_missing_resident_returns_404(client):
    response = client.get("/residents/9999/edit")

    assert response.status_code == 404


def test_deactivation_changes_resident_status(client, app):
    resident = create_resident(client, app)

    response = client.post(
        f"/residents/{resident.id}/deactivate",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Resident successfully deactivated" in response.data

    deactivated_resident = app.extensions[
        "resident_services"
    ]["query"].get_resident(resident.id)

    assert deactivated_resident.status == "Inactive"


def test_inactive_resident_remains_visible_and_searchable(client, app):
    resident = create_resident(client, app)

    client.post(
        f"/residents/{resident.id}/deactivate"
    )

    response = client.get("/residents?q=Juan")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Inactive" in response.data
    assert b"Deactivate" not in response.data


def test_get_deactivation_route_is_not_allowed(client, app):
    resident = create_resident(client, app)

    response = client.get(
        f"/residents/{resident.id}/deactivate"
    )

    assert response.status_code == 405

    unchanged_resident = app.extensions[
        "resident_services"
    ]["query"].get_resident(resident.id)

    assert unchanged_resident.status == "Active"


def test_repeated_deactivation_is_safe(client, app):
    resident = create_resident(client, app)

    first_response = client.post(
        f"/residents/{resident.id}/deactivate"
    )

    second_response = client.post(
        f"/residents/{resident.id}/deactivate",
        follow_redirects=True,
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 200
    assert b"already inactive" in second_response.data

    final_resident = app.extensions[
        "resident_services"
    ]["query"].get_resident(resident.id)

    assert final_resident.status == "Inactive"