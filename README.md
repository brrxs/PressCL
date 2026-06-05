# PressCL

> **Status:** Personal project, actively used but not actively maintained. Issues welcome; PRs reviewed best-effort. Outlet selectors may break when news sites redesign.

Browser-based app for searching Chilean news archives. Enter a keyword and a date range, pick your outlets, and download a structured dataset — no coding required.

Full usage documentation: [INSTRUCTIONS.md](app/INSTRUCTIONS.md).

---

## How it works

You open the app in your browser, type a search query (e.g. `reforma pensiones`), set a date window, and hit run. PressCL searches 15 Chilean news outlets simultaneously and returns a table of articles — headline, body, date, source, URL — ready to download as CSV or Parquet.

Under the hood it uses each site's native search endpoint where available, and falls back to crawling category feeds with local keyword filtering where it is not.

---

## Setup — Windows

**Requirements:** Python 3.10 or higher. Download from [python.org](https://www.python.org/downloads/) and check "Add Python to PATH" during install.

1. Download or clone this repository
2. Double-click `setup.bat` — wait for it to finish (downloads Chromium, ~300 MB, one time only)
3. Double-click the **PressCL** shortcut that appears
4. The app opens in your browser automatically

That's it. No terminal, no commands.

---

## Media coverage

16 outlets covering the main segments of Chile's national news media landscape.

| Outlet | URL | Type |
|---|---|---|
| Biobío Chile | biobiochile.cl | Radio/Digital |
| CHV Noticias | chilevision.cl | Broadcast (TV) |
| CIPER Chile | ciperchile.cl | Investigative |
| CNN Chile | cnnchile.com | Broadcast (TV) |
| Cooperativa | cooperativa.cl | Radio/digital |
| El Ciudadano | elciudadano.com | Alternative |
| El Desconcierto | eldesconcierto.cl | Alternative |
| El Mostrador | elmostrador.cl | Digital |
| El Siglo | elsiglo.cl | Alternative |
| Emol | emol.com | Print-digital |
| La Cuarta | lacuarta.com | Print-digital |
| La Nación | lanacion.cl | Print-digital |
| Mega Noticias | meganoticias.cl | Broadcast (TV) |
| T13 | t13.cl | Broadcast (TV) |
| 24 Horas | 24horas.cl | Broadcast (TV) |
| Google News | news.google.com | Search engine |

---

## Output

Each article is saved with 8 fields:

| Field | Description |
|---|---|
| `titulo` | Headline |
| `cuerpo` | Body text |
| `bajada` | Subtitle / lead (when available) |
| `fecha` | Publication date (YYYY-MM-DD) |
| `fuente` | Outlet |
| `url` | Article URL |
| `fecha_scraping` | When the article was collected |
| `query` | The search query used |

---

## Responsible use

PressCL is designed for research and journalistic use on public news content.

- Requests are rate-limited to 1.5–3.5 seconds between pages per outlet.
- Scraping is capped at 50 pages per search and 100 articles/day for Google News.
- You are responsible for complying with each outlet's terms of service.
- This tool does not bypass paywalls or access restricted content.

---

## Acknowledgments

- **[datamedios](https://socialtec-cl.github.io/datamedios/)** (socialtec-cl) — R package for Chilean media data. The hidden JSON search APIs used by Biobío and Emol were discovered through its source code.
- **[prensa_chile](https://github.com/bastianolea/prensa_chile)** (Bastián Olea) — Prior scraper for Chilean press that shaped the outlet selection and overall approach.
- **[GNews](https://github.com/ranahaani/GNews)** (ranahaani) — Library wrapping Google News RSS. Powers the Google News outlet with Chile/Spanish targeting.
- **[trafilatura](https://trafilatura.readthedocs.io/en/latest/)** — Article extraction library used to retrieve and clean full article bodies.

---

## For developers

If you want to use the CLI, add outlets, or understand the internals, see [INSTRUCTIONS.md](app/INSTRUCTIONS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT](LICENSE)
