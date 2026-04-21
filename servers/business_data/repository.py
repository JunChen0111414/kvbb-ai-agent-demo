from __future__ import annotations

from contextlib import closing

import psycopg


class BusinessRepository:
    def __init__(self, db_url: str, db_schema: str = "public") -> None:
        self.db_url = db_url
        self.db_schema = db_schema

    def get_case_status(self, case_id: str) -> dict:
        sql = f"""
            SELECT
                case_id,
                status,
                substatus,
                owner_team,
                updated_at,
                next_action,
                source_system
            FROM {self.db_schema}.cases
            WHERE case_id = %s
            LIMIT 1
        """

        with closing(psycopg.connect(self.db_url)) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (case_id,))
                row = cur.fetchone()

        if not row:
            raise ValueError(f"Case not found: {case_id}")

        return {
            "case_id": row[0],
            "status": row[1],
            "substatus": row[2],
            "owner_team": row[3],
            "updated_at": row[4].isoformat() if row[4] else None,
            "next_action": row[5],
            "source_system": row[6] or "kvbb-core",
        }

    def search_cases(self, filters: dict, limit: int) -> dict:
        conditions = []
        params: list = []

        if filters.get("customer_id"):
            conditions.append("customer_id = %s")
            params.append(filters["customer_id"])

        if filters.get("statuses"):
            placeholders = ", ".join(["%s"] * len(filters["statuses"]))
            conditions.append(f"status IN ({placeholders})")
            params.extend(filters["statuses"])

        if filters.get("created_after"):
            conditions.append("created_at > %s")
            params.append(filters["created_after"])

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
            SELECT
                case_id,
                status,
                created_at
            FROM {self.db_schema}.cases
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """
        params.append(limit)

        count_sql = f"""
            SELECT COUNT(*)
            FROM {self.db_schema}.cases
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
                "status": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
            }
            for row in rows
        ]

        return {
            "items": items,
            "count": count_row[0] if count_row else 0,
        }