from dataclasses import dataclass
from datetime import date


@dataclass
class ServiceRequest:
    resident_id: int
    service_type: str
    description: str
    date_requested: date
    id: int | None = None
    status: str = "Pending"