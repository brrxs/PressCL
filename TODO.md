# PressCL — Pre-Publication TODO

Tracking issues identified in the readiness evaluation (2026-06-05).
Check items off as you complete them. Estimated total effort: ~4–6 hours.

## Blockers — must fix before publishing

- [x] **B1** — Add `LICENSE` (MIT) at repo root. Use year `2026`. (5 min)
- [x] **B2** — Move `app/README.md` → `README.md` at repo root. Adjust internal paths so commands work from root (`python app/run.py ...` or instruct `cd app` first). (15 min)
- [x] **B3** — Fix broken `INSTRUCTIONS.md` link in README (lines 5 and 68 of original). Either create the file with full flag reference / multi-query syntax / troubleshooting, or remove the link and inline essentials. (30–60 min)

## High priority — fix this week

- [x] **H1** — Create root-level `.gitignore`. Copy from `app/.gitignore` and add: `.env`, `.streamlit/secrets.toml`, `*.lock`, `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`, `*.swp`. (5 min)
- [x] **H2** — Resolve naming inconsistency (`PressCL` vs `prensa_chile_py` vs `scraper-medios-chile`). Recommend `PressCL` as display name across README and docs. (20 min)
- [x] **H3** — Pin dependencies: `pip freeze > app/requirements-lock.txt` from working venv, commit it. (5 min)
- [x] **H4** — Add "Responsible use / Scraping ethics" section to README documenting delays (1.5–3.5s), hard caps (50 pages, 100 articles/day for Google News), User-Agent identification, and user's TOS responsibility. (20 min)

## Medium priority — before promoting to others

- [x] **M1** — Add `CONTRIBUTING.md` explaining outlet base classes (`BaseScraper` / `BaseApiScraper` / `BasePlaywrightScraper`), required methods, registration, and `python run.py check <outlet>` testing. (45 min)
- [x] **M2** — Add `CHANGELOG.md` reconstructed from git for v0.1 and v0.2. Use [Keep a Changelog](https://keepachangelog.com) format going forward. (20 min)
- [ ] **M3** — Smoke-test `setup.bat` on a clean folder (verify `PressCL.lnk` is created and app launches). (30–60 min)
- [x] **M4** — Add "Status: personal project" note to README setting expectations on maintenance/PRs. (5 min)
- [x] **M5** — Fold `INSTRUCCIONES.txt` into root README as a Spanish-language install section. Delete the `.txt`. (20 min)

## Low priority — nice-to-have

- [ ] **L1** — Add tests (skip unless something breaks; selector tests against live sites are brittle).
- [ ] **L2** — Move `MIN_TITULO_LEN`, `MIN_CUERPO_LEN`, `HARD_PAGE_CAP` etc. to `config.toml` (only if you find yourself tuning them).
- [ ] **L3** — Add a minimal GitHub Actions workflow (import-smoke-test).
- [ ] **L4** — Add `SECURITY.md` (one paragraph: "report security issues to `<email>`").
- [ ] **L5** — Add `.github/ISSUE_TEMPLATE/` and `PULL_REQUEST_TEMPLATE.md` (only if issues get noisy).
- [ ] **L6** — Audit `app/.streamlit/config.toml` and `app/style-kit/` for any machine-specific paths.
- [ ] **L7** — Adopt conventional-commit prefixes (`feat:`, `fix:`, `docs:`) on new commits.

## Ship

- [ ] Tag `v0.3` after M3 smoke-test passes.
- [ ] Push to GitHub, mark repo public.
- [ ] Verify in incognito: README renders, links work, LICENSE shows in sidebar.

## Verification checklist before going public

- [ ] Visit GitHub repo URL incognito — README renders with description, install, media coverage table.
- [ ] Click every README link — no 404s.
- [ ] GitHub sidebar shows "MIT License".
- [ ] Fresh clone on a clean Windows folder — `setup.bat` completes, `PressCL.lnk` launches, scrape succeeds.
- [ ] `git status` after a clean run — no `.venv/`, `__pycache__/`, `datos/`, `reports/`, logs.
- [ ] Non-technical Spanish-speaker can follow install steps unassisted.
- [ ] `python app/run.py check <outlet>` passes for at least 3 outlets.

---

**Security review**: Cleared. No secrets, no `eval`/`exec`/`pickle`/`shell=True`, no PII, no telemetry. Safe to publish once blockers above are resolved.
