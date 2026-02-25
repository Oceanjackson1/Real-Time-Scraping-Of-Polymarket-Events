import time
import logging
from typing import List, Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)


class GammaAPIClient:
    """Client for the Polymarket Gamma API."""

    def __init__(self, base_url: str, page_limit: int, max_pages: int,
                 request_delay: float):
        self.base_url = base_url
        self.page_limit = page_limit
        self.max_pages = max_pages
        self.request_delay = request_delay
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PolymarketScraper/1.0",
        })

    def _get(self, endpoint: str, params: dict = None,
             max_retries: int = 3) -> Optional[Any]:
        """Single GET request with retry and exponential backoff."""
        url = f"{self.base_url}{endpoint}"
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning("Rate limited. Waiting %ds...", wait)
                    time.sleep(wait)
                elif response.status_code >= 500:
                    wait = 2 ** attempt
                    logger.warning("Server error %d. Retry in %ds",
                                   response.status_code, wait)
                    time.sleep(wait)
                else:
                    logger.error("Request failed: %d %s",
                                 response.status_code, url)
                    return None
            except requests.exceptions.RequestException as e:
                wait = 2 ** attempt
                logger.error("Request exception: %s. Retry in %ds", e, wait)
                time.sleep(wait)
        return None

    def fetch_all_active_events(self) -> List[Dict[str, Any]]:
        """Paginate through all active, non-closed events."""
        all_events: List[Dict[str, Any]] = []
        for page in range(self.max_pages):
            offset = page * self.page_limit
            params = {
                "active": "true",
                "closed": "false",
                "order": "volume24hr",
                "ascending": "false",
                "limit": self.page_limit,
                "offset": offset,
            }
            page_data = self._get("/events", params=params)
            if page_data is None:
                logger.error("Failed to fetch page %d. Stopping.", page)
                break
            all_events.extend(page_data)
            if len(page_data) < self.page_limit:
                break
            time.sleep(self.request_delay)
        return all_events

    def fetch_tags(self) -> List[Dict[str, Any]]:
        """Fetch all available tags."""
        result = self._get("/tags")
        return result if result else []


if __name__ == "__main__":
    from config import (GAMMA_BASE_URL, API_PAGE_LIMIT,
                        MAX_PAGES, REQUEST_DELAY_SECONDS)

    logging.basicConfig(level=logging.INFO)
    client = GammaAPIClient(GAMMA_BASE_URL, API_PAGE_LIMIT,
                            MAX_PAGES, REQUEST_DELAY_SECONDS)
    events = client.fetch_all_active_events()
    print(f"Fetched {len(events)} events")
    if events:
        print(f"First event: {events[0].get('title', 'N/A')}")
        tags = events[0].get("tags", [])
        print(f"Tags: {[t.get('label') for t in tags]}")
