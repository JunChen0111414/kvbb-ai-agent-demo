import psycopg
import os


# ===== KPI 统计 =====
def get_case_statistics(payload=None):
    conn = None
    try:
        conn = psycopg.connect(os.environ["DB_URL"])
        cur = conn.cursor()

        # 总数
        cur.execute("SELECT COUNT(*) FROM kvbb_requests;")
        total = cur.fetchone()[0] or 0

        # 各状态统计
        cur.execute("""
            SELECT bearbeitungsstatus, COUNT(*)
            FROM kvbb_requests
            GROUP BY bearbeitungsstatus;
        """)

        rows = cur.fetchall()

        stats = {
            "total": total,
            "pending": 0,
            "in_progress": 0,
            "approved": 0,
            "rejected": 0
        }

        for status, count in rows:
            status = (status or "").lower()

            if status in ["widerspruch", "pending_review"]:
                stats["pending"] += count
            elif status in ["in_bearbeitung", "in_progress"]:
                stats["in_progress"] += count
            elif status in ["erfolgreich", "approved"]:
                stats["approved"] += count
            else:
                stats["rejected"] += count

        return stats

    except Exception as e:
        return {
            "error": str(e),
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "approved": 0,
            "rejected": 0
        }

    finally:
        if conn:
            conn.close()


# ===== 趋势数据 =====
def get_case_trend():
    conn = None
    try:
        conn = psycopg.connect(os.environ["DB_URL"])
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(eingangsdatum), COUNT(*)
            FROM kvbb_requests
            GROUP BY DATE(eingangsdatum)
            ORDER BY DATE(eingangsdatum);
        """)

        rows = cur.fetchall()

        return [
            {"date": str(r[0]), "count": r[1]}
            for r in rows
        ]

    except Exception as e:
        return []

    finally:
        if conn:
            conn.close()


def get_cases_by_status(status):
    import psycopg
    import os

    conn = psycopg.connect(os.environ["DB_URL"])
    cur = conn.cursor()

    query_map = {
        "pending": "WHERE bearbeitungsstatus IN ('widerspruch')",
        "in_progress": "WHERE bearbeitungsstatus IN ('in_bearbeitung')",
        "approved": "WHERE bearbeitungsstatus IN ('erfolgreich')",
        "rejected": "WHERE bearbeitungsstatus NOT IN ('widerspruch','in_bearbeitung','erfolgreich')"
    }

    query = f"""
        SELECT vorgangsnummer, bearbeitungsstatus, eingangsdatum
        FROM kvbb_requests
        {query_map.get(status, "")}
        ORDER BY eingangsdatum DESC
        LIMIT 20;
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "case_id": r[0],
            "status": r[1],
            "created_at": str(r[2])
        }
        for r in rows
    ]