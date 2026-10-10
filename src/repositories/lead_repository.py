import math
from typing import Any, Dict, List, Optional
import pymysql
from src.db import get_db_cursor


class LeadRepository:
    @staticmethod
    def create(email: str, full_name: Optional[str], source: str) -> Dict[str, Any]:
        sql = """
            INSERT INTO lead_signups (email, full_name, source)
            VALUES (%s, %s, %s)
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute(sql, (email, full_name, source))
                lead_id = cursor.lastrowid
                return {
                    "id": lead_id,
                    "email": email,
                    "full_name": full_name,
                    "source": source,
                    "created": True
                }
        except pymysql.err.IntegrityError as e:
            # Error 1062 = Duplicate entry for key 'uq_lead_signups_email_source'
            if e.args[0] == 1062:
                return {
                    "email": email,
                    "full_name": full_name,
                    "source": source,
                    "created": False,
                    "already_registered": True
                }
            raise e

    @staticmethod
    def get_by_email_and_source(email: str, source: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT id, email, full_name, source, requested_at FROM lead_signups WHERE email = %s AND source = %s"
        with get_db_cursor() as cursor:
            cursor.execute(sql, (email, source))
            return cursor.fetchone()

    @staticmethod
    def list_all(source: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        sql = "SELECT id, email, full_name, source, requested_at FROM lead_signups"
        params = []
        if source:
            sql += " WHERE source = %s"
            params.append(source)
        sql += " ORDER BY requested_at DESC LIMIT %s"
        params.append(limit)

        with get_db_cursor() as cursor:
            cursor.execute(sql, tuple(params))
            items = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "email": r["email"],
                    "full_name": r["full_name"],
                    "source": r["source"],
                    "requested_at": str(r["requested_at"]) if r.get("requested_at") else None
                }
                for r in items
            ]

    @staticmethod
    def get_paginated(
        source: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        conditions = []
        params: List[Any] = []

        if source:
            conditions.append("source = %s")
            params.append(source)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_sql = f"SELECT COUNT(*) AS total FROM lead_signups {where_clause}"

        offset = (page - 1) * per_page
        list_sql = f"""
            SELECT id, email, full_name, source, requested_at
            FROM lead_signups
            {where_clause}
            ORDER BY requested_at DESC, id DESC
            LIMIT %s OFFSET %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(count_sql, tuple(params))
            total_row = cursor.fetchone()
            total_items = total_row["total"] if total_row else 0

            cursor.execute(list_sql, tuple(params + [per_page, offset]))
            items = cursor.fetchall()

        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

        formatted_items = [
            {
                "id": r["id"],
                "email": r["email"],
                "full_name": r["full_name"],
                "source": r["source"],
                "requested_at": str(r["requested_at"]) if r.get("requested_at") else None
            }
            for r in items
        ]

        return {
            "items": formatted_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }
