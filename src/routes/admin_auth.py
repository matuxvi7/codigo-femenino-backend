import hmac

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from src.config import Config
from src.extensions import limiter

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin/auth")


@admin_auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    if not Config.admin_auth_is_configured():
        return jsonify({
            "success": False,
            "error": "AUTHENTICATION_NOT_CONFIGURED",
            "message": "El acceso administrativo no está configurado.",
        }), 503

    credentials = request.get_json(silent=True)
    if not isinstance(credentials, dict):
        credentials = {}

    username = credentials.get("username")
    password = credentials.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return _invalid_credentials()

    username_matches = hmac.compare_digest(
        username.encode("utf-8"), Config.ADMIN_USERNAME.encode("utf-8")
    )
    password_matches = hmac.compare_digest(
        password.encode("utf-8"), Config.ADMIN_PASSWORD.encode("utf-8")
    )
    if not (username_matches and password_matches):
        return _invalid_credentials()

    access_token = create_access_token(identity=Config.ADMIN_USERNAME)
    return jsonify({
        "success": True,
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": Config.JWT_ACCESS_TOKEN_EXPIRES,
    }), 200


def _invalid_credentials():
    return jsonify({
        "success": False,
        "error": "INVALID_CREDENTIALS",
        "message": "Usuario o contraseña incorrectos.",
    }), 401
