
"""Web routes for the CSMS user interface."""

from datetime import date

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
from csms.models.service_request import ServiceRequest


main_blueprint = Blueprint("main", __name__)


def get_resident_services():
    """Retrieve configured Resident services."""
    return current_app.extensions["resident_services"]


def get_service_request_services():
    """Retrieve configured Service Request services."""
    return current_app.extensions["service_request_services"]


def get_dashboard_service():
    """Retrieve the configured Dashboard service."""
    return current_app.extensions["dashboard_service"]


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


def format_validation_errors(errors) -> list[str]:
    """Convert Resident validator field names into readable messages."""
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

    if isinstance(errors, dict):
        return [
            messages.get(field, message)
            for field, message in errors.items()
        ]

    return [
        messages.get(error, "Please check the submitted information.")
        for error in errors
    ]


def format_service_request_errors(errors) -> list[str]:
    """Convert Service Request validation errors into readable messages."""
    messages = {
        "resident_id": "Please enter a valid Resident ID.",
        "service_type": "Service type is required.",
        "description": "Description is required.",
        "date_requested": "Please enter a valid request date.",
        "status": "Invalid service request status.",
        "id": "Service Request ID must not be supplied.",
    }

    if isinstance(errors, dict):
        return [
            messages.get(field, message)
            for field, message in errors.items()
        ]

    return [
        messages.get(error, "Please check the submitted information.")
        for error in errors
    ]


# ---------------------------------------------------------------------
# General routes
# ---------------------------------------------------------------------

@main_blueprint.get("/")
def index() -> str:
    """Display the welcome page."""
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


# ---------------------------------------------------------------------
# Dashboard routes
# ---------------------------------------------------------------------

@main_blueprint.get("/dashboard")
def dashboard():
    """Display dashboard statistics and recent service requests."""
    dashboard_data = get_dashboard_service().get_dashboard_data()

    return render_template(
        "dashboard.html",
        **dashboard_data,
    )


# ---------------------------------------------------------------------
# Resident routes
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# Service Request routes
# ---------------------------------------------------------------------

@main_blueprint.get("/service-requests")
def service_request_list():
    """Display, search, and filter Service Requests."""
    search_query = request.args.get("q", "").strip()
    selected_status = request.args.get("status", "All").strip()

    status_filter = (
        None if selected_status == "All"
        else selected_status
    )

    try:
        service_requests = (
            get_service_request_services()["query"].list_service_requests(
                search_term=search_query,
                status=status_filter,
            )
        )
    except ValueError:
        abort(400)

    return render_template(
        "service_requests.html",
        service_requests=service_requests,
        search_query=search_query,
        selected_status=selected_status,
        statuses=[
            "All",
            "Pending",
            "In Progress",
            "Completed",
            "Cancelled",
        ],
    )


@main_blueprint.route(
    "/service-requests/new",
    methods=["GET", "POST"],
)
def new_service_request():
    """Display and process the Service Request submission form."""
    if request.method == "GET":
        return render_template(
            "service_request_form.html",
            form_data={},
            errors=[],
        )

    form_data = {
        "resident_id": request.form.get("resident_id", "").strip(),
        "service_type": request.form.get("service_type", "").strip(),
        "description": request.form.get("description", "").strip(),
        "date_requested": request.form.get(
            "date_requested", ""
        ).strip(),
    }

    errors = []

    try:
        resident_id = int(form_data["resident_id"])
    except (TypeError, ValueError):
        resident_id = 0
        errors.append("Please enter a valid Resident ID.")

    try:
        request_date = date.fromisoformat(
            form_data["date_requested"]
        )
    except (TypeError, ValueError):
        request_date = None
        errors.append("Please enter a valid request date.")

    if errors:
        return render_template(
            "service_request_form.html",
            form_data=form_data,
            errors=errors,
        ), 400

    service_request = ServiceRequest(
        resident_id=resident_id,
        service_type=form_data["service_type"],
        description=form_data["description"],
        date_requested=request_date,
    )

    result = get_service_request_services()["submission"].submit(
        service_request
    )

    if not result.success:
        errors = format_service_request_errors(result.errors)

        if result.error_message:
            errors.append(result.error_message)

        return render_template(
            "service_request_form.html",
            form_data=form_data,
            errors=errors,
        ), 400

    flash("Service Request successfully submitted.", "success")

    return redirect(
        url_for(
            "main.service_request_detail",
            request_id=result.service_request.id,
        )
    )


@main_blueprint.get("/service-requests/<int:request_id>")
def service_request_detail(request_id: int):
    """Display a single Service Request."""
    service_request = (
        get_service_request_services()["query"].get_service_request(
            request_id
        )
    )

    if service_request is None:
        abort(404)

    return render_template(
        "service_request_detail.html",
        service_request=service_request,
    )


@main_blueprint.post(
    "/service-requests/<int:request_id>/status"
)
def update_service_request_status(request_id: int):
    """Apply an allowed Service Request status transition."""
    target_status = request.form.get(
        "target_status",
        request.form.get("status", ""),
    ).strip()

    result = get_service_request_services()["status"].update_status(
        request_id,
        target_status,
    )

    if not result.success:
        if result.error_message == "Service request not found":
            abort(404)

        flash(
            result.error_message or "Unable to update Service Request.",
            "error",
        )

        return redirect(
            url_for(
                "main.service_request_detail",
                request_id=request_id,
            )
        )

    flash("Service Request status successfully updated.", "success")

    return redirect(
        url_for(
            "main.service_request_detail",
            request_id=request_id,
        )
    )
