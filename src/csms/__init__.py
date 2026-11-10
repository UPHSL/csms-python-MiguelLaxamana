"""Community Services Management System Flask application."""

from flask import Flask

from csms.config import DevelopmentConfig
from csms.database import initialize_database
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_deactivation_service import (
    ResidentDeactivationService,
)
from csms.services.resident_query_service import (
    ResidentQueryService,
)
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_update_service import (
    ResidentUpdateService,
)
from csms.services.resident_validator import ResidentValidator


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    """Create and configure the CSMS Flask application."""

    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    if test_config is not None:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    repository = ResidentRepository(
        app.config["DATABASE_PATH"]
    )
    validator = ResidentValidator()

    app.extensions["resident_services"] = {
        "query": ResidentQueryService(repository),
        "registration": ResidentRegistrationService(
            validator,
            repository,
        ),
        "update": ResidentUpdateService(
            validator,
            repository,
        ),
        "deactivation": ResidentDeactivationService(repository),
    }

    from csms.ui.routes import main_blueprint

    app.register_blueprint(main_blueprint)

    return app