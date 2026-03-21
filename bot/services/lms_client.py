"""LMS API client service."""

import httpx
from typing import Optional


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002).
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
        """Get all items (labs and tasks) from the backend.
        
        Returns:
            List of items with their metadata.
            
        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Get pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04").
            
        Returns:
            List of pass rate statistics per task.
            
        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self._client.get(
            "/analytics/pass-rates",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check if the backend is healthy.
        
        Returns:
            Health status with item count.
            
        Raises:
            httpx.HTTPError: If the API request fails.
        """
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}


def create_lms_client(base_url: str, api_key: str) -> LMSClient:
    """Create an LMS client instance.
    
    Args:
        base_url: Base URL of the LMS API.
        api_key: API key for authentication.
        
    Returns:
        Configured LMSClient instance.
    """
    return LMSClient(base_url, api_key)
