from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from src.services.article_service import ArticleService
from src.utils.hateoas import build_paginated_response
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
    raw_status = request.args.get("status")
    if raw_status is not None:
        clean_status = raw_status.strip().lower()
        status_filter = None if clean_status == "all" else clean_status
    else:
        status_filter = "published"

    if status_filter != "published":
        verify_jwt_in_request()

    result = ArticleService.list_articles(
        category_slug=category_slug,
        search=search,
        status=status_filter,
        page=page,
        per_page=per_page,
    )

    extra_params = {}
    if category_slug:
        extra_params["category"] = category_slug
    if search:
        extra_params["search"] = search
    if raw_status is not None and raw_status.strip():
        extra_params["status"] = raw_status.strip()

    return jsonify(build_paginated_response(
        data=result["items"],
        pagination=result["pagination"],
        endpoint=request.path,
        extra_params=extra_params,
    ))


@articles_bp.get("/<slug>")
def get_article(slug: str):
    clean_slug = slug.strip().lower()
    include_all_statuses = request.args.get("preview", "false").lower() in ("true", "1")
    if include_all_statuses:
        verify_jwt_in_request()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
