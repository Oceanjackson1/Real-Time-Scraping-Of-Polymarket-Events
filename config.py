# API endpoints
GAMMA_BASE_URL = "https://gamma-api.polymarket.com"
EVENTS_ENDPOINT = "/events"
MARKETS_ENDPOINT = "/markets"
TAGS_ENDPOINT = "/tags"

# Polymarket website base URL for constructing market links
POLYMARKET_BASE_URL = "https://polymarket.com/event"

# Scraper settings
REFRESH_INTERVAL_SECONDS = 30
API_PAGE_LIMIT = 100
MAX_PAGES = 50

# Rate limiting (conservative delay between paginated requests)
REQUEST_DELAY_SECONDS = 0.05

# Export settings
EXPORT_DIR = "exports"
