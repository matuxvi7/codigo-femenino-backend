import math
from typing import Any, Dict, List, Optional, Tuple
from src.db import get_db_cursor

ARTICLE_FIELDS = (
    "title",
    "slug",
    "category_id",
    "excerpt",
    "author",
    "read_time_minutes",
    "status",
    "published_at",
    "image_url",
    "image_public_id",
)


class ArticleRepository:
    @staticmethod
    def get_paginated(
        category_slug: Optional[str] = None,
        status: Optional[str] = "published",
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        conditions = []
        params = []

        if status:
            conditions.append("a.status = %s")
            params.append(status)

        if category_slug:
            conditions.append("c.slug = %s")
            params.append(category_slug)

        if search:
            conditions.append("(a.title LIKE %s OR a.excerpt LIKE %s)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            {where_clause}
        """

        offset = (page - 1) * per_page
        list_sql = f"""
            SELECT 
                a.id,
                a.slug,
                a.title,
                a.excerpt,
                a.author,
                a.image_url,
                a.image_public_id,
                a.published_at,
                a.read_time_minutes,
                a.status,
                a.created_at,
                c.id AS category_id,
                c.slug AS category_slug,
                c.name AS category_name
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            {where_clause}
            ORDER BY a.published_at DESC, a.id DESC
            LIMIT %s OFFSET %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(count_sql, tuple(params))
            total_row = cursor.fetchone()
            total_items = total_row["total"] if total_row else 0

            cursor.execute(list_sql, tuple(params + [per_page, offset]))
            items = cursor.fetchall()

        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

        formatted_items = []
        for row in items:
            formatted_items.append({
                "id": row["id"],
                "slug": row["slug"],
                "title": row["title"],
                "excerpt": row["excerpt"],
                "author": row["author"],
                "image_url": row["image_url"],
                "image_public_id": row["image_public_id"],
                "published_at": str(row["published_at"]) if row["published_at"] else None,
                "read_time_minutes": row["read_time_minutes"],
                "status": row["status"],
                "category": {
                    "id": row["category_id"],
                    "slug": row["category_slug"],
                    "name": row["category_name"]
                }
            })

        return {
            "items": formatted_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    @staticmethod
    def get_by_slug(slug: str, status: Optional[str] = "published") -> Optional[Dict[str, Any]]:
        conditions = ["a.slug = %s"]
        params = [slug]

        if status:
            conditions.append("a.status = %s")
            params.append(status)

        sql = f"""
            SELECT 
                a.id,
                a.category_id,
                a.slug,
                a.title,
                a.excerpt,
                a.author,
                a.image_url,
                a.image_public_id,
                a.published_at,
                a.read_time_minutes,
                a.status,
                a.created_at,
                a.updated_at,
                c.slug AS category_slug,
                c.name AS category_name,
                c.description AS category_description
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            WHERE {' AND '.join(conditions)}
            LIMIT 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, tuple(params))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row["id"],
                "slug": row["slug"],
                "title": row["title"],
                "excerpt": row["excerpt"],
                "author": row["author"],
                "image_url": row["image_url"],
                "image_public_id": row["image_public_id"],
                "published_at": str(row["published_at"]) if row["published_at"] else None,
                "read_time_minutes": row["read_time_minutes"],
                "status": row["status"],
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "updated_at": str(row["updated_at"]) if row["updated_at"] else None,
                "category": {
                    "id": row["category_id"],
                    "slug": row["category_slug"],
                    "name": row["category_name"],
                    "description": row["category_description"]
                }
            }

    @staticmethod
    def get_sections(article_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT position, heading, content
            FROM article_sections
            WHERE article_id = %s
            ORDER BY position ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (article_id,))
            return cursor.fetchall()

    @staticmethod
    def get_related(article_id: int, category_id: int, limit: int = 3) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                a.id,
                a.slug,
                a.title,
                a.excerpt,
                a.author,
                a.image_url,
                a.image_public_id,
                a.published_at,
                a.read_time_minutes,
                c.slug AS category_slug,
                c.name AS category_name
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            WHERE a.category_id = %s 
              AND a.id != %s 
              AND a.status = 'published'
            ORDER BY a.published_at DESC
            LIMIT %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (category_id, article_id, limit))
            items = cursor.fetchall()
            return [
                {
                    "slug": row["slug"],
                    "title": row["title"],
                    "excerpt": row["excerpt"],
                    "author": row["author"],
                    "image_url": row["image_url"],
                    "image_public_id": row["image_public_id"],
                    "published_at": str(row["published_at"]) if row["published_at"] else None,
                    "read_time_minutes": row["read_time_minutes"],
                    "category": {
                        "slug": row["category_slug"],
                        "name": row["category_name"]
                    }
                }
                for row in items
            ]

    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        sql = """
            INSERT INTO articles (
                category_id, slug, title, excerpt, author, published_at, read_time_minutes, status,
                image_url, image_public_id
            ) VALUES (
                %(category_id)s, %(slug)s, %(title)s, %(excerpt)s, %(author)s,
                COALESCE(%(published_at)s, CURRENT_DATE), %(read_time_minutes)s, %(status)s,
                %(image_url)s, %(image_public_id)s
            )
        """
        with get_db_cursor() as cursor:
            article_data = {key: data[key] for key in ARTICLE_FIELDS if key in data}
            cursor.execute(sql, article_data)
            article_id = cursor.lastrowid

            sections = data.get("sections", [])
            if sections:
                section_sql = """
                    INSERT INTO article_sections (article_id, position, heading, content)
                    VALUES (%s, %s, %s, %s)
                """
                for s in sections:
                    cursor.execute(section_sql, (article_id, s["position"], s.get("heading"), s["content"]))

            return article_id

    @staticmethod
    def update(slug: str, data: Dict[str, Any]) -> bool:
        fields = []
        params = {}
        for key in (
            "title",
            "excerpt",
            "author",
            "published_at",
            "read_time_minutes",
            "status",
            "category_id",
            "image_url",
            "image_public_id",
        ):
            if key in data:
                fields.append(f"{key} = %({key})s")
                params[key] = data[key]

        with get_db_cursor() as cursor:
            if fields:
                params["old_slug"] = slug
                update_sql = f"UPDATE articles SET {', '.join(fields)} WHERE slug = %(old_slug)s"
                cursor.execute(update_sql, params)

            if "sections" in data:
                cursor.execute("SELECT id FROM articles WHERE slug = %s", (slug,))
                row = cursor.fetchone()
                if row:
                    art_id = row["id"]
                    cursor.execute("DELETE FROM article_sections WHERE article_id = %s", (art_id,))
                    section_sql = """
                        INSERT INTO article_sections (article_id, position, heading, content)
                        VALUES (%s, %s, %s, %s)
                    """
                    for s in data["sections"]:
                        cursor.execute(section_sql, (art_id, s["position"], s.get("heading"), s["content"]))

            return True

    @staticmethod
    def delete(slug: str) -> bool:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM articles WHERE slug = %s", (slug,))
            return cursor.rowcount > 0
