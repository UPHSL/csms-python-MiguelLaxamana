"""Web routes for the CSMS user interface."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from csms.models.resident import Resident

main_blueprint = Blueprint("main", __name__)


def get_resident_services():
    """Retrieve application services configured by the app factory."""
    return current_app.extensions["resident_services"]


def get_form_data() -> dict[str, str]:
    """Collect editable Resident fields from the submitted form."""
    return {
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "address": request.form.get("address", "").strip(),
        "contact_number": request.form.get(
            "contact_number", ""
        ).strip(),
        "email": request.form.get("email", "").strip(),
    }


def format_validation_errors(errors: list[str]) -> list[str]:
    """Convert validator field names into readable messages."""
    messages = {
        "first_name": "First name is required.",
        "last_name": "Last name is required.",
        "address": "Address is required.",
        "contact_number": (
            "Contact number must contain 11 digits "
            "and start with 09."
        ),
        "email": "Please enter a valid email address.",
        "status": "Invalid resident status.",
    }

    return [
        messages.get(error, "Please check the submitted information.")
        for error in errors
    ]


@main_blueprint.get("/")
def index() -> str:
    """Display the Sprint 0 welcome page."""
    return render_template(
        "index.html",
        application_name=current_app.config["APP_NAME"],
        application_version=current_app.config["APP_VERSION"],
        current_sprint=current_app.config["CURRENT_SPRINT"],
    )


@main_blueprint.get("/health")
def health():
    """Return a simple application health response."""
    return jsonify(
        {
            "application": current_app.config["APP_NAME"],
            "status": "ok",
            "version": current_app.config["APP_VERSION"],
        }
    )


@main_blueprint.get("/residents")
def resident_list():
    """Display and search persisted residents."""
    query = request.args.get("q", "")

    residents = get_resident_services()["query"].search_residents(
        query
    )

    return render_template(
        "residents.html",
        residents=residents,
        search_query=query,
    )


@main_blueprint.route(
    "/residents/register",
    methods=["GET", "POST"],
)
def register_resident():
    """Display the registration form and register residents."""
    if request.method == "GET":
        return render_template(
            "resident_form.html",
            page_title="Register Resident",
            form_action=url_for("main.register_resident"),
            resident=None,
            form_data={},
            errors=[],
            is_edit=False,
        )

    form_data = get_form_data()

    resident = Resident(
        first_name=form_data["first_name"],
        last_name=form_data["last_name"],
        address=form_data["address"],
        contact_number=form_data["contact_number"],
        email=form_data["email"],
    )

    result = get_resident_services()["registration"].register_resident(
        resident
    )

    if not result.success:
        return render_template(
            "resident_form.html",
            page_title="Register Resident",
            form_action=url_for("main.register_resident"),
            resident=None,
            form_data=form_data,
            errors=format_validation_errors(result.errors),
            is_edit=False,
        ), 400

    flash("Resident successfully registered.", "success")

    return redirect(url_for("main.resident_list"))


@main_blueprint.route(
    "/residents/<int:resident_id>/edit",
    methods=["GET", "POST"],
)
def edit_resident(resident_id: int):
    """Display and process the Resident edit form."""
    services = get_resident_services()
    existing_resident = services["query"].get_resident(resident_id)

    if existing_resident is None:
        abort(404)

    if request.method == "GET":
        form_data = {
            "first_name": existing_resident.first_name,
            "last_name": existing_resident.last_name,
            "address": existing_resident.address,
            "contact_number": existing_resident.contact_number,
            "email": existing_resident.email,
        }

        return render_template(
            "resident_form.html",
            page_title="Edit Resident",
            form_action=url_for(
                "main.edit_resident",
                resident_id=resident_id,
            ),
            resident=existing_resident,
            form_data=form_data,
            errors=[],
            is_edit=True,
        )

    form_data = get_form_data()

    result = services["update"].update_resident(
        resident_id=resident_id,
        first_name=form_data["first_name"],
        last_name=form_data["last_name"],
        address=form_data["address"],
        contact_number=form_data["contact_number"],
        email=form_data["email"],
    )

    if result.not_found:
        abort(404)

    if not result.success:
        return render_template(
            "resident_form.html",
            page_title="Edit Resident",
            form_action=url_for(
                "main.edit_resident",
                resident_id=resident_id,
            ),
            resident=existing_resident,
            form_data=form_data,
            errors=format_validation_errors(result.errors),
            is_edit=True,
        ), 400

    flash("Resident information successfully updated.", "success")

    return redirect(url_for("main.resident_list"))


@main_blueprint.post(
    "/residents/<int:resident_id>/deactivate"
)
def deactivate_resident(resident_id: int):
    """Deactivate an active resident without deleting the record."""
    result = get_resident_services()["deactivation"].deactivate_resident(
        resident_id
    )

    if result.not_found:
        abort(404)

    if result.already_inactive:
        flash("This resident is already inactive.", "info")
    else:
        flash("Resident successfully deactivated.", "success")

    return redirect(url_for("main.resident_list"))