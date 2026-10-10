from typing import Any, Dict, List, Optional
from src.repositories.article_repository import ArticleRepository


class ArticleService:
    @staticmethod
    def list_articles(
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = "published",
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        return ArticleRepository.get_paginated(
            category_slug=category_slug,
            search=search,
            status=status,
            page=page,
            per_page=per_page,
        )

    @staticmethod
    def get_article_detail(slug: str, status: Optional[str] = "published") -> Optional[Dict[str, Any]]:
        article = ArticleRepository.get_by_slug(slug, status=status)
        if not article:
            return None

        # Obtener secciones ordenadas
        sections = ArticleRepository.get_sections(article["id"])
        article["sections"] = [
            {
                "position": s["position"],
                "heading": s["heading"],
                "content": s["content"]
            }
            for s in sections
        ]

        # Obtener artículos relacionados en la misma categoría
        related = ArticleRepository.get_related(
            article_id=article["id"],
            category_id=article["category"]["id"],
            limit=3
        )
        article["related_articles"] = related

        return article

    @staticmethod
    def create_article(data: Dict[str, Any]) -> Dict[str, Any]:
        article_id = ArticleRepository.create(data)
        created = ArticleRepository.get_by_slug(data["slug"], status=None)
        return created or {"id": article_id, "slug": data["slug"]}

    @staticmethod
    def update_article(slug: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = ArticleRepository.get_by_slug(slug, status=None)
        if not existing:
            return None

        ArticleRepository.update(slug, data)
        target_slug = data.get("slug", slug)
        return ArticleRepository.get_by_slug(target_slug, status=None)

    @staticmethod
    def delete_article(slug: str) -> bool:
        return ArticleRepository.delete(slug)
