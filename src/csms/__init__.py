
"""Community Services Management System Flask application."""

from flask import Flask

from csms.config import DevelopmentConfig
from csms.database import initialize_database
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.dashboard_service import DashboardService
from csms.services.resident_deactivation_service import (
    ResidentDeactivationService,
)
from csms.services.resident_query_service import ResidentQueryService
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_update_service import ResidentUpdateService
from csms.services.resident_validator import ResidentValidator
from csms.services.service_request_query_service import (
    ServiceRequestQueryService,
)
from csms.services.service_request_status_service import (
    ServiceRequestStatusService,
)
from csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from csms.services.service_request_validator import (
    ServiceRequestValidator,
)


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    """Create and configure the CSMS Flask application."""

    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    if test_config is not None:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    resident_repository = ResidentRepository(
        app.config["DATABASE_PATH"]
    )
    service_request_repository = ServiceRequestRepository(
        app.config["DATABASE_PATH"]
    )

    resident_validator = ResidentValidator()

    app.extensions["resident_services"] = {
        "query": ResidentQueryService(resident_repository),
        "registration": ResidentRegistrationService(
            resident_validator,
            resident_repository,
        ),
        "update": ResidentUpdateService(
            resident_validator,
            resident_repository,
        ),
        "deactivation": ResidentDeactivationService(
            resident_repository,
        ),
    }

    app.extensions["service_request_services"] = {
        "query": ServiceRequestQueryService(
            service_request_repository,
        ),
        "submission": ServiceRequestSubmissionService(
            ServiceRequestValidator(),
            resident_repository,
            service_request_repository,
        ),
        "status": ServiceRequestStatusService(
            service_request_repository,
        ),
    }

    # T14: Dashboard service
    app.extensions["dashboard_service"] = DashboardService(
        resident_repository,
        service_request_repository,
    )

    from csms.ui.routes import main_blueprint

    app.register_blueprint(main_blueprint)

    return app
