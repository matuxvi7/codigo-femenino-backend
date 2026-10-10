import os
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader
from src.config import Config
from src.dev_database import reset_development_database
from src.routes import api
from src.routes.docs import docs_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de CORS para permitir consumo desde el frontend
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
    if not Config.DEBUG or is_running_from_reloader():
        reset_development_database()
    app = create_app()
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
