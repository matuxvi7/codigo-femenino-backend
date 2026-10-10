from flask import Blueprint, jsonify
from src.routes.health import health_bp
from src.routes.categories import categories_bp
from src.routes.articles import articles_bp
from src.routes.leads import leads_bp
from src.routes.admin_auth import admin_auth_bp

api = Blueprint("api", __name__, url_prefix="/api")

# Registrar sub-módulos dentro del blueprint /api
api.register_blueprint(health_bp)
api.register_blueprint(categories_bp)
api.register_blueprint(articles_bp)
api.register_blueprint(leads_bp)
api.register_blueprint(admin_auth_bp)


@api.app_errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "BAD_REQUEST",
        "message": "Petición no válida o formato incorrecto."
    }), 400


@api.app_errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "NOT_FOUND",
        "message": "El recurso solicitado no existe."
    }), 404


@api.app_errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "METHOD_NOT_ALLOWED",
        "message": "Método HTTP no permitido para este endpoint."
    }), 405


@api.app_errorhandler(429)
def too_many_requests(error):
    response = error.get_response()
    response.set_data(jsonify({
        "success": False,
        "error": "RATE_LIMIT_EXCEEDED",
        "message": "Se excedió el límite de solicitudes. Intenta nuevamente más tarde.",
    }).get_data())
    response.content_type = "application/json"
    return response


@api.app_errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": "INTERNAL_SERVER_ERROR",
        "message": "Ha ocurrido un error interno en el servidor."
    }), 500
