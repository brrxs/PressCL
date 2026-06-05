# PressCL

> **Status:** Personal project, actively used but not actively maintained. Issues welcome; PRs reviewed best-effort. Outlet selectors may break when news sites redesign — run `python run.py check <slug>` to diagnose.

Keyword scraper for Chilean online news. Given a search query and date range, it retrieves articles from 15 outlets and Google News, spanning print-digital, broadcast, investigative, and alternative media. Dual interface: Streamlit GUI and CLI.

Full usage documentation: [INSTRUCTIONS.md](app/INSTRUCTIONS.md).

---

## What it does

Takes a keyword query (e.g. `"reforma pensiones"`) and a date window, returns a structured dataset of articles — headline, body, date, source, URL — across all configured outlets. Uses each site's native search endpoint where available, falls back to crawling category feeds with local keyword filtering where it is not.

Output is written to CSV and Parquet files under `app/datos/`, one subfolder per outlet.

---

## Media coverage

16 outlets covering the main segments of Chile's national news media landscape.

| Outlet | Slug | URL | Type |
|---|---|---|---|
| Biobío Chile | `biobio` | biobiochile.cl | Radio/Digital |
| CHV Noticias | `chvnoticias` | chilevision.cl | Broadcast (TV) |
| CIPER Chile | `ciper` | ciperchile.cl | Investigative |
| CNN Chile | `cnnchile` | cnnchile.com | Broadcast (TV) |
| Cooperativa | `cooperativa` | cooperativa.cl | Radio/digital |
| El Ciudadano | `elciudadano` | elciudadano.com | Alternative |
| El Desconcierto | `eldesconcierto` | eldesconcierto.cl | Alternative |
| El Mostrador | `elmostrador` | elmostrador.cl | Digital |
| El Siglo | `elsiglo` | elsiglo.cl | Alternative |
| Emol | `emol` | emol.com | Print-digital |
| La Cuarta | `lacuarta` | lacuarta.com | Print-digital |
| La Nación | `lanacion` | lanacion.cl | Print-digital |
| Mega Noticias | `meganoticias` | meganoticias.cl | Broadcast (TV) |
| T13 | `t13` | t13.cl | Broadcast (TV) |
| 24 Horas | `24horas` | 24horas.cl | Broadcast (TV) |
| Google News | `google_news` | news.google.com | Search engine |

---

## Output schema

Each article record has 8 fields:

| Field | Description |
|---|---|
| `titulo` | Headline |
| `cuerpo` | Body text |
| `bajada` | Subtitle / lead (when available) |
| `fecha` | Publication date (YYYY-MM-DD) |
| `fuente` | Outlet slug |
| `url` | Canonical article URL |
| `fecha_scraping` | Timestamp of when the article was collected |
| `query` | The search query used |

---

## Quick start

```powershell
# Clone and enter the app directory
git clone https://github.com/brrxsn/scraper-medios-chile.git
cd scraper-medios-chile

# Setup (one time) — Windows
.\setup.bat

# Or manually:
cd app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium

# Launch the GUI (from app/)
streamlit run app.py

# Or use the CLI (from app/)
python run.py run --query "reforma pensiones" --days 7 --progress
```

See [INSTRUCTIONS.md](app/INSTRUCTIONS.md) for the full flag reference, multi-query syntax, merge/clean/check commands, troubleshooting, and design notes.

---

## Responsible use

PressCL is designed for research and journalistic use on public news content.

- Requests are rate-limited to 1.5–3.5 seconds between pages per outlet.
- Scraping is capped at 50 pages per search and 100 articles/day for Google News.
- Outlets are identified via a standard browser User-Agent (`Mozilla/5.0 compatible`).
- You are responsible for complying with each outlet's terms of service.
- This tool does not bypass paywalls or access restricted content.

---

## Acknowledgments

This project builds directly on the following work:

- **[datamedios](https://socialtec-cl.github.io/datamedios/)** (socialtec-cl) — R package for Chilean media data. The hidden JSON search APIs used by Biobío and Emol were discovered through its source code; the offset and pagination logic mirrors its implementation.

- **[prensa_chile](https://github.com/bastianolea/prensa_chile)** (Bastián Olea) — Prior scraper for Chilean press that shaped the outlet selection and overall approach.

- **[GNews](https://github.com/ranahaani/GNews)** (ranahaani) — Library wrapping Google News RSS. Powers the `google_news` outlet with Chile/Spanish targeting.

- **[trafilatura](https://trafilatura.readthedocs.io/en/latest/)** — Article extraction library used to retrieve and clean full article bodies across outlets.

---

## Instalación (Español)

**Requisitos:** Python 3.10 o superior. Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/) y marca la opción "Add Python to PATH".

**Primera vez (instalación):**

1. Hacer doble clic en `setup.bat`
2. Esperar a que termine (puede tomar unos minutos — descarga Chromium)
3. Listo, no es necesario repetir este paso

**Abrir la app:**

1. Hacer doble clic en el acceso directo `PressCL` creado por el instalador
2. El navegador se abrirá automáticamente con la app

**Cerrar la app:**

- Cerrar el navegador (o la pestaña) cierra la app completamente.

---

## License

[MIT](LICENSE)
