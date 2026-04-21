from __future__ import annotations

from contextlib import closing

import psycopg


def normalize_status(raw_status: str | None) -> str:
    if not raw_status:
        return "in_progress"

    value = raw_status.strip().lower()

    mapping = {
        "neu": "new",
        "eingegangen": "new",
        "offen": "new",
        "in_bearbeitung": "in_progress",
        "bearbeitung": "in_progress",
        "processing": "in_progress",
        "widerspruch": "pending_review",
        "prüfung": "pending_review",
        "pruefung": "pending_review",
        "review": "pending_review",
        "freigegeben": "approved",
        "genehmigt": "approved",
        "approved": "approved",
        "abgelehnt": "rejected",
        "deny": "rejected",
        "denied": "rejected",
        "rejected": "rejected",
        "gesperrt": "blocked",
        "blocked": "blocked",
    }

    return mapping.get(value, "in_progress")


def normalize_next_action(normalized_status: str) -> str:
    mapping = {
        "new": "triage",
        "in_progress": "processing",
        "pending_review": "human_review",
        "approved": "notify",
        "rejected": "notify",
        "blocked": "manual_check",
    }
    return mapping.get(normalized_status, "processing")


def raw_statuses_for_filter(normalized_statuses: list[str]) -> list[str]:
    reverse_mapping = {
        "new": ["neu", "eingegangen", "offen"],
        "in_progress": ["in_bearbeitung", "bearbeitung", "processing"],
        "pending_review": ["widerspruch", "prüfung", "pruefung", "review"],
        "approved": ["freigegeben", "genehmigt", "approved"],
        "rejected": ["abgelehnt", "deny", "denied", "rejected"],
        "blocked": ["gesperrt", "blocked"],
    }

    raw_values: list[str] = []
    for status in normalized_statuses:
        raw_values.extend(reverse_mapping.get(status, [status]))

    seen = set()
    deduped: list[str] = []
    for value in raw_values:
        lowered = value.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(value)

    return deduped


class BusinessRepository:
    def __init__(self, db_url: str, db_schema: str = "public") -> None:
        self.db_url = db_url
        self.db_schema = db_schema

    def get_case_status(self, case_id: str) -> dict:
        sql = f"""
            SELECT
                vorgangsnummer AS case_id,
                bearbeitungsstatus AS status,
                ki_ergebnis AS substatus,
                human_review AS owner_team,
                updated_at
            FROM {self.db_schema}.kvbb_requests
            WHERE vorgangsnummer = %s
            LIMIT 1
        """

        with closing(psycopg.connect(self.db_url)) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (case_id,))
                row = cur.fetchone()

        if not row:
            raise ValueError(f"Case not found: {case_id}")

        normalized_status = normalize_status(row[1])

        return {
            "case_id": row[0],
            "status": normalized_status,
            "substatus": row[2],
            "owner_team": row[3],
            "updated_at": row[4].isoformat() if row[4] else None,
            "next_action": normalize_next_action(normalized_status),
            "source_system": "kvbb-azure",
        }

    def search_cases(self, filters: dict, limit: int) -> dict:
        conditions = []
        params: list = []

        if filters.get("customer_id"):
            conditions.append("betriebsstaette = %s")
            params.append(filters["customer_id"])

        if filters.get("statuses"):
            raw_statuses = raw_statuses_for_filter(filters["statuses"])
            placeholders = ", ".join(["%s"] * len(raw_statuses))
            conditions.append(f"LOWER(bearbeitungsstatus) IN ({placeholders})")
            params.extend([status.lower() for status in raw_statuses])

        if filters.get("created_after"):
            conditions.append("eingangsdatum > %s")
            params.append(filters["created_after"])

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
            SELECT
                vorgangsnummer AS case_id,
                bearbeitungsstatus AS status,
                eingangsdatum AS created_at
            FROM {self.db_schema}.kvbb_requests
            {where_clause}
            ORDER BY eingangsdatum DESC
            LIMIT %s
        """
        params.append(limit)

        count_sql = f"""
            SELECT COUNT(*)
            FROM {self.db_schema}.kvbb_requests
            {where_clause}
        """

        with closing(psycopg.connect(self.db_url)) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

                cur.execute(count_sql, params[:-1])
                count_row = cur.fetchone()

        items = [
            {
                "case_id": row[0],
                "status": normalize_status(row[1]),
                "created_at": row[2].isoformat() if row[2] else None,
            }
            for row in rows
        ]

        return {
            "items": items,
            "count": count_row[0] if count_row else 0,
        }