from src.csms.models.service_request import ServiceRequest


class ServiceRequestStatusResult:
    def __init__(
        self,
        success: bool,
        service_request: ServiceRequest | None = None,
        error_message: str | None = None,
    ):
        self.success = success
        self.service_request = service_request
        self.error_message = error_message