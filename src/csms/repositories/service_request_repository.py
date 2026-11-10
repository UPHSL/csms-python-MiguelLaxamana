from datetime import date

from src.csms.database import get_connection
from src.csms.models.service_request import ServiceRequest


class ServiceRequestRepository:

    def _row_to_service_request(self, row) -> ServiceRequest:
        req_date = row["date_requested"]

        if isinstance(req_date, str):
            req_date = date.fromisoformat(req_date)

        return ServiceRequest(
            id=row["id"],
            resident_id=row["resident_id"],
            service_type=row["service_type"],
            description=row["description"],
            date_requested=req_date,
            status=row["status"],
        )

    def save(self, request: ServiceRequest) -> ServiceRequest:
        conn = get_connection()

        try:
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

            return request
        finally:
            conn.close()

    def find_by_id(self, request_id: int) -> ServiceRequest | None:
        conn = get_connection()

        try:
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

            if row is None:
                return None

            return self._row_to_service_request(row)
        finally:
            conn.close()

    def find_all(
        self,
        search_term: str | None = None,
        status: str | None = None,
    ) -> list[ServiceRequest]:
        conn = get_connection()

        try:
            cursor = conn.cursor()

            query = """
                SELECT
                    id,
                    resident_id,
                    service_type,
                    description,
                    date_requested,
                    status
                FROM service_requests
            """

            conditions = []
            parameters = []

            if search_term:
                conditions.append(
                    """
                    (
                        service_type LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                    )
                    """
                )

                search_pattern = f"%{search_term}%"
                parameters.extend([search_pattern, search_pattern])

            if status:
                conditions.append("status = ?")
                parameters.append(status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                ORDER BY date_requested DESC, id DESC
            """

            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                self._row_to_service_request(row)
                for row in rows
            ]
        finally:
            conn.close()

    def update_status(
        self,
        request_id: int,
        status: str,
    ) -> ServiceRequest | None:
        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE service_requests
                SET status = ?
                WHERE id = ?
                """,
                (status, request_id),
            )

            if cursor.rowcount == 0:
                return None

            conn.commit()
        finally:
            conn.close()

        return self.find_by_id(request_id)