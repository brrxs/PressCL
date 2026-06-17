"""Thread-safe per-host robots.txt checker for HTML scrapers.

API scrapers (BaseApiScraper) consume explicit JSON data endpoints and are
intentionally exempt; this module is only used by the HTML choke points
(BaseScraper._fetch and BasePlaywrightScraper._pw_get).
"""

import logging
import threading
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import requests

from scraper.config import PROJECT_NAME

logger = logging.getLogger(__name__)

BOT_UA = PROJECT_NAME

_cache: dict[str, RobotFileParser | None] = {}
_lock = threading.Lock()


def _robots_for(host_root: str) -> RobotFileParser | None:
    with _lock:
        if host_root in _cache:
            return _cache[host_root]

        rp = RobotFileParser()
        try:
            resp = requests.get(
                host_root + "/robots.txt",
                timeout=10,
                headers={"User-Agent": BOT_UA},
            )
            if resp.status_code == 200:
                # Decode as utf-8-sig: some sites (e.g. emol.com) serve
                # robots.txt with a UTF-8 BOM and no charset header, so
                # requests falls back to latin-1 and leaves stray bytes
                # that corrupt the first "User-agent: *" line.
                text = resp.content.decode("utf-8-sig", errors="replace")
                rp.parse(text.splitlines())
            # Any non-200 (404, 403, etc.) leaves rp empty, which means
            # can_fetch() returns True (allow-all). This treats all
            # non-200 responses as fail-open, per the project's decision.
        except requests.RequestException:
            rp = None

        _cache[host_root] = rp
        return rp


def can_fetch(url: str) -> bool:
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return True

    host_root = f"{parts.scheme}://{parts.netloc}"
    rp = _robots_for(host_root)
    if rp is None:
        return True
    return rp.can_fetch(BOT_UA, url)
