import re
from datetime import date
from typing import Optional
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from scraper.base import BaseScraper

# El Ciudadano URLs end in /MM/DD/ with no year, e.g.
# https://www.elciudadano.com/chile/some-slug/07/02/
_MMDD_RE = re.compile(r"/(\d{2})/(\d{2})/?$")

# Each article is republished as /en/ and /deustche/ translations; only the
# Spanish original is worth scraping.
_TRANSLATION_PREFIXES = ("/en/", "/deustche/")


class ElCiudadanoScraper(BaseScraper):
    SOURCE_SLUG = "elciudadano"
    INDEX_URL_TEMPLATE = "https://www.elciudadano.com/page/{page}"
    SEARCH_URL_TEMPLATE = "https://www.elciudadano.com/?s={query}&orderby=date&order=DESC&paged={page}"

    @property
    def link_selector(self): return "article a[href*='elciudadano.com']"

    @property
    def title_selector(self): return "h1"

    @property
    def date_selector(self): return "time"

    @property
    def body_selector(self): return "div[class*='content'] p"

    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        links = super()._extract_links(soup)
        return [
            u for u in links
            if not urlsplit(u).path.startswith(_TRANSLATION_PREFIXES)
        ]

    def _link_date(self, url: str) -> Optional[date]:
        d = super()._link_date(url)
        if d is not None:
            return d
        m = _MMDD_RE.search(urlsplit(url).path)
        if m is None:
            return None
        month, day = int(m.group(1)), int(m.group(2))
        today = date.today()
        # No year in the URL: assume the most recent past occurrence of MM/DD.
        for year in (today.year, today.year - 1):
            try:
                d = date(year, month, day)
            except ValueError:
                continue
            if d <= today:
                return d
        return None

    def _date_text(self, soup: BeautifulSoup) -> Optional[str]:
        # 1. Open Graph meta tag (most reliable — WordPress always publishes this)
        val = self._meta_date(soup)
        if val:
            return val
        # 2. <time datetime="..."> attribute
        el = soup.select_one(self.date_selector)
        if el is not None:
            dt_attr = el.get("datetime")
            if dt_attr:
                return dt_attr
            text = el.get_text(strip=True)
            if text:
                return text
        # 3. URL path /YYYY/MM/DD/
        return self._url_date_from_soup(soup)
