from flask import Blueprint, jsonify, request
from src.services.article_service import ArticleService
from src.validators import (
    parse_pagination,
    validate_article_payload,
    validate_slug,
)

articles_bp = Blueprint("articles", __name__, url_prefix="/articles")


@articles_bp.get("")
def list_articles():
    page, per_page = parse_pagination(request.args)
    category_slug = request.args.get("category", "").strip().lower() or None
    search = request.args.get("search", "").strip() or None
    status = request.args.get("status", "published").strip().lower()
    if status == "all":
        status = None

    result = ArticleService.list_articles(
        category_slug=category_slug,
        search=search,
        status=status,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "success": True,
        "data": result["items"],
        "pagination": result["pagination"]
    })


@articles_bp.get("/<slug>")
def get_article(slug: str):
    clean_slug = slug.strip().lower()
    include_all_statuses = request.args.get("preview", "false").lower() in ("true", "1")
    status = None if include_all_statuses else "published"

    article = ArticleService.get_article_detail(clean_slug, status=status)
    if not article:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": f"El artículo '{clean_slug}' no fue encontrado o no está publicado."
        }), 404

    return jsonify({
        "success": True,
        "data": article
    })


@articles_bp.post("")
def create_article():
    payload = request.get_json(silent=True)
    is_valid, errors, clean_data = validate_article_payload(payload, is_update=False)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Datos de artículo no válidos.",
            "details": errors
        }), 400

    created = ArticleService.create_article(clean_data)
    return jsonify({
        "success": True,
        "message": "Artículo creado con éxito.",
        "data": created
    }), 201


@articles_bp.put("/<slug>")
def update_article(slug: str):
    clean_slug = slug.strip().lower()
    payload = request.get_json(silent=True)
    is_valid, errors, clean_data = validate_article_payload(payload, is_update=True)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Datos de actualización no válidos.",
            "details": errors
        }), 400

    updated = ArticleService.update_article(clean_slug, clean_data)
    if not updated:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": f"El artículo '{clean_slug}' no fue encontrado."
        }), 404

    return jsonify({
        "success": True,
        "message": "Artículo actualizado con éxito.",
        "data": updated
    })


@articles_bp.delete("/<slug>")
def delete_article(slug: str):
    clean_slug = slug.strip().lower()
    deleted = ArticleService.delete_article(clean_slug)
    if not deleted:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": f"El artículo '{clean_slug}' no fue encontrado."
        }), 404

    return jsonify({
        "success": True,
        "message": f"El artículo '{clean_slug}' ha sido eliminado exitosamente."
    })
