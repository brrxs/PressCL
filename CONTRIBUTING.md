# Contributing to PressCL

This is a personal project — contributions are welcome but reviewed best-effort.

## Adding a new outlet

Each outlet lives in `app/scraper/outlets/<slug>.py`. Three base classes cover the three scraper types:

### 1. `BaseScraper` — HTML scraping (most outlets)

Subclass this for outlets with a standard HTML listing page and article pages.

```python
from scraper.base import BaseScraper

class MyOutlet(BaseScraper):
    SOURCE_SLUG = "myoutlet"
    SEARCH_URL_TEMPLATE = "https://myoutlet.cl/search?q={query}&page={page}"
    INDEX_URL_TEMPLATE  = "https://myoutlet.cl/noticias/page/{page}/"  # feed fallback

    # CSS selectors
    link_selector     = "a.article-title"        # links on listing page
    title_selector    = "h1.entry-title"          # headline on article page
    date_selector     = "time[datetime]"          # date element (datetime attr or text)
    body_selector     = "div.entry-content p"     # body paragraphs
    subtitle_selector = "p.standfirst"            # optional; None if absent
```

Required abstract properties: `link_selector`, `title_selector`, `date_selector`, `body_selector`.

Optional overrides: `subtitle_selector` (default `None`), `DELAY_MIN`/`DELAY_MAX`, `REQUEST_TIMEOUT`, `HEADERS`.

If the outlet's date isn't in a standard HTML element (e.g., it's in the canonical URL), override `_parse_date_from_article(soup, url)`.

### 2. `BaseApiScraper` — JSON API outlets (Biobío, Emol)

Use when the outlet exposes a hidden JSON search API (check XHR requests in browser DevTools).

```python
from scraper.base_api import BaseApiScraper

class MyApiOutlet(BaseApiScraper):
    SOURCE_SLUG = "myoutlet"
    API_URL     = "https://myoutlet.cl/api/search"

    def _build_params(self, query: str, page: int) -> dict:
        return {"q": query, "page": page, "size": 20}

    def _parse_response(self, data: dict) -> list[dict]:
        # Return a list of dicts with keys: titulo, cuerpo, bajada, fecha, url
        return [
            {"titulo": a["title"], "cuerpo": a["body"], "bajada": "",
             "fecha": a["date"][:10], "url": a["url"]}
            for a in data.get("results", [])
        ]
```

### 3. `BasePlaywrightScraper` — JS-rendered outlets (T13, 24 Horas, CHV)

Use only when the site requires JavaScript execution. These are slower and use a real Chromium browser.

```python
from scraper.base_playwright import BasePlaywrightScraper

class MyJsOutlet(BasePlaywrightScraper):
    SOURCE_SLUG = "myoutlet"
    LISTING_URL = "https://myoutlet.cl/noticias/"

    def _extract_links(self, page) -> list[str]:
        return [el.get_attribute("href") for el in page.query_selector_all("a.news-link")]

    def _parse_article(self, page, url: str) -> dict | None:
        # Return dict with titulo, cuerpo, bajada, fecha, url — or None to skip
        ...
```

### Registering the outlet

Add the new class to `app/scraper/outlets/__init__.py`:

```python
from scraper.outlets.myoutlet import MyOutlet
```

And register it in `app/run.py` in the `OUTLET_REGISTRY` dict:

```python
"myoutlet": MyOutlet,
```

### Testing your outlet

```powershell
cd app
python run.py check myoutlet
```

This fetches the listing page and one article, prints all parsed fields, and shows any warnings — without saving data. Fix selector issues until `check` returns a clean article with `titulo`, `cuerpo`, `fecha`, and `url` all populated.

Then do a short live scrape:

```powershell
python run.py run myoutlet --query "prueba" --days 3 --progress
```

## Reporting broken selectors

If an outlet stops returning articles, it likely means the site redesigned their HTML. Open an issue with:

- The outlet slug
- Output of `python run.py check <slug>`
- The date you noticed the breakage

## Code style

- Python 3.10+, type hints encouraged.
- No external formatter is enforced — keep consistent with the surrounding file.
- New outlet files should follow the pattern of the nearest existing equivalent (e.g., model a new HTML outlet on `elmostrador.py`, a new API outlet on `biobio.py`).
