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
                    "requested_at": str(r["requested_at"])
                }
                for r in items
            ]
