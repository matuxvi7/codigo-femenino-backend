import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()


class Config:
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
    RESET_DEV_DATABASE_ON_STARTUP = os.getenv(
        "RESET_DEV_DATABASE_ON_STARTUP", "false"
    ).strip().lower() in ("true", "1", "yes", "on")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Base de datos MySQL
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "codigo_femenino")
    DB_SSL_REQUIRED = os.getenv("DB_SSL_REQUIRED", "false").strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )
    DB_SSL_CA = os.getenv("DB_SSL_CA", "").strip() or None
    if DB_SSL_REQUIRED and not DB_SSL_CA:
        raise ValueError("DB_SSL_CA es obligatorio cuando DB_SSL_REQUIRED está habilitado.")
    DB_SSL_OPTIONS = (
        {
            "ssl_ca": DB_SSL_CA,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
        if DB_SSL_CA
        else {}
    )

    DB_POOL_MIN_CACHED = int(os.getenv("DB_POOL_MIN_CACHED", "2"))
    DB_POOL_MAX_CONNECTIONS = int(os.getenv("DB_POOL_MAX_CONNECTIONS", "10"))
