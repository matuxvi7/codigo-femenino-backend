from typing import Any, Dict, List, Optional
from src.db import get_db_cursor


class CategoryRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                c.id, 
                c.slug, 
                c.name, 
                c.description, 
                c.created_at, 
                c.updated_at,
                COUNT(a.id) AS articles_count
            FROM categories c
            LEFT JOIN articles a ON a.category_id = c.id AND a.status = 'published'
            GROUP BY c.id
            ORDER BY c.id ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT 
                c.id, 
                c.slug, 
                c.name, 
                c.description, 
                c.created_at, 
                c.updated_at,
                COUNT(a.id) AS articles_count
            FROM categories c
            LEFT JOIN articles a ON a.category_id = c.id AND a.status = 'published'
            WHERE c.slug = %s
            GROUP BY c.id
            LIMIT 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (slug,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT id, slug, name, description FROM categories WHERE id = %s LIMIT 1"
        with get_db_cursor() as cursor:
            cursor.execute(sql, (category_id,))
            return cursor.fetchone()
