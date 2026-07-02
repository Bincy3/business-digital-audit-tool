import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "audit_history.db"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

SCORE_FILTERS = {
    "excellent": (80, 100),
    "average": (50, 79),
    "poor": (0, 49),
}


class DatabaseError(Exception):
    pass


def _connect() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        raise DatabaseError("Unable to open the audit history database.") from exc


def _ensure_columns(conn: sqlite3.Connection) -> None:
    cursor = conn.execute("PRAGMA table_info(audits)")
    columns = {row[1] for row in cursor.fetchall()}
    schema = [
        ("industry", "TEXT"),
        ("seo_score", "INTEGER"),
        ("technical_basics_score", "INTEGER"),
        ("social_presence_score", "INTEGER"),
        ("contact_readiness_score", "INTEGER"),
        ("conversion_readiness_score", "INTEGER"),
        ("recommendations", "TEXT"),
        ("whatsapp_message", "TEXT"),
    ]
    for column_name, column_def in schema:
        if column_name not in columns:
            conn.execute(f"ALTER TABLE audits ADD COLUMN {column_name} {column_def}")


def init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                industry TEXT,
                website_url TEXT NOT NULL,
                overall_score INTEGER NOT NULL,
                seo_score INTEGER,
                technical_basics_score INTEGER,
                social_presence_score INTEGER,
                contact_readiness_score INTEGER,
                conversion_readiness_score INTEGER,
                audit_time TEXT NOT NULL,
                html_filename TEXT NOT NULL,
                txt_filename TEXT NOT NULL,
                recommendations TEXT,
                whatsapp_message TEXT,
                status TEXT NOT NULL
            )
            """
        )
        _ensure_columns(conn)
        conn.commit()
    except sqlite3.Error as exc:
        raise DatabaseError("Could not initialize the audit history database.") from exc
    finally:
        conn.close()


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "audit"
    return cleaned[:48]


def build_report_filenames(business_name: str) -> Tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = sanitize_filename(business_name)
    html_filename = f"{base}_{timestamp}.html"
    txt_filename = f"{base}_{timestamp}.txt"
    return html_filename, txt_filename


def _serialize_recommendations(recommendations: Any) -> Optional[str]:
    if recommendations is None:
        return None
    if isinstance(recommendations, str):
        return recommendations
    return json.dumps(list(recommendations))


def _deserialize_recommendations(value: Optional[str]) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return [str(value)]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def add_audit(
    business_name: str,
    industry: str,
    website_url: str,
    overall_score: int,
    seo_score: int,
    technical_basics_score: int,
    social_presence_score: int,
    contact_readiness_score: int,
    conversion_readiness_score: int,
    html_filename: str,
    txt_filename: str,
    recommendations: Optional[List[str]],
    whatsapp_message: str,
    status: str,
) -> int:
    init_db()
    conn = _connect()
    audit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor = conn.execute(
            """
            INSERT INTO audits (
                business_name,
                industry,
                website_url,
                overall_score,
                seo_score,
                technical_basics_score,
                social_presence_score,
                contact_readiness_score,
                conversion_readiness_score,
                audit_time,
                html_filename,
                txt_filename,
                recommendations,
                whatsapp_message,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                business_name,
                industry,
                website_url,
                overall_score,
                seo_score,
                technical_basics_score,
                social_presence_score,
                contact_readiness_score,
                conversion_readiness_score,
                audit_time,
                html_filename,
                txt_filename,
                _serialize_recommendations(recommendations),
                whatsapp_message,
                status,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        raise DatabaseError("Could not save the audit history record.") from exc
    finally:
        conn.close()


def get_audit(audit_id: int) -> Optional[Dict]:
    init_db()
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
        if not row:
            return None
        audit = dict(row)
        audit["recommendations"] = _deserialize_recommendations(audit.get("recommendations"))
        return audit
    except sqlite3.Error as exc:
        raise DatabaseError("Unable to read an audit history record.") from exc
    finally:
        conn.close()


def update_audit(audit_id: int, **fields: Any) -> bool:
    init_db()
    conn = _connect()
    try:
        if not fields:
            return False
        if "recommendations" in fields:
            fields["recommendations"] = _serialize_recommendations(fields["recommendations"])
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [audit_id]
        cursor = conn.execute(f"UPDATE audits SET {assignments} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise DatabaseError("Could not update the audit history record.") from exc
    finally:
        conn.close()


def delete_audit(audit_id: int) -> bool:
    init_db()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT html_filename, txt_filename FROM audits WHERE id = ?", (audit_id,)
        ).fetchone()
        if not row:
            return False

        html_path = REPORTS_DIR / row["html_filename"]
        txt_path = REPORTS_DIR / row["txt_filename"]

        for path in (html_path, txt_path):
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass

        conn.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
        conn.commit()
        return True
    except sqlite3.Error as exc:
        raise DatabaseError("Could not delete the audit history record.") from exc
    finally:
        conn.close()


def _build_filters(
    search_business: str = "",
    search_website: str = "",
    score_filter: str = "",
) -> Tuple[str, List]:
    conditions = []
    params: List = []
    if search_business:
        conditions.append("LOWER(business_name) LIKE ?")
        params.append(f"%{search_business.lower()}%")
    if search_website:
        conditions.append("LOWER(website_url) LIKE ?")
        params.append(f"%{search_website.lower()}%")
    if score_filter in SCORE_FILTERS:
        minimum, maximum = SCORE_FILTERS[score_filter]
        conditions.append("overall_score BETWEEN ? AND ?")
        params.extend([minimum, maximum])
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_clause, params


def list_audits(
    search_business: str = "",
    search_website: str = "",
    score_filter: str = "",
    sort_by: str = "audit_time",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict], int]:
    init_db()
    conn = _connect()
    order = "ASC" if order.lower() == "asc" else "DESC"
    if sort_by not in {"audit_time", "overall_score"}:
        sort_by = "audit_time"
    where, params = _build_filters(search_business, search_website, score_filter)
    try:
        count_query = f"SELECT COUNT(*) as total FROM audits {where}"
        total = conn.execute(count_query, params).fetchone()["total"]
        offset = (max(page, 1) - 1) * page_size
        query = (
            f"SELECT * FROM audits {where} ORDER BY {sort_by} {order} "
            f"LIMIT ? OFFSET ?"
        )
        rows = conn.execute(query, (*params, page_size, offset)).fetchall()
        audits = [dict(row) for row in rows]
        for audit in audits:
            audit["recommendations"] = _deserialize_recommendations(audit.get("recommendations"))
        return audits, total
    except sqlite3.Error as exc:
        raise DatabaseError("Could not query audit history.") from exc
    finally:
        conn.close()


def get_history_stats() -> Dict[str, Optional[object]]:
    init_db()
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_audits,
                AVG(overall_score) AS average_score,
                MAX(overall_score) AS highest_score,
                MIN(overall_score) AS lowest_score,
                MAX(audit_time) AS last_audit_date
            FROM audits
            """
        ).fetchone()
        if not row:
            return {
                "total_audits": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "last_audit_date": None,
            }
        return {
            "total_audits": row["total_audits"] or 0,
            "average_score": round(row["average_score"] or 0, 1),
            "highest_score": row["highest_score"] or 0,
            "lowest_score": row["lowest_score"] or 0,
            "last_audit_date": row["last_audit_date"],
        }
    except sqlite3.Error as exc:
        raise DatabaseError("Could not calculate audit history stats.") from exc
    finally:
        conn.close()
