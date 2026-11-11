class DashboardService:
    """Compose repository dashboard data for the UI."""

    def __init__(
        self,
        resident_repository,
        service_request_repository,
    ) -> None:
        self.resident_repository = resident_repository
        self.service_request_repository = service_request_repository

    def get_dashboard_data(self) -> dict:
        """Return dashboard counts and the five most recent requests."""
        resident_counts = (
            self.resident_repository.get_dashboard_counts()
        )
        request_counts = (
            self.service_request_repository.get_dashboard_counts()
        )
        recent_requests = (
            self.service_request_repository.find_recent(limit=5)
        )

        return {
            "resident_counts": resident_counts,
            "request_counts": request_counts,
            "open_requests": (
                request_counts["pending"]
                + request_counts["in_progress"]
            ),
            "recent_requests": recent_requests,
        }