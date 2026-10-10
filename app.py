import os
from flask import Flask, jsonify
from flask_cors import CORS
from src.config import Config
from src.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de CORS para permitir consumo desde el frontend
    CORS(
        app,
        resources={r"/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # Registrar rutas principales bajo /api
    app.register_blueprint(api)

    @app.route("/")
    def index():
        return jsonify({
            "service": "Código Femenino - API Backend",
            "version": "1.0.0",
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
    app = create_app()
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
