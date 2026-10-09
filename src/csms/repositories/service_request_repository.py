from datetime import date

from src.csms.database import get_connection
from src.csms.models.service_request import ServiceRequest


class ServiceRequestRepository:
    def save(self, request: ServiceRequest) -> ServiceRequest:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO service_requests (
                resident_id,
                service_type,
                description,
                date_requested,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.resident_id,
                request.service_type,
                request.description,
                request.date_requested.isoformat()
                if isinstance(request.date_requested, date)
                else str(request.date_requested),
                request.status,
            ),
        )

        conn.commit()
        request.id = cursor.lastrowid
        conn.close()

        return request

    def find_by_id(self, request_id: int) -> ServiceRequest | None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                resident_id,
                service_type,
                description,
                date_requested,
                status
            FROM service_requests
            WHERE id = ?
            """,
            (request_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        req_date = row["date_requested"]

        if isinstance(req_date, str):
            req_date = date.fromisoformat(req_date)

        return ServiceRequest(
            resident_id=row["resident_id"],
            service_type=row["service_type"],
            description=row["description"],
            date_requested=req_date,
            id=row["id"],
            status=row["status"],
        )