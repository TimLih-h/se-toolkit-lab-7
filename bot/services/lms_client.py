"""LMS API client service with all 9 endpoints as tools."""

import httpx
from typing import Any


class LMSClient:
    """Client for the LMS backend API with tool methods."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API.
            api_key: API key for Bearer token authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    def get_items(self) -> list[dict]:
        """Get all items (labs and tasks) from the backend."""
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list[dict]:
        """Get enrolled students and groups."""
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict]:
        """Get score distribution (4 buckets) for a lab."""
        response = self._client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Get per-task averages and attempt counts for a lab."""
        response = self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: str) -> list[dict]:
        """Get submissions per day for a lab."""
        response = self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict]:
        """Get per-group scores and student counts for a lab."""
        response = self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 5) -> list[dict]:
        """Get top N learners by score for a lab."""
        response = self._client.get(
            "/analytics/top-learners",
            params={"lab": lab, "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate percentage for a lab."""
        response = self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger ETL sync to refresh data from autochecker."""
        response = self._client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check if the backend is healthy."""
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}


def create_lms_client(base_url: str, api_key: str) -> LMSClient:
    """Create an LMS client instance."""
    return LMSClient(base_url, api_key)
