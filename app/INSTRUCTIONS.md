# PressCL — Instructions

---

## Using the app

### 1. Open PressCL

Double-click the **PressCL** shortcut on your desktop. The app opens in your browser automatically. If it's your first time, run `setup.bat` first (see the main README).

### 2. Enter your search

- **Query** — the keyword or phrase to search (e.g. `reforma pensiones`, `Boric`). Wrap a term in double quotes (e.g. `"CAE"`) to match it case-sensitively as a whole word.
- **Date range** — pick a start and end date. The app searches articles published within that window.
- **Outlets** — all 16 are selected by default. Uncheck any you don't need.
- **Workers** — how many outlets to scrape in parallel (default: 4). Higher = faster, but heavier on your machine.

### 3. Run

Click **Ejecutar**. A live table shows each outlet's status as results come in. When all outlets finish, the table shows how many articles each one returned.

### 4. Download results

Once the run completes, use the download buttons to save your dataset as **CSV** or **Parquet**. Files are also saved locally in `app/datos/` — one subfolder per outlet, one file per run.

### 5. Multi-query searches

To search for name variants or related terms at once, add multiple queries (one per line in the query box). Within each phrase, all words must appear (AND). Across phrases, any match keeps the article (OR).

Example: searching `Mara Sedini` and `Sedini` separately returns articles that mention either form.

### 6. Case-sensitive search

Wrap a term in double quotes to match it case-sensitively as a whole word:

- `"CAE"` — matches only the uppercase acronym, not `cae` or `Cae`
- `"Ley Corta"` — matches this exact casing only
- Mix freely: `"CAE", pensiones reforma` searches case-sensitive `"CAE"` **or** accent-insensitive `pensiones reforma`

**CLI:** single-quote the argument so the shell passes the literal double quotes:

```powershell
python run.py run --query '"CAE"' --days 30
```

---

## Output files

```
app/datos/
  {outlet}/
    {outlet}_{query}_{YYYYMMDD_HHMMSS}.csv
    {outlet}_{query}_{YYYYMMDD_HHMMSS}.parquet
  curated/
    {query}-dataset-{YYYYMMDD}.csv        ← merged across outlets
    {query}-dataset-{YYYYMMDD}.parquet
```

Each article has 8 fields: `titulo`, `cuerpo`, `bajada`, `fecha`, `fuente`, `url`, `fecha_scraping`, `query`.

After each run, a summary report is written to `app/reports/`.

---

## Troubleshooting

**The app doesn't open / PressCL shortcut doesn't work**
Run `setup.bat` again. If that doesn't help, open a terminal in the `app/` folder and run:
```powershell
.venv\Scripts\python -m streamlit run app.py
```

**An outlet returns 0 articles**
The site may have redesigned its HTML since the last update. Open a terminal in `app/` and run:
```powershell
.venv\Scripts\python run.py check <outlet-slug>
```
This prints what the scraper sees on that outlet's page — useful for diagnosing broken selectors.

**Moving the folder to a new machine**
The `.venv` virtual environment hardcodes the Python path and won't work after moving. Delete it and run `setup.bat` again:
```powershell
Remove-Item -Recurse -Force app\.venv
```

**Playwright Chromium not installed**
```powershell
app\.venv\Scripts\python -m playwright install chromium
```

---

## Advanced — CLI usage

The CLI (`run.py`) is for users who want to automate scraping, run scheduled jobs, or work from scripts. It exposes everything the app does, plus merge/clean utilities.

Run all commands from inside the `app/` folder with the venv activated.

### `run`

```powershell
python run.py run --query "reforma pensiones" --days 7 --progress
python run.py run elsiglo emol --query "pobreza" --since 2026-04-01 --to 2026-04-30
python run.py run --query "Mara Sedini" --query "Sedini" --since 2026-03-11
```

| Flag | Default | Description |
|---|---|---|
| `--query` / `-q` | none | Search phrase. Repeatable for OR logic across phrases. |
| `--days N` | 7 | Scrape the last N days |
| `--since YYYY-MM-DD` | 7 days ago | Start date (inclusive) |
| `--to YYYY-MM-DD` | today | End date (inclusive) |
| `--workers N` / `-w` | min(outlets, 4) | Parallel workers |
| `--progress` | off | Show live rich table |

### `merge`

Combines all CSVs in `datos/` into a single deduplicated dataset in `datos/curated/`. Normalizes Google News rows (extracts real outlet name, strips repeated text from body).

```powershell
python run.py merge --query "megarreforma" --since 2026-05-01
python run.py merge   # no filter — all articles
```

### `clean`

```powershell
python run.py clean                  # delete all raw files in datos/
python run.py clean google_news      # specific outlet only
python run.py clean --reports        # also delete reports/
python run.py clean --dry-run        # preview without deleting
```

Always skips `datos/curated/`.

### `check`

Smoke-test a single outlet — fetches one listing page and one article, prints all parsed fields. Doesn't save anything.

```powershell
python run.py check emol
python run.py check t13
```

### `list`

```powershell
python run.py list
```

---

## Outlet notes

| Slug | Type | Notes |
|---|---|---|
| `elsiglo` | HTML | WordPress |
| `elmostrador` | HTML | WordPress |
| `ciper` | HTML | Date from URL. Multi-word search returns 0 — use multiple `--query` phrases. |
| `eldesconcierto` | HTML | No working search (JS-rendered). Crawls 5 category pages ~75 URLs. |
| `elciudadano` | HTML | WordPress; OG meta date fallback |
| `biobio` | JSON API | Hidden API (same as `datamedios` R package) |
| `cooperativa` | HTML | Prontus CMS; date from URL |
| `cnnchile` | HTML | WordPress slug-style search |
| `lanacion` | HTML | WordPress; slow, 10 s timeout |
| `meganoticias` | HTML | WordPress; OG meta date fallback |
| `lacuarta` | HTML | Custom CMS |
| `emol` | JSON API | Hidden API at `newsapi.ecn.cl` |
| `t13` | Playwright | Homepage only, ~54 URLs |
| `24horas` | Playwright | Scroll-to-load, 8-page cap |
| `chvnoticias` | Playwright | Listing page only, ~8 URLs |
