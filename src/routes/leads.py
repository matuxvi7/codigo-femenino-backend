from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.extensions import limiter
from src.services.lead_service import LeadService
from src.utils.hateoas import build_paginated_response
from src.validators import parse_pagination, validate_lead_payload

leads_bp = Blueprint("leads", __name__)


@leads_bp.post("/leads")
@limiter.shared_limit("10 per minute; 30 per hour", scope="public-lead-forms")
def create_lead():
    payload = request.get_json(silent=True)
    is_valid, errors, clean_data = validate_lead_payload(payload)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Datos de suscripción incompletos o incorrectos.",
            "details": errors
        }), 400

    result = LeadService.register_lead(
        email=clean_data["email"],
        full_name=clean_data.get("full_name"),
        source=clean_data["source"]
    )
    return jsonify(result), 200


@leads_bp.post("/newsletter")
@limiter.shared_limit("10 per minute; 30 per hour", scope="public-lead-forms")
def subscribe_newsletter():
    """Endpoint directo para suscripción al newsletter general."""
    payload = request.get_json(silent=True) or {}
    payload["source"] = "newsletter"
    is_valid, errors, clean_data = validate_lead_payload(payload)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Datos de suscripción no válidos.",
            "details": errors
        }), 400

    result = LeadService.register_lead(
        email=clean_data["email"],
        full_name=clean_data.get("full_name"),
        source="newsletter"
    )
    return jsonify(result), 200


@leads_bp.post("/guia-gratuita")
@limiter.shared_limit("10 per minute; 30 per hour", scope="public-lead-forms")
def subscribe_guia_gratuita():
    """Endpoint directo para descarga de guía gratuita / ebook inicial."""
    payload = request.get_json(silent=True) or {}
    payload["source"] = "guia_gratuita"
    is_valid, errors, clean_data = validate_lead_payload(payload)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Datos de suscripción no válidos.",
            "details": errors
        }), 400

    result = LeadService.register_lead(
        email=clean_data["email"],
        full_name=clean_data.get("full_name"),
        source="guia_gratuita"
    )
    return jsonify(result), 200


@leads_bp.get("/leads")
@jwt_required()
def list_leads():
    page, per_page = parse_pagination(request.args)
    source = request.args.get("source", "").strip() or None

    result = LeadService.list_leads(
        source=source,
        page=page,
        per_page=per_page,
    )

    extra_params = {}
    if source:
        extra_params["source"] = source

    response = build_paginated_response(
        data=result["items"],
        pagination=result["pagination"],
        endpoint=request.path,
        extra_params=extra_params,
    )
    # Metadato count adicional para compatibilidad
    response["count"] = len(result["items"])

    return jsonify(response), 200
