"""Google News RSS — supplementary catch-all source for Chilean media.

Uses the public Google News RSS search endpoint (no API key required).
Each RSS entry carries a Google redirect URL; this scraper resolves each
one to the actual destination URL so _cmd_merge can deduplicate against
directly-scraped outlets.

Date windowing: _collect_for_phrase loops day-by-day so each RSS call
covers a single day (up to 100 results/day). If a day hits the 100-result
cap a WARNING is logged; pass additional --query phrases to get more
coverage (each phrase gets its own 100-result slot per day).
"""
import logging
from datetime import date, datetime, timedelta
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from scraper.base_api import BaseApiScraper

logger = logging.getLogger(__name__)

_RSS_URL = "https://news.google.com/rss/search"
_RSS_PARAMS = {"hl": "es", "gl": "CL", "ceid": "CL:es"}
_RESOLVE_TIMEOUT = 10


class GoogleNewsScraper(BaseApiScraper):
    SOURCE_SLUG = "google_news"
    REQUEST_TIMEOUT = 30

    def _collect_for_phrase(self, phrase: str, since: date, until: date) -> list[dict]:
        results: list[dict] = []
        seen: set[str] = set()
        day = since
        while day <= until:
            self._since = day
            self._until = day
            for article in super()._collect_for_phrase(phrase, day, day):
                url = article.get("url") or ""
                if url not in seen:
                    seen.add(url)
                    results.append(article)
            day += timedelta(days=1)
        return results

    def _fetch_page(self, query: str, offset: int) -> list[dict]:
        if offset > 0:
            return []
        bounded_query = query
        if hasattr(self, "_since") and self._since:
            bounded_query += f" after:{self._since.strftime('%Y/%m/%d')}"
        if hasattr(self, "_until") and self._until:
            bounded_query += f" before:{self._until.strftime('%Y/%m/%d')}"
        try:
            resp = requests.get(
                _RSS_URL,
                params={**_RSS_PARAMS, "q": bounded_query},
                headers=self.HEADERS,
                timeout=self.REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                logger.warning(
                    f"[{self.SOURCE_SLUG}] RSS HTTP {resp.status_code} for query={query!r}"
                )
                return []
            feed = feedparser.parse(resp.content)
            entries = list(feed.entries)
            logger.info(
                f"[{self.SOURCE_SLUG}] RSS returned {len(entries)} entries for query={query!r}"
            )
            if len(entries) >= 100:
                logger.warning(
                    f"[{self.SOURCE_SLUG}] RSS cap reached (100 results) "
                    f"for query={query!r} on {getattr(self, '_since', '?')} — "
                    f"results may be incomplete; add more --query phrases "
                    f"to increase coverage (each phrase gets its own 100-result slot per day)"
                )
            return entries
        except Exception as e:
            logger.warning(f"[{self.SOURCE_SLUG}] RSS fetch error: {e}")
            return []

    def _map_article(self, raw) -> Optional[dict]:
        titulo = (raw.get("title") or "").strip()
        if not titulo or len(titulo) < 20:
            return None

        redirect_url = raw.get("link") or ""
        if not redirect_url:
            return None

        actual_url = self._resolve_url(redirect_url) or redirect_url

        fecha = None
        if raw.get("published_parsed"):
            try:
                fecha = date(*raw["published_parsed"][:3]).isoformat()
            except Exception:
                pass

        raw_summary = raw.get("summary") or ""
        bajada_text = BeautifulSoup(raw_summary, "lxml").get_text(" ", strip=True)
        source_name = (raw.get("source") or {}).get("title") or ""
        if source_name:
            bajada = f"[{source_name}] {bajada_text}" if bajada_text else f"[{source_name}]"
        else:
            bajada = bajada_text or None
        if bajada and len(bajada) > 500:
            bajada = bajada[:500]

        cuerpo = bajada or titulo

        return {
            "titulo": titulo,
            "cuerpo": cuerpo,
            "bajada": bajada,
            "fecha": fecha,
            "fuente": self.SOURCE_SLUG,
            "url": actual_url,
            "fecha_scraping": datetime.now().isoformat(timespec="seconds"),
            "query": "",
        }

    def _resolve_url(self, redirect_url: str) -> Optional[str]:
        """Follow Google News redirect and return the final destination URL.

        Returns None if resolution fails or stays on news.google.com,
        so the caller can fall back to the redirect URL.
        """
        try:
            resp = requests.head(
                redirect_url,
                allow_redirects=True,
                timeout=_RESOLVE_TIMEOUT,
                headers=self.HEADERS,
            )
            final = resp.url
            if final and not final.startswith("https://news.google.com"):
                return final
            resp2 = requests.get(
                redirect_url,
                allow_redirects=True,
                timeout=_RESOLVE_TIMEOUT,
                headers=self.HEADERS,
                stream=True,
            )
            resp2.close()
            final2 = resp2.url
            return final2 if (final2 and not final2.startswith("https://news.google.com")) else None
        except Exception as e:
            logger.debug(f"[{self.SOURCE_SLUG}] URL resolve failed {redirect_url}: {e}")
            return None
