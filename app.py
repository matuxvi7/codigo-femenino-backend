from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.serving import is_running_from_reloader
from src.config import Config
from src.dev_database import reset_development_database
from src.extensions import limiter
from src.routes import api
from src.routes.docs import docs_bp


def create_app() -> Flask:
    Config.validate()
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["RATELIMIT_STORAGE_URI"] = Config.RATE_LIMIT_STORAGE_URI
    app.config["RATELIMIT_STRATEGY"] = "fixed-window"
    app.config["RATELIMIT_HEADERS_ENABLED"] = True
    app.config["RATELIMIT_IN_MEMORY_FALLBACK_ENABLED"] = False
    limiter.init_app(app)
    if Config.APP_ENV == "production":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(_reason: str):
        return jsonify({
            "success": False,
            "error": "AUTHENTICATION_REQUIRED",
            "message": "Se requiere un token de acceso válido.",
        }), 401

    @jwt.invalid_token_loader
    def invalid_token(_reason: str):
        return jsonify({
            "success": False,
            "error": "INVALID_TOKEN",
            "message": "El token de acceso no es válido.",
        }), 401

    @jwt.expired_token_loader
    def expired_token(_jwt_header: dict, _jwt_payload: dict):
        return jsonify({
            "success": False,
            "error": "TOKEN_EXPIRED",
            "message": "El token de acceso expiró. Inicia sesión nuevamente.",
        }), 401

    CORS(
        app,
        resources={r"/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # Registrar documentación interactiva Swagger en /docs
    app.register_blueprint(docs_bp)

    # Registrar rutas principales de la API bajo /api
    app.register_blueprint(api)

    @app.route("/")
    def index():
        return jsonify({
            "service": "Código Femenino - API Backend",
            "version": "1.0.0",
            "documentation": {
                "swagger_ui": "/docs",
                "openapi_spec": "/docs/openapi.yaml"
            },
            "endpoints": {
                "health": "/api/health",
                "categories": "/api/categories",
                "articles": "/api/articles",
                "leads": "/api/leads",
                "newsletter": "/api/newsletter",
                "guia_gratuita": "/api/guia-gratuita"
            }
        })

    return app


if __name__ == "__main__":
    if Config.APP_ENV == "development" and (
        not Config.DEBUG or is_running_from_reloader()
    ):
        reset_development_database()
    app = create_app()
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
