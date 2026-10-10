from typing import Any, Dict, List, Optional
from src.repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    def list_categories() -> List[Dict[str, Any]]:
        categories = CategoryRepository.get_all()
        return [
            {
                "id": c["id"],
                "slug": c["slug"],
                "name": c["name"],
                "description": c["description"],
                "articles_count": c.get("articles_count", 0),
            }
            for c in categories
        ]

    @staticmethod
    def get_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        cat = CategoryRepository.get_by_slug(slug)
        if not cat:
            return None
        return {
            "id": cat["id"],
            "slug": cat["slug"],
            "name": cat["name"],
            "description": cat["description"],
            "articles_count": cat.get("articles_count", 0),
        }
