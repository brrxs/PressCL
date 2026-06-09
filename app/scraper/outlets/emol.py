from datetime import datetime
from html import unescape
from typing import Optional

from bs4 import BeautifulSoup

from scraper.base_api import BaseApiScraper
from scraper.utils import clean_text

API_BASE = "https://newsapi.ecn.cl/NewsApi/emol/buscador/emol"


class EmolScraper(BaseApiScraper):
    SOURCE_SLUG = "emol"
    BATCH_SIZE = 10

    def _fetch_page(self, query: str, offset: int) -> list[dict]:
        data = self._get(API_BASE, params={"q": query, "size": self.BATCH_SIZE, "from": offset})
        if data is None:
            return []
        try:
            return [hit["_source"] for hit in data["hits"]["hits"]]
        except (KeyError, TypeError):
            return []

    def _map_article(self, raw: dict) -> Optional[dict]:
        titulo = unescape(raw.get("titulo") or "")
        texto_raw = raw.get("texto") or ""

        if not titulo or len(titulo) < 20:
            return None

        # texto contains HTML markup — extract plain text
        cuerpo = BeautifulSoup(unescape(texto_raw), "lxml").get_text(separator=" ", strip=True)

        if not cuerpo or len(cuerpo) < 400:
            return None

        fecha_raw = raw.get("fechaPublicacion") or raw.get("fechaModificacion")
        fecha = None
        if fecha_raw:
            try:
                fecha = datetime.fromisoformat(
                    fecha_raw.replace("Z", "+00:00")
                ).date().isoformat()
            except Exception:
                pass

        bajada_raw = raw.get("bajada")
        if isinstance(bajada_raw, list):
            bajada = unescape(" ".join(item.get("texto", "") for item in bajada_raw if isinstance(item, dict)))
            bajada = clean_text(bajada) or None
        elif isinstance(bajada_raw, str):
            bajada = clean_text(unescape(bajada_raw)) or None
        else:
            bajada = None

        return {
            "titulo": clean_text(titulo),
            "cuerpo": clean_text(cuerpo),
            "bajada": bajada,
            "fecha": fecha,
            "fuente": self.SOURCE_SLUG,
            "url": raw.get("permalink", ""),
            "fecha_scraping": datetime.now().isoformat(timespec="seconds"),
            "query": "",
        }
