"""
Read-only access to the external references SQLite (synced from outside).
A fresh connection is opened per query so a newly synced file is always picked up.
"""
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from yiwu_app.utils.image_client import IMAGE_SERVER_URL

REFS_DB_PATH = os.getenv("REFS_DB_PATH", "/var/flyon_refs/referencias.db")
SEARCH_LIMIT = 40
CHINA_TZ = timezone(timedelta(hours=8))


def norm(s: str) -> str:
    s = (s or "").upper().strip()
    for ch in (" ", "-", "_", ".", "/"):
        s = s.replace(ch, "")
    return s


def is_available() -> bool:
    return os.path.isfile(REFS_DB_PATH)


def _connect():
    conn = sqlite3.connect(f"file:{REFS_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _like_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _image_url(image, image_v) -> str:
    if not image:
        return ""
    return f"{IMAGE_SERVER_URL}/images/market_refs/{image}?v={image_v or ''}"


def search(q: str = "", store: str = "") -> dict:
    """Returns {"available": bool, "results": [ {ref..., "stores": [...]}, ... ]}."""
    q = (q or "").strip()
    store_q = (store or "").strip().upper()
    q_norm = norm(q)
    use_q = len(q) >= 2 and len(q_norm) >= 1
    use_store = len(store_q) >= 1

    if not is_available():
        return {"available": False, "results": []}
    if not use_q and not use_store:
        return {"available": True, "results": []}

    where, params = [], []
    if use_q:
        where.append("(r.ref_norm LIKE ? ESCAPE '\\' OR r.name LIKE ? ESCAPE '\\')")
        params += [f"%{_like_escape(q_norm)}%", f"%{_like_escape(q)}%"]
    if use_store:
        where.append(
            "EXISTS (SELECT 1 FROM ref_stores s WHERE s.ref_norm = r.ref_norm "
            "AND s.store_norm LIKE ? ESCAPE '\\')"
        )
        params.append(f"%{_like_escape(store_q)}%")

    if use_q:
        order = (
            "CASE WHEN r.ref_norm = ? THEN 0 "
            "WHEN r.ref_norm LIKE ? ESCAPE '\\' THEN 1 ELSE 2 END, "
            "r.last_date IS NULL, r.last_date DESC"
        )
        order_params = [q_norm, f"{_like_escape(q_norm)}%"]
    else:
        order = "r.last_date IS NULL, r.last_date DESC"
        order_params = []

    sql = (
        "SELECT r.ref, r.ref_norm, r.name, r.composition, r.unit, r.image, r.image_v, "
        "r.last_store, r.last_date FROM refs r "
        f"WHERE {' AND '.join(where)} ORDER BY {order} LIMIT {SEARCH_LIMIT}"
    )

    try:
        conn = _connect()
    except sqlite3.Error:
        return {"available": False, "results": []}
    try:
        refs = [dict(row) for row in conn.execute(sql, params + order_params)]
        stores_by_ref: dict[str, list[dict]] = {}
        if refs:
            keys = [r["ref_norm"] for r in refs]
            placeholders = ",".join("?" * len(keys))
            rows = conn.execute(
                "SELECT ref_norm, store_number, store_norm, store_contact, last_price_rmb, "
                "currency, unit, times, first_date, last_date FROM ref_stores "
                f"WHERE ref_norm IN ({placeholders}) "
                "ORDER BY last_date IS NULL, last_date DESC",
                keys,
            )
            for row in rows:
                s = dict(row)
                s["matches"] = bool(use_store and store_q in (s.get("store_norm") or ""))
                stores_by_ref.setdefault(s["ref_norm"], []).append(s)
    except sqlite3.Error:
        return {"available": False, "results": []}
    finally:
        conn.close()

    for r in refs:
        r["image_url"] = _image_url(r.get("image"), r.get("image_v"))
        r["stores"] = stores_by_ref.get(r["ref_norm"], [])
    return {"available": True, "results": refs}


def get_exported_at() -> str:
    """meta.exported_at converted to China time (UTC+8) as DD/MM/YYYY, or ""."""
    if not is_available():
        return ""
    try:
        conn = _connect()
    except sqlite3.Error:
        return ""
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'exported_at'").fetchone()
    except sqlite3.Error:
        return ""
    finally:
        conn.close()
    if not row or not row[0]:
        return ""
    raw = str(row[0]).strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return format_date(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CHINA_TZ).strftime("%d/%m/%Y")


def format_date(value) -> str:
    """'YYYY-MM-DD...' -> 'DD/MM/YYYY'; returns the input unchanged if it can't be parsed."""
    if not value:
        return ""
    s = str(value).strip()
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return s
