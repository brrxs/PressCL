"""PressCL — centralised constants.

Every magic number, project-level string and schema definition lives here so
that outlet scrapers, the CLI, the GUI, and utility modules all share a single
source of truth.
"""

# ── Project identity ──────────────────────────────────────────────────────────
PROJECT_NAME = "PressCL"
PROJECT_VERSION = "0.5"

# ── User-Agent strings ────────────────────────────────────────────────────────
# Bot-style UA used by HTML/API scrapers and robots.txt checks.
USER_AGENT = f"Mozilla/5.0 (compatible; {PROJECT_NAME}/{PROJECT_VERSION}; +https://github.com/theChosen16/PressCL)"

# Browser-realistic UA used by Playwright scrapers and Google News enrichment.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ── Article validation ────────────────────────────────────────────────────────
MIN_TITULO_LEN = 20
MIN_CUERPO_LEN = 400

# ── Pagination caps ───────────────────────────────────────────────────────────
HARD_PAGE_CAP = 50      # max listing/search pages per outlet (HTML scrapers)
HARD_OFFSET_CAP = 500   # max articles per API phrase-run

# ── Output schema ─────────────────────────────────────────────────────────────
SCHEMA = [
    "titulo",
    "cuerpo",
    "bajada",
    "fecha",
    "fuente",
    "url",
    "fecha_scraping",
    "query",
]
