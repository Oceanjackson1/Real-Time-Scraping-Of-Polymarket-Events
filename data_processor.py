import re
from datetime import datetime, timezone
from typing import List, Dict

from models import Tag, Market, Event, ScraperSnapshot
from config import POLYMARKET_BASE_URL

PRIORITY_TAGS = [
    "Politics", "Crypto", "Sports", "Finance",
    "Science", "Entertainment", "Business", "Economy",
    "AI", "Technology", "Culture", "World",
]


class DataProcessor:
    """Transforms raw Gamma API data into structured, categorized objects."""

    @staticmethod
    def parse_market(raw: dict, event_slug: str) -> Market:
        slug = raw.get("slug", "")
        outcomes = raw.get("outcomes", [])
        if isinstance(outcomes, str):
            try:
                import json
                outcomes = json.loads(outcomes)
            except Exception:
                outcomes = []

        outcome_prices = raw.get("outcomePrices", [])
        if isinstance(outcome_prices, str):
            try:
                import json
                outcome_prices = json.loads(outcome_prices)
            except Exception:
                outcome_prices = []

        volume = 0.0
        try:
            volume = float(raw.get("volumeNum") or raw.get("volume") or 0)
        except (ValueError, TypeError):
            pass

        volume_24hr = 0.0
        try:
            volume_24hr = float(raw.get("volume24hr", 0) or 0)
        except (ValueError, TypeError):
            pass

        liquidity = 0.0
        try:
            liquidity = float(raw.get("liquidity", 0) or 0)
        except (ValueError, TypeError):
            pass

        url = ""
        if event_slug and slug:
            url = f"{POLYMARKET_BASE_URL}/{event_slug}/{slug}"
        elif event_slug:
            url = f"{POLYMARKET_BASE_URL}/{event_slug}"

        resolved_by = raw.get("resolvedBy") or ""
        uma_bond = None
        uma_reward = None
        try:
            if raw.get("umaBond") is not None:
                uma_bond = float(raw["umaBond"])
        except (ValueError, TypeError):
            pass
        try:
            if raw.get("umaReward") is not None:
                uma_reward = float(raw["umaReward"])
        except (ValueError, TypeError):
            pass

        oracle_type = "UMA" if uma_bond is not None else "Unknown"
        oracle_link = (f"https://polygonscan.com/address/{resolved_by}"
                       if resolved_by else "")

        if oracle_type == "Unknown":
            desc = raw.get("description", "")
            cl_match = re.search(r'https?://data\.chain\.link/[^\s,)"]+', desc)
            if cl_match:
                oracle_type = "Chainlink"
                oracle_link = cl_match.group(0).rstrip(".")

        return Market(
            id=raw.get("id", ""),
            question=raw.get("question", ""),
            slug=slug,
            outcomes=outcomes,
            outcome_prices=outcome_prices,
            volume=volume,
            volume_24hr=volume_24hr,
            liquidity=liquidity,
            active=raw.get("active", False),
            closed=raw.get("closed", False),
            end_date=raw.get("endDate"),
            polymarket_url=url,
            description=raw.get("description", ""),
            resolved_by=resolved_by or None,
            oracle_type=oracle_type,
            oracle_link=oracle_link,
            uma_bond=uma_bond,
            uma_reward=uma_reward,
            created_at=raw.get("createdAt"),
        )

    @staticmethod
    def parse_event(raw: dict) -> Event:
        tags = [
            Tag(
                id=str(t.get("id", "")),
                label=t.get("label", ""),
                slug=t.get("slug", ""),
            )
            for t in raw.get("tags", [])
        ]

        slug = raw.get("slug", "")
        markets = [
            DataProcessor.parse_market(m, slug)
            for m in raw.get("markets", [])
        ]

        category = DataProcessor.determine_category(tags)

        volume = sum(m.volume for m in markets) if markets else 0.0
        volume_24hr = sum(m.volume_24hr for m in markets) if markets else 0.0
        liquidity = sum(m.liquidity for m in markets) if markets else 0.0

        return Event(
            id=str(raw.get("id", "")),
            title=raw.get("title", ""),
            slug=slug,
            volume=volume,
            volume_24hr=volume_24hr,
            liquidity=liquidity,
            active=raw.get("active", False),
            closed=raw.get("closed", False),
            tags=tags,
            markets=markets,
            polymarket_url=f"{POLYMARKET_BASE_URL}/{slug}" if slug else "",
            category=category,
            start_date=raw.get("startDate"),
            end_date=raw.get("endDate"),
            description=raw.get("description", ""),
            created_at=raw.get("createdAt"),
        )

    @staticmethod
    def determine_category(tags: List[Tag]) -> str:
        labels = [t.label for t in tags if t.label and t.label != "All"]
        for priority in PRIORITY_TAGS:
            for label in labels:
                if label.lower() == priority.lower():
                    return priority
        return labels[0] if labels else "Uncategorized"

    @staticmethod
    def categorize_events(events: List[Event]) -> Dict[str, List[Event]]:
        categories: Dict[str, List[Event]] = {}
        for event in events:
            categories.setdefault(event.category, []).append(event)
        return dict(sorted(categories.items()))

    @staticmethod
    def build_snapshot(raw_events: List[dict],
                       fetch_duration: float) -> ScraperSnapshot:
        all_events = [DataProcessor.parse_event(raw) for raw in raw_events]
        seen_ids: set = set()
        events: List[Event] = []
        for e in all_events:
            if e.id not in seen_ids:
                seen_ids.add(e.id)
                events.append(e)
        total_markets = sum(len(e.markets) for e in events)
        total_volume = sum(e.volume for e in events)
        categories = DataProcessor.categorize_events(events)

        return ScraperSnapshot(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            events=events,
            total_events=len(events),
            total_markets=total_markets,
            total_volume=total_volume,
            categories=categories,
            fetch_duration_seconds=fetch_duration,
        )


if __name__ == "__main__":
    import logging
    from api_client import GammaAPIClient
    from config import (GAMMA_BASE_URL, API_PAGE_LIMIT,
                        MAX_PAGES, REQUEST_DELAY_SECONDS)

    logging.basicConfig(level=logging.INFO)
    client = GammaAPIClient(GAMMA_BASE_URL, API_PAGE_LIMIT,
                            MAX_PAGES, REQUEST_DELAY_SECONDS)
    raw = client.fetch_all_active_events()
    snapshot = DataProcessor.build_snapshot(raw, 0.0)
    print(f"Events: {snapshot.total_events}")
    print(f"Markets: {snapshot.total_markets}")
    print(f"Total Volume: ${snapshot.total_volume:,.2f}")
    print("\nCategories:")
    for cat, evts in snapshot.categories.items():
        cat_vol = sum(e.volume for e in evts)
        print(f"  {cat}: {len(evts)} events (${cat_vol:,.0f})")
