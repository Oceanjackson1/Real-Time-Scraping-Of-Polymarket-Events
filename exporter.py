import csv
import json
import os
from dataclasses import asdict
from datetime import datetime

from models import ScraperSnapshot
from config import EXPORT_DIR


class Exporter:
    """Exports scraped data to CSV and JSON files."""

    def __init__(self):
        os.makedirs(EXPORT_DIR, exist_ok=True)

    def export_csv(self, snapshot: ScraperSnapshot) -> str:
        filepath = self._generate_filename("polymarket_events_{}.csv")
        rows = []
        for event in snapshot.events:
            top_market = max(event.markets, key=lambda m: m.volume,
                             default=None)
            row = {
                "event_id": event.id,
                "title": event.title,
                "category": event.category,
                "tags": "; ".join(t.label for t in event.tags),
                "num_markets": len(event.markets),
                "total_volume": round(event.volume, 2),
                "volume_24hr": round(event.volume_24hr, 2),
                "liquidity": round(event.liquidity, 2),
                "top_market_question": top_market.question if top_market else "",
                "top_outcome": "",
                "top_price": "",
                "polymarket_url": event.polymarket_url,
                "scraped_at": snapshot.timestamp,
            }
            if top_market and top_market.outcome_prices:
                try:
                    prices = [float(p) for p in top_market.outcome_prices]
                    best_idx = prices.index(max(prices))
                    if best_idx < len(top_market.outcomes):
                        row["top_outcome"] = top_market.outcomes[best_idx]
                    row["top_price"] = round(max(prices), 4)
                except (ValueError, TypeError):
                    pass
            rows.append(row)

        if rows:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        return filepath

    def export_json(self, snapshot: ScraperSnapshot) -> str:
        filepath = self._generate_filename("polymarket_events_{}.json")
        data = {
            "scraped_at": snapshot.timestamp,
            "total_events": snapshot.total_events,
            "total_markets": snapshot.total_markets,
            "total_volume": round(snapshot.total_volume, 2),
            "fetch_duration_seconds": snapshot.fetch_duration_seconds,
            "categories": {
                cat: [asdict(e) for e in events]
                for cat, events in snapshot.categories.items()
            },
            "events": [asdict(e) for e in snapshot.events],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def _generate_filename(self, template: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(EXPORT_DIR, template.format(timestamp))
