from csms.repositories.resident_repository import (
    ResidentRepository,
)
from csms.services.resident_deactivation_result import (
    ResidentDeactivationResult,
)


class ResidentDeactivationService:
    def __init__(
        self,
        repository: ResidentRepository,
    ) -> None:
        self.repository = repository

    def deactivate_resident(
        self,
        resident_id: int,
    ) -> ResidentDeactivationResult:
        existing_resident = (
            self.repository.find_by_id(
                resident_id
            )
        )

        if existing_resident is None:
            return (
                ResidentDeactivationResult.resident_not_found()
            )

        if existing_resident.status == "Inactive":
            return (
                ResidentDeactivationResult.already_inactive_result(
                    existing_resident
                )
            )

        deactivated_resident = (
            self.repository.deactivate_by_id(
                resident_id
            )
        )

        if deactivated_resident is None:
            return (
                ResidentDeactivationResult.resident_not_found()
            )

        return (
            ResidentDeactivationResult.successful(
                deactivated_resident
            )
        )