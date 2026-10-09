from src.csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from src.csms.services.service_request_status_result import (
    ServiceRequestStatusResult,
)


class ServiceRequestStatusService:
    SUPPORTED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    ALLOWED_TRANSITIONS = {
        "Pending": {"In Progress", "Cancelled"},
        "In Progress": {"Completed", "Cancelled"},
        "Completed": set(),
        "Cancelled": set(),
    }

    def __init__(
        self,
        service_request_repository: ServiceRequestRepository,
    ):
        self.service_request_repository = service_request_repository

    def update_status(
        self,
        request_id: int,
        target_status: str,
    ) -> ServiceRequestStatusResult:
        # 1. Check whether the request exists.
        request = self.service_request_repository.find_by_id(request_id)

        if request is None:
            return ServiceRequestStatusResult(
                success=False,
                error_message="Service request not found",
            )

        # 2. Validate the requested target status.
        if target_status not in self.SUPPORTED_STATUSES:
            return ServiceRequestStatusResult(
                success=False,
                error_message="Unsupported target status",
            )

        # 3. Validate the transition before changing the database.
        allowed_statuses = self.ALLOWED_TRANSITIONS.get(request.status, set())

        if target_status not in allowed_statuses:
            return ServiceRequestStatusResult(
                success=False,
                error_message="Invalid status transition",
            )

        # 4. Persist only a valid status transition.
        updated_request = self.service_request_repository.update_status(
            request_id,
            target_status,
        )

        if updated_request is None:
            return ServiceRequestStatusResult(
                success=False,
                error_message="Service request not found",
            )

        return ServiceRequestStatusResult(
            success=True,
            service_request=updated_request,
        )