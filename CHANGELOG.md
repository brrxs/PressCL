# Changelog

All notable changes to PressCL are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.4.1] — 2026-06-09

### Added
- **Responsible-use disclaimer**: a full-page notice shown each time the app opens; the user must click "Acepto" before the interface becomes usable.
- **Hourly run limit**: whole-app runs are capped at 3 per hour, tracked in a persistent SQLite store (`.cache/runs.sqlite`, `scraper/ratelimit.py`) so the cap survives tab close/reopen. The "▶ Ejecutar" button disables when the cap is reached and shows when the next run unlocks.
- **robots.txt compliance**: HTML scrapers (`BaseScraper._fetch`, `BasePlaywrightScraper._pw_get`) now check each host's `robots.txt` before requesting a URL, skipping disallowed pages (`scraper/robots.py`). API-based scrapers, which consume explicit JSON endpoints, are exempt.

---

## [0.4] — 2026-06-09

### Added
- **Permanent article cache** (`scraper/cache.py`): articles scraped once are stored in a local SQLite database (`.cache/articles.sqlite`) and served from there on subsequent runs, never re-requesting the same article from the medium.
- **Case-sensitive search via quoted terms**: wrapping a term in double quotes (e.g. `"CAE"`) matches it case-sensitively as a whole word/phrase; unquoted terms remain accent- and case-insensitive as before.
- **16th outlet scraper** (previously undocumented): the scraper registry now includes 16 outlets, up from the 15 documented in [0.1].

### Changed
- **Date-aware pagination stop**: listing and search page collection halts as soon as all links on a page pre-date the `since` window, avoiding unnecessary requests to media sites.
- **HTTP keep-alive**: `BaseScraper` and `BaseApiScraper` now reuse TCP/TLS connections via `requests.Session`, reducing connection overhead on each scraping run.
- **Google News full-text enrichment via Playwright** (previously undocumented): full-text retrieval now opens parallel headless Playwright pages and feeds each article to `trafilatura` for body extraction; `trafilatura` alone is no longer sufficient.

---

## [0.3] — 2026-06-05

### Added
- **Auto-shutdown monitor** (previously undocumented): the Streamlit process exits shortly after the last browser tab closes, so one-click launches don't leave orphaned servers running.

### Changed
- `setup.bat` rebranded to PressCL; auto-creates desktop shortcut via PowerShell
- Streamlit results table now auto-sizes height to show all outlet rows without scrolling
- **Inline `ThreadPoolExecutor` replaced `streamlit_runner` adapter** (previously undocumented): the Streamlit GUI now runs scrapers via an inline `ThreadPoolExecutor` in `app.py`; `streamlit_runner.py` is retained but no longer imported.

### Fixed
- `setup.bat` shortcut creation failed at step 4: CMD `^` line-continuation inside the quoted PowerShell `-Command` string was passed literally, aborting the script. Collapsed to a single line and replaced `\"` escaping with `[char]34`.
- `PressCL.lnk` launched nothing: `launch.vbs` started Streamlit hidden (window style `0`), where its internal `webbrowser.open()` fails silently. Now uses `--server.headless true` and opens the browser from VBS, with a port guard to avoid spawning duplicate instances.

---

## [0.2] — 2026-06-05

Major reorganization: all application code moved into `app/` subdirectory.
Streamlit GUI introduced alongside the existing CLI.

### Added
- **Streamlit GUI** (`app/app.py`): web interface for interactive searching — multi-query support, parallel worker control, live progress table, CSV/Parquet download
- `launch.vbs` and `stop.bat` for one-click launch/close on Windows
- `app/scraper/streamlit_runner.py`: adapter running scraper pool inside Streamlit's execution model (subsequently replaced — see [0.3])
- Google News full-article retrieval via `trafilatura`
- Auto-generated Markdown run reports in `reports/` after each CLI run
- `validate.py`: standalone outlet selector validator

### Changed
- All source files moved from repo root into `app/` subdirectory
- Streamlit theme: terracotta colour palette, custom CSS, SVG logo
- `.gitignore` moved to `app/`

### Removed
- `INSTRUCTIONS.md`, `References.md`, `progress.md`, `report.md`, `launch.bat` from root (superseded by new structure or deleted as transient artifacts)
- Old Windows shortcut files at repo root

---

## [0.1] — 2026-06-04

First working release. CLI-only.

### Added
- **CLI** (`run.py`) with five commands: `run`, `merge`, `clean`, `check`, `list`
- 15 outlet scrapers across three base types: `BaseScraper` (HTML), `BaseApiScraper` (JSON), `BasePlaywrightScraper` (Playwright/Chromium)
- Multi-query fan-out with AND-within / OR-across phrase semantics
- Accent-insensitive keyword matching via `unicodedata.normalize`
- Parallel execution via `multiprocessing.Pool`
- CSV and Parquet output via `pandas` + `pyarrow`
- Logging queue (`QueueHandler` / `QueueListener`) for safe multiprocess log aggregation
- `setup.bat` one-time Windows installer
- Streamlit config and theme (`.streamlit/config.toml`)

---

[0.4.1]: https://github.com/brrxs/PressCL/compare/v0.4...v0.4.1
[0.4]: https://github.com/brrxs/PressCL/compare/v0.3...v0.4
[0.3]: https://github.com/brrxs/PressCL/compare/v0.2...v0.3
[0.2]: https://github.com/brrxs/PressCL/compare/v0.1...v0.2
[0.1]: https://github.com/brrxs/PressCL/releases/tag/v0.1
