
from csms.models.service_request import ServiceRequest
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


class ServiceRequestQueryService:
    SUPPORTED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    def __init__(
        self,
        repository: ServiceRequestRepository,
    ) -> None:
        self.repository = repository

    def list_service_requests(
        self,
        search_term: str | None = None,
        status: str | None = None,
    ) -> list[ServiceRequest]:
        normalized_search_term = (
            "" if search_term is None
            else search_term.strip()
        )

        normalized_status = (
            None if status is None or not status.strip()
            else status.strip()
        )

        if (
            normalized_status is not None
            and normalized_status not in self.SUPPORTED_STATUSES
        ):
            raise ValueError("Unsupported service request status")

        return self.repository.find_all(
            search_term=normalized_search_term or None,
            status=normalized_status,
        )

    def get_service_request(
        self,
        request_id: int,
    ) -> ServiceRequest | None:
        return self.repository.find_by_id(request_id)
