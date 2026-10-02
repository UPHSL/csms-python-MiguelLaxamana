from src.csms.models.service_request import ServiceRequest
from src.csms.repositories.resident_repository import ResidentRepository
from src.csms.repositories.service_request_repository import ServiceRequestRepository
from src.csms.services.service_request_submission_result import ServiceRequestSubmissionResult
from src.csms.services.service_request_validator import ServiceRequestValidator


class ServiceRequestSubmissionService:
    def __init__(
        self,
        validator: ServiceRequestValidator,
        resident_repository: ResidentRepository,
        service_request_repository: ServiceRequestRepository,
    ):
        self.validator = validator
        self.resident_repository = resident_repository
        self.service_request_repository = service_request_repository

    def submit(self, request: ServiceRequest) -> ServiceRequestSubmissionResult:
        # 1. Validate intrinsic properties
        errors = self.validator.validate(request)
        if errors:
            return ServiceRequestSubmissionResult(
                success=False,
                errors=errors,
            )

        # 2. Verify resident exists
        resident = self.resident_repository.find_by_id(request.resident_id)
        if resident is None:
            return ServiceRequestSubmissionResult(
                success=False,
                error_message="Resident not found",
            )

        # 3. Verify resident is Active
        if resident.status != "Active":
            return ServiceRequestSubmissionResult(
                success=False,
                error_message="Resident is Inactive",
            )

        # 4. Persist valid request
        persisted_request = self.service_request_repository.save(request)

        return ServiceRequestSubmissionResult(
            success=True,
            service_request=persisted_request,
        )