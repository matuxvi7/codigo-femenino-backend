from flask import Blueprint, jsonify, request
from src.services.lead_service import LeadService
from src.validators import validate_lead_payload

leads_bp = Blueprint("leads", __name__)


@leads_bp.post("/leads")
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
def list_leads():
    source = request.args.get("source")
    leads = LeadService.list_leads(source=source)
    return jsonify({
        "success": True,
        "count": len(leads),
        "data": leads
    })
