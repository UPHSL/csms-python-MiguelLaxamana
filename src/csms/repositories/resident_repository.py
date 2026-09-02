from csms.database import get_connection
from csms.models.resident import Resident


class ResidentRepository:
    def __init__(self, database_path=None):
        self.database_path = database_path

    def save(self, resident: Resident) -> Resident:
        connection = get_connection(self.database_path) if self.database_path else get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO residents (
                    first_name,
                    last_name,
                    address,
                    contact_number,
                    email,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    resident.first_name,
                    resident.last_name,
                    resident.address,
                    resident.contact_number,
                    resident.email,
                    resident.status,
                ),
            )

            connection.commit()
            resident.id = cursor.lastrowid
            return resident
        finally:
            connection.close()

    def find_by_id(self, resident_id: int) -> Resident | None:
        connection = get_connection(self.database_path) if self.database_path else get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    address,
                    contact_number,
                    email,
                    status
                FROM residents
                WHERE id = ?
                """,
                (resident_id,),
            ).fetchone()

            if row is None:
                return None

            return Resident(
                first_name=row["first_name"],
                last_name=row["last_name"],
                address=row["address"],
                contact_number=row["contact_number"],
                email=row["email"],
                status=row["status"],
                id=row["id"],
            )
        finally:
            connection.close()