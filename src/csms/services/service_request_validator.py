from datetime import date

from src.csms.models.service_request import ServiceRequest


class ServiceRequestValidator:
    def validate(self, request: ServiceRequest) -> dict[str, str]:
        errors = {}

        # Rule 1: ID must be unassigned before submission
        if request.id is not None:
            errors["id"] = "Service Request ID must be unassigned before submission."

        # Rule 2: Resident ID must be valid
        if (
            not isinstance(request.resident_id, int)
            or request.resident_id <= 0
        ):
            errors["resident_id"] = "Valid Resident ID is required."

        # Rule 3: Service Type is required and cannot be blank/whitespace
        if not request.service_type or not request.service_type.strip():
            errors["service_type"] = "Service type is required."

        # Rule 4: Description is required and cannot be blank/whitespace
        if not request.description or not request.description.strip():
            errors["description"] = "Description is required."

        # Rule 5: Date requested is required and must be a valid date
        if not isinstance(request.date_requested, date):
            errors["date_requested"] = "Valid date requested is required."

        # Rule 6: Status must be Pending
        if request.status != "Pending":
            errors["status"] = "New service request status must be Pending."

        return errors