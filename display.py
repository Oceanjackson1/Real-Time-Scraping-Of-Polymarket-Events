from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from models import ScraperSnapshot

CATEGORY_COLORS = {
    "Politics": "red",
    "Crypto": "yellow",
    "Sports": "green",
    "Finance": "cyan",
    "Science": "blue",
    "Entertainment": "magenta",
    "Business": "bright_cyan",
    "Economy": "bright_green",
    "AI": "bright_magenta",
    "Technology": "bright_blue",
    "Culture": "bright_yellow",
    "World": "bright_red",
}


def format_volume(vol: float) -> str:
    if vol >= 1_000_000:
        return f"${vol / 1_000_000:.1f}M"
    elif vol >= 1_000:
        return f"${vol / 1_000:.1f}K"
    else:
        return f"${vol:.0f}"


class Dashboard:
    """Rich terminal dashboard for displaying Polymarket data."""

    def __init__(self):
        self.console = Console()

    def build_header(self, snapshot: ScraperSnapshot) -> Panel:
        header = Text()
        header.append("POLYMARKET REAL-TIME MONITOR", style="bold white")
        header.append("  |  ", style="dim")
        header.append(f"Events: {snapshot.total_events}", style="cyan")
        header.append("  |  ", style="dim")
        header.append(f"Markets: {snapshot.total_markets}", style="green")
        header.append("  |  ", style="dim")
        header.append(f"Total Volume: {format_volume(snapshot.total_volume)}",
                       style="bold yellow")
        header.append("  |  ", style="dim")
        header.append(f"Fetch: {snapshot.fetch_duration_seconds:.1f}s",
                       style="dim")
        header.append("  |  ", style="dim")
        header.append(f"Updated: {snapshot.timestamp}", style="dim")
        return Panel(header, border_style="bright_blue")

    def build_category_summary_table(self,
                                     snapshot: ScraperSnapshot) -> Table:
        table = Table(
            title="Categories Overview",
            box=box.SIMPLE_HEAVY,
            title_style="bold magenta",
            expand=True,
        )
        table.add_column("Category", style="bold", width=18)
        table.add_column("Events", justify="center", width=8)
        table.add_column("Total Volume", justify="right", width=14)
        table.add_column("24h Volume", justify="right", width=14)

        for cat_name, cat_events in snapshot.categories.items():
            cat_vol = sum(e.volume for e in cat_events)
            cat_24h = sum(e.volume_24hr for e in cat_events)
            color = CATEGORY_COLORS.get(cat_name, "white")
            table.add_row(
                Text(cat_name, style=color),
                str(len(cat_events)),
                format_volume(cat_vol),
                format_volume(cat_24h),
            )

        return table

    def build_events_table(self, snapshot: ScraperSnapshot,
                           category_filter: str = None) -> Table:
        title = "Active Polymarket Events"
        if category_filter:
            title += f" [{category_filter}]"

        table = Table(
            title=title,
            box=box.ROUNDED,
            show_lines=True,
            expand=True,
            title_style="bold cyan",
        )
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Title", style="white", max_width=40, no_wrap=True)
        table.add_column("Category", style="magenta", width=14)
        table.add_column("Markets", justify="center", width=8)
        table.add_column("Volume", justify="right", style="green", width=14)
        table.add_column("24h Vol", justify="right", style="yellow", width=12)
        table.add_column("Top Outcome", width=18)
        table.add_column("Price", justify="right", width=8)
        table.add_column("Link", style="blue", max_width=40, no_wrap=True)

        events = snapshot.events
        if category_filter:
            events = [e for e in events if e.category == category_filter]

        events = sorted(events, key=lambda e: e.volume_24hr, reverse=True)

        for idx, event in enumerate(events, 1):
            top_market = max(event.markets, key=lambda m: m.volume,
                             default=None)
            top_outcome = ""
            top_price = ""
            if top_market and top_market.outcome_prices:
                try:
                    prices = [float(p) for p in top_market.outcome_prices]
                    best_idx = prices.index(max(prices))
                    if best_idx < len(top_market.outcomes):
                        top_outcome = top_market.outcomes[best_idx]
                    top_price = f"{max(prices):.1%}"
                except (ValueError, TypeError):
                    pass

            color = CATEGORY_COLORS.get(event.category, "white")
            short_url = event.polymarket_url.replace(
                "https://polymarket.com/event/", "")
            if len(short_url) > 38:
                short_url = short_url[:35] + "..."

            table.add_row(
                str(idx),
                event.title[:40],
                Text(event.category, style=color),
                str(len(event.markets)),
                format_volume(event.volume),
                format_volume(event.volume_24hr),
                top_outcome,
                top_price,
                short_url,
            )

        return table

    def render(self, snapshot: ScraperSnapshot,
               category_filter: str = None) -> Group:
        if snapshot is None:
            return Group(
                Panel(
                    Text("Loading data...", style="dim italic"),
                    border_style="bright_blue",
                )
            )

        return Group(
            self.build_header(snapshot),
            self.build_category_summary_table(snapshot),
            self.build_events_table(snapshot, category_filter),
        )
