import csv
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from scraper.outlets import REGISTRY
from scraper.output import SCHEMA

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scraper de Prensa Chilena",
    page_icon="🗞",
    layout="wide",
)

# ── JetBrains Mono + minor overrides ─────────────────────────────────────────
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap"
          rel="stylesheet">
    <style>
        html, body, [class*="css"], .stTextArea textarea, .stTextInput input,
        .stDataFrame, button, label, .stMarkdown p { font-family: 'JetBrains Mono', monospace !important; }
        /* Terracotta active tab underline */
        .stTabs [data-baseweb="tab"][aria-selected="true"] { border-bottom-color: #B8541C !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "articles" not in st.session_state:
    st.session_state.articles = []
if "run_meta" not in st.session_state:
    st.session_state.run_meta = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = Path(__file__).parent / "style-kit" / "assets" / "logo.svg"
    if logo_path.exists():
        st.image(str(logo_path))
    st.markdown("**Monitor Social UC**")
    st.divider()

    query_raw = st.text_area(
        "Búsqueda",
        placeholder="ej: reforma pensiones\npobreza vivienda",
        help=(
            "Una frase por línea.\n"
            "Dentro de cada línea: TODAS las palabras deben aparecer (AND).\n"
            "Entre líneas: basta con que aparezca UNA (OR).\n"
            "Dejar vacío para traer todo lo del período."
        ),
        height=110,
    )

    today = date.today()
    col_a, col_b = st.columns(2)
    with col_a:
        since = st.date_input("Desde", value=today - timedelta(days=7), max_value=today)
    with col_b:
        until = st.date_input("Hasta", value=today, max_value=today)

    st.markdown("**Medios**")
    all_slugs = sorted(REGISTRY.keys())
    select_all = st.checkbox("Seleccionar todos", value=True)
    if select_all:
        selected_outlets = all_slugs
        st.caption(f"{len(all_slugs)} medios seleccionados")
    else:
        selected_outlets = st.multiselect(
            "Medios",
            all_slugs,
            default=all_slugs,
            placeholder="Elige medios…",
            label_visibility="collapsed",
        )

    with st.expander("Opciones avanzadas"):
        n_workers = st.slider(
            "Procesos en paralelo", 1, 4, 3,
            help="Cuántos medios se scrapeean al mismo tiempo. Más = más rápido pero más uso de CPU/RAM.",
        )
        gn_fulltext = st.checkbox(
            "Google News: recuperar texto completo",
            help="Descarga el artículo completo vía Playwright (más lento). "
                 "Por defecto sólo trae el extracto RSS.",
        )

    run_disabled = not selected_outlets or since > until
    run_btn = st.button(
        "▶  Ejecutar",
        type="primary",
        use_container_width=True,
        disabled=run_disabled,
    )
    if since > until:
        st.error("La fecha de inicio debe ser anterior o igual a la fecha de término.")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("Scraper de Prensa Chilena")
st.caption(f"{len(REGISTRY)} medios · datos guardados en datos/")
st.divider()

if run_btn:
    queries = [q.strip() for q in query_raw.splitlines() if q.strip()]
    since_d = date(since.year, since.month, since.day)
    until_d = date(until.year, until.month, until.day)

    if gn_fulltext:
        os.environ["GNEWS_FULLTEXT"] = "1"
    elif "GNEWS_FULLTEXT" in os.environ:
        del os.environ["GNEWS_FULLTEXT"]

    status: dict[str, tuple[str, str]] = {
        slug: ("⏳ Pendiente", "—") for slug in selected_outlets
    }

    st.markdown(f"**Scrapeando {len(selected_outlets)} medio(s)…**")
    progress_bar = st.progress(0.0)
    table_slot = st.empty()

    def _refresh():
        rows = [{"Medio": s, "Estado": e, "Artículos": n} for s, (e, n) in status.items()]
        table_slot.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    _refresh()

    def _scrape(slug: str) -> tuple[str, list[dict]]:
        scraper = REGISTRY[slug]()
        articles = scraper.run(queries=queries, since=since_d, until=until_d)
        return slug, articles or []

    all_articles: list[dict] = []
    done = 0

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = {pool.submit(_scrape, slug): slug for slug in selected_outlets}
        for future in as_completed(futures):
            slug = futures[future]
            done += 1
            try:
                _, arts = future.result()
                status[slug] = ("✓ Listo", str(len(arts)))
                all_articles.extend(arts)
            except Exception as exc:
                status[slug] = (f"✗ Error", "0")
            progress_bar.progress(done / len(selected_outlets))
            _refresh()

    st.session_state.articles = all_articles
    st.session_state.run_meta = {
        "queries": queries,
        "since": since,
        "until": until,
        "n_outlets": len(selected_outlets),
    }

    if all_articles:
        st.success(f"✓ {len(all_articles)} artículos recopilados.")
    else:
        st.warning("No se encontraron artículos con los filtros indicados.")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.articles:
    articles = st.session_state.articles
    meta = st.session_state.run_meta

    st.subheader(f"{len(articles)} artículos")
    if meta:
        q_label = (
            ", ".join(f'"{q}"' for q in meta["queries"])
            if meta["queries"] else "sin filtro de búsqueda"
        )
        st.caption(f"{q_label} · {meta['since']} → {meta['until']}")

    preview_cols = ["titulo", "fecha", "fuente", "url"]
    df = pd.DataFrame(articles)
    existing = [c for c in preview_cols if c in df.columns]
    st.dataframe(df[existing], use_container_width=True, hide_index=True)

    with st.expander("Desglose por fuente"):
        counts: dict[str, int] = {}
        for a in articles:
            src = a.get("fuente", "?")
            counts[src] = counts.get(src, 0) + 1
        df_counts = pd.DataFrame(
            sorted(counts.items(), key=lambda x: -x[1]),
            columns=["Fuente", "Artículos"],
        )
        st.dataframe(df_counts, hide_index=True, use_container_width=True)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=SCHEMA, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(articles)

    fname = f"prensa_chile_{date.today().strftime('%Y%m%d')}.csv"
    st.download_button(
        "⬇  Descargar CSV",
        data=buf.getvalue().encode("utf-8"),
        file_name=fname,
        mime="text/csv",
        type="primary",
    )

else:
    st.markdown(
        """
        <div style="text-align:center;padding:4rem 0;opacity:0.45;">
            <div style="font-size:3rem">🗞</div>
            <p>Configura una búsqueda en el panel izquierdo y presiona <strong>Ejecutar</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
