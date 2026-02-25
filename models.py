from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Tag:
    id: str
    label: str
    slug: str


@dataclass
class Market:
    id: str
    question: str
    slug: str
    outcomes: List[str]
    outcome_prices: List[str]
    volume: float
    volume_24hr: float
    liquidity: float
    active: bool
    closed: bool
    end_date: Optional[str]
    polymarket_url: str


@dataclass
class Event:
    id: str
    title: str
    slug: str
    volume: float
    volume_24hr: float
    liquidity: float
    active: bool
    closed: bool
    tags: List[Tag]
    markets: List[Market]
    polymarket_url: str
    category: str
    start_date: Optional[str]
    end_date: Optional[str]


@dataclass
class ScraperSnapshot:
    timestamp: str
    events: List[Event]
    total_events: int
    total_markets: int
    total_volume: float
    categories: dict = field(default_factory=dict)
    fetch_duration_seconds: float = 0.0
