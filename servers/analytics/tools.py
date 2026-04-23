import httpx
import psycopg
import os
from collections import Counter
from dotenv import load_dotenv

# ===== 加载环境变量 =====
load_dotenv()

USE_N8N = os.getenv("USE_N8N", "true").lower() == "true"
N8N_URL = os.getenv("N8N_BASE_URL")
DB_URL = os.getenv("DB_URL")

# ===== 安全检查 =====
if USE_N8N and not N8N_URL:
    raise ValueError("Missing N8N_BASE_URL environment variable")

if not USE_N8N and not DB_URL:
    raise ValueError("Missing DB_URL environment variable")


# ===== 数据标准化（关键）=====
def _normalize(item):
    return {
        "case_id": item.get("vorgangsnummer"),
        "status": item.get("bearbeitungsstatus"),
        "created_at": item.get("eingangsdatum"),
        "raw": item
    }


# ===== PostgreSQL =====
def _fetch_from_db():
    try:
        print("👉 Using PostgreSQL data source")

        conn = psycopg.connect(DB_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM kvbb_requests;")
        rows = cur.fetchall()

        cols = [desc[0] for desc in cur.description]
        conn.close()

        data = [dict(zip(cols, row)) for row in rows]
        return [_normalize(x) for x in data]

    except Exception as e:
        print("❌ DB error:", e)
        raise


# ===== n8n =====
def _fetch_from_n8n():
    try:
        print("👉 Using n8n data source")

        res = httpx.get(
            f"{N8N_URL}/b75d488b-93fd-4a78-afc4-d25133d8d577",
            timeout=5
        )
        res.raise_for_status()

        data = res.json()

        if not isinstance(data, list):
            raise ValueError("n8n response is not a list")

        return [_normalize(x) for x in data]

    except Exception as e:
        print("❌ n8n error:", e)
        raise


# ===== 统一入口（带 fallback）=====
def _fetch_cases():
    if USE_N8N:
        try:
            return _fetch_from_n8n()
        except Exception:
            print("⚠️ Falling back to PostgreSQL...")
            return _fetch_from_db()
    else:
        try:
            return _fetch_from_db()
        except Exception:
            print("⚠️ Falling back to n8n...")
            return _fetch_from_n8n()


# ===== KPI =====
def get_case_statistics(payload=None):
    data = _fetch_cases()

    stats = {
        "total": len(data),
        "pending": 0,
        "in_progress": 0,
        "approved": 0,
        "rejected": 0
    }

    for item in data:
        status = (item["status"] or "").lower()

        if status in ["widerspruch", "pending_review"]:
            stats["pending"] += 1
        elif status in ["in_bearbeitung", "in_progress"]:
            stats["in_progress"] += 1
        elif status in ["erfolgreich", "approved"]:
            stats["approved"] += 1
        else:
            stats["rejected"] += 1

    return stats


# ===== Trend =====
def get_case_trend():
    data = _fetch_cases()

    counts = Counter()

    for item in data:
        date = item["created_at"]
        if date:
            counts[str(date)[:10]] += 1

    return [
        {"date": k, "count": v}
        for k, v in sorted(counts.items())
    ]


# ===== Drill-down =====
def get_cases_by_status(status):
    data = _fetch_cases()

    result = []

    for item in data:
        s = (item["status"] or "").lower()

        if status == "pending" and s == "widerspruch":
            result.append(item)
        elif status == "in_progress" and s == "in_bearbeitung":
            result.append(item)
        elif status == "approved" and s == "erfolgreich":
            result.append(item)
        elif status == "rejected":
            result.append(item)

    return result[:20]