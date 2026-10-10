from flask import Blueprint, jsonify
from src.db import check_db_connection

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    db_status = check_db_connection()
    status_code = 200 if db_status.get("status") == "connected" else 503
    return jsonify({
        "status": "ok" if status_code == 200 else "degraded",
        "service": "codigo-femenino-backend",
        "database": db_status
    }), status_code
