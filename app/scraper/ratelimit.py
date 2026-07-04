import atexit
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Env override solo para la sesión actual: PRESSCL_MAX_RUNS_PER_HOUR=0 lo
# desactiva (modo de prueba, ver test-mode.bat). Por defecto 3/hora.
MAX_RUNS_PER_HOUR = int(os.getenv("PRESSCL_MAX_RUNS_PER_HOUR", "3"))

_DB_PATH = Path(__file__).parent.parent / ".cache" / "runs.sqlite"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False, timeout=30)
_conn.execute("PRAGMA journal_mode=WAL")
_conn.execute("CREATE TABLE IF NOT EXISTS runs (ts TEXT NOT NULL)")
_conn.commit()
_lock = threading.Lock()


def _close():
    try:
        _conn.close()
    except Exception:
        pass


atexit.register(_close)


def _prune() -> None:
    cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
    _conn.execute("DELETE FROM runs WHERE ts < ?", (cutoff,))
    _conn.commit()


def record_run() -> None:
    with _lock:
        _prune()
        _conn.execute("INSERT INTO runs (ts) VALUES (?)", (datetime.now().isoformat(),))
        _conn.commit()


def count_last_hour() -> int:
    cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
    with _lock:
        return _conn.execute(
            "SELECT COUNT(*) FROM runs WHERE ts >= ?", (cutoff,)
        ).fetchone()[0]


def next_free_at() -> Optional[datetime]:
    cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
    with _lock:
        row = _conn.execute(
            "SELECT ts FROM runs WHERE ts >= ? ORDER BY ts ASC LIMIT 1", (cutoff,)
        ).fetchone()
    if row is None:
        return None
    oldest = datetime.fromisoformat(row[0])
    return oldest + timedelta(hours=1)
