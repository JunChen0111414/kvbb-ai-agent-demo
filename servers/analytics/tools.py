import psycopg
import os

def get_case_statistics(payload=None):
    conn = psycopg.connect(os.environ["DB_URL"])
    cur = conn.cursor()

    # 总数
    cur.execute("SELECT COUNT(*) FROM kvbb_requests;")
    total = cur.fetchone()[0]

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
        if status in ["widerspruch"]:
            stats["pending"] += count
        elif status in ["in_bearbeitung"]:
            stats["in_progress"] += count
        elif status in ["erfolgreich"]:
            stats["approved"] += count
        else:
            stats["rejected"] += count

    return stats