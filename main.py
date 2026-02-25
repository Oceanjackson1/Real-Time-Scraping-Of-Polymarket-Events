import time
import signal
import sys
import logging
import argparse

from rich.live import Live

from config import (GAMMA_BASE_URL, REFRESH_INTERVAL_SECONDS,
                    API_PAGE_LIMIT, MAX_PAGES, REQUEST_DELAY_SECONDS)
from api_client import GammaAPIClient
from data_processor import DataProcessor
from display import Dashboard
from exporter import Exporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Real-time Polymarket Events Scraper"
    )
    parser.add_argument(
        "--interval", type=int, default=REFRESH_INTERVAL_SECONDS,
        help="Refresh interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export data to CSV and JSON on each refresh",
    )
    parser.add_argument(
        "--export-once", action="store_true",
        help="Scrape once, export, and exit (no dashboard)",
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Filter by category (e.g., Politics, Crypto)",
    )
    return parser.parse_args()


def scrape_cycle(client: GammaAPIClient) -> 'ScraperSnapshot':
    start = time.time()
    raw_events = client.fetch_all_active_events()
    duration = time.time() - start
    return DataProcessor.build_snapshot(raw_events, duration)


def main():
    args = parse_args()
    client = GammaAPIClient(
        base_url=GAMMA_BASE_URL,
        page_limit=API_PAGE_LIMIT,
        max_pages=MAX_PAGES,
        request_delay=REQUEST_DELAY_SECONDS,
    )
    dashboard = Dashboard()
    exporter = Exporter()

    # --export-once mode: scrape, export, exit
    if args.export_once:
        snapshot = scrape_cycle(client)
        csv_path = exporter.export_csv(snapshot)
        json_path = exporter.export_json(snapshot)
        print(f"\nScraped {snapshot.total_events} events, "
              f"{snapshot.total_markets} markets")
        print(f"Total Volume: ${snapshot.total_volume:,.2f}")
        print(f"\nExported to:")
        print(f"  CSV:  {csv_path}")
        print(f"  JSON: {json_path}")
        return

    # Live dashboard mode
    shutdown = False

    def signal_handler(sig, frame):
        nonlocal shutdown
        shutdown = True

    signal.signal(signal.SIGINT, signal_handler)

    with Live(
        dashboard.render(None),
        refresh_per_second=1,
        screen=False,
        console=dashboard.console,
    ) as live:
        while not shutdown:
            try:
                snapshot = scrape_cycle(client)
                live.update(dashboard.render(snapshot, args.category))
                logger.info(
                    "Scraped %d events, %d markets in %.1fs",
                    snapshot.total_events,
                    snapshot.total_markets,
                    snapshot.fetch_duration_seconds,
                )

                if args.export:
                    csv_path = exporter.export_csv(snapshot)
                    json_path = exporter.export_json(snapshot)
                    logger.info("Exported: %s, %s", csv_path, json_path)

                # Wait with 1-second granularity for responsive shutdown
                for _ in range(args.interval):
                    if shutdown:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error("Scrape cycle failed: %s", e, exc_info=True)
                time.sleep(5)

    print("\nShutdown complete. Goodbye.")


if __name__ == "__main__":
    main()
