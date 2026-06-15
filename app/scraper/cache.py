import atexit
import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

_DB_PATH = Path(__file__).parent.parent / ".cache" / "articles.sqlite"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False, timeout=30)
_conn.execute("PRAGMA journal_mode=WAL")
_conn.execute(
    "CREATE TABLE IF NOT EXISTS articles "
    "(url TEXT PRIMARY KEY, data TEXT, fetched_at TEXT)"
)
_conn.commit()
_lock = threading.Lock()


def _close():
    try:
        _conn.close()
    except Exception:
        pass


atexit.register(_close)


def get(url: str) -> Optional[dict]:
    with _lock:
        row = _conn.execute(
            "SELECT data FROM articles WHERE url = ?", (url,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def put(article: dict) -> None:
    url = article.get("url") or ""
    if not url:
        return
    data = json.dumps(article, ensure_ascii=False)
    with _lock:
        _conn.execute(
            "INSERT OR REPLACE INTO articles (url, data, fetched_at) VALUES (?, ?, ?)",
            (url, data, datetime.now().isoformat(timespec="seconds")),
        )
        _conn.commit()


def count() -> int:
    with _lock:
        return _conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]


def db_size_bytes() -> int:
    total = 0
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(_DB_PATH) + suffix)
        if p.exists():
            total += p.stat().st_size
    return total


def clear() -> int:
    with _lock:
        n = _conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        _conn.execute("DELETE FROM articles")
        _conn.commit()
        _conn.execute("VACUUM")
        return n
