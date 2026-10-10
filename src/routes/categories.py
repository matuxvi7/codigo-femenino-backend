from flask import Blueprint, jsonify
from src.services.category_service import CategoryService

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.get("")
def list_categories():
    categories = CategoryService.list_categories()
    return jsonify({
        "success": True,
        "count": len(categories),
        "data": categories
    })


@categories_bp.get("/<slug>")
def get_category(slug: str):
    category = CategoryService.get_category_by_slug(slug.strip().lower())
    if not category:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": f"La categoría '{slug}' no fue encontrada."
        }), 404

    return jsonify({
        "success": True,
        "data": category
    })
