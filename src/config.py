import os
from urllib.parse import urlsplit

from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()


def _parse_origins(value: str) -> list[str]:
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


def _is_example_value(value: str | None) -> bool:
    if not value:
        return True

    normalized = value.strip().casefold()
    placeholders = {
        "admin",
        "administrator",
        "change_me",
        "change-me",
        "changeme",
        "contrasena",
        "contraseña",
        "example",
        "password",
        "secret",
        "secret_key",
        "test",
        "tu_contrasena",
        "tu_contraseña",
        "tu_usuario",
        "user",
        "username",
        "usuario",
    }
    prefixes = (
        "change_me_",
        "change-me-",
        "changeme_",
        "example_",
        "example-",
        "replace_me",
        "replace-me",
        "test_",
        "test-",
        "your_",
        "your-",
    )
    return normalized in placeholders or normalized.startswith(prefixes)


class Config:
    PORT = int(os.getenv("PORT", "5000"))
    APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
    DEBUG = APP_ENV == "development" and os.getenv(
        "FLASK_DEBUG", "true"
    ).strip().lower() in ("true", "1", "t", "yes", "on")
    RESET_DEV_DATABASE_ON_STARTUP = os.getenv(
        "RESET_DEV_DATABASE_ON_STARTUP", "false"
    ).strip().lower() in ("true", "1", "yes", "on")
    CORS_ORIGINS = _parse_origins(
        os.getenv("CORS_ORIGINS", "*" if APP_ENV == "development" else "")
    )

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
    if APP_ENV == "production" and "DB_SSL_REQUIRED" not in os.environ:
        DB_SSL_REQUIRED = True
    DB_SSL_CA = os.getenv("DB_SSL_CA", "").strip() or None
    DB_SSL_OPTIONS = (
        {
            "ssl_ca": DB_SSL_CA,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
        if DB_SSL_CA
        else {}
    )

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip() or None
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "").strip() or None
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "").strip() or None

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip() or None
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or None
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or None
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60
    REDIS_URL = os.getenv("REDIS_URL", "").strip() or None
    RATE_LIMIT_STORAGE_URI = REDIS_URL or "memory://"

    DB_POOL_MIN_CACHED = int(os.getenv("DB_POOL_MIN_CACHED", "2"))
    DB_POOL_MAX_CONNECTIONS = int(os.getenv("DB_POOL_MAX_CONNECTIONS", "10"))

    @classmethod
    def validate(cls) -> None:
        if cls.APP_ENV not in ("development", "production"):
            raise ValueError("APP_ENV debe ser 'development' o 'production'.")

        if cls.APP_ENV == "development":
            return

        required_variables = (
            "DB_HOST",
            "DB_PORT",
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "CORS_ORIGINS",
            "ADMIN_USERNAME",
            "ADMIN_PASSWORD",
            "JWT_SECRET_KEY",
            "REDIS_URL",
        )
        missing_variables = [
            name
            for name in required_variables
            if not getattr(cls, name, None)
            or not str(getattr(cls, name)).strip()
        ]
        if missing_variables:
            raise ValueError(
                "Faltan variables requeridas para producción: "
                + ", ".join(missing_variables)
                + "."
            )

        if cls.RESET_DEV_DATABASE_ON_STARTUP:
            raise ValueError(
                "RESET_DEV_DATABASE_ON_STARTUP debe ser false en producción."
            )
        if _is_example_value(cls.ADMIN_USERNAME):
            raise ValueError(
                "ADMIN_USERNAME no puede ser un valor vacío o de ejemplo."
            )
        if _is_example_value(cls.ADMIN_PASSWORD):
            raise ValueError(
                "ADMIN_PASSWORD no puede ser un valor vacío o de ejemplo."
            )
        if len(cls.JWT_SECRET_KEY.strip().encode("utf-8")) < 32:
            raise ValueError(
                "JWT_SECRET_KEY debe contener al menos 32 bytes aleatorios."
            )
        if _is_example_value(cls.JWT_SECRET_KEY):
            raise ValueError(
                "JWT_SECRET_KEY no puede ser un valor de ejemplo."
            )
        if len(cls.ADMIN_PASSWORD.strip()) < 12:
            raise ValueError(
                "ADMIN_PASSWORD debe contener al menos 12 caracteres."
            )
        try:
            redis_url = urlsplit(cls.REDIS_URL)
            redis_url.port
        except ValueError:
            raise ValueError(
                "REDIS_URL debe ser una URI válida de un servicio Redis externo."
            ) from None
        if (
            redis_url.scheme not in ("redis", "rediss")
            or not redis_url.hostname
            or redis_url.path not in ("", "/") and not redis_url.path[1:].isdigit()
        ):
            raise ValueError(
                "REDIS_URL debe ser una URI redis:// o rediss:// válida."
            )
        if not cls.DB_SSL_REQUIRED or not cls.DB_SSL_CA:
            raise ValueError(
                "Producción requiere DB_SSL_REQUIRED=true y DB_SSL_CA configurado."
            )
        if not os.path.isabs(cls.DB_SSL_CA) or not os.path.isfile(cls.DB_SSL_CA):
            raise ValueError(
                "DB_SSL_CA debe apuntar a un archivo CA existente, como un Render Secret File."
            )
        if not cls.CORS_ORIGINS or "*" in cls.CORS_ORIGINS:
            raise ValueError(
                "CORS_ORIGINS debe enumerar explícitamente los orígenes de producción."
            )

        for origin in cls.CORS_ORIGINS:
            try:
                parsed_origin = urlsplit(origin)
                hostname = parsed_origin.hostname
                parsed_origin.port
            except ValueError:
                raise ValueError(
                    "Cada origen de producción en CORS_ORIGINS debe ser una URL HTTPS exacta."
                ) from None
            if (
                parsed_origin.scheme != "https"
                or not parsed_origin.netloc
                or not hostname
                or parsed_origin.username
                or parsed_origin.password
                or parsed_origin.path
                or parsed_origin.query
                or parsed_origin.fragment
                or "*" in origin
                or any(character.isspace() for character in origin)
            ):
                raise ValueError(
                    "Cada origen de producción en CORS_ORIGINS debe ser una URL HTTPS exacta."
                )

        cloudinary_credentials = (
            cls.CLOUDINARY_CLOUD_NAME,
            cls.CLOUDINARY_API_KEY,
            cls.CLOUDINARY_API_SECRET,
        )
        if any(cloudinary_credentials) and not all(cloudinary_credentials):
            raise ValueError(
                "Configura juntas CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y "
                "CLOUDINARY_API_SECRET, o deja las tres vacías."
            )

    @classmethod
    def admin_auth_is_configured(cls) -> bool:
        return (
            bool(cls.ADMIN_USERNAME and cls.ADMIN_USERNAME.strip())
            and not _is_example_value(cls.ADMIN_USERNAME)
            and bool(cls.ADMIN_PASSWORD and cls.ADMIN_PASSWORD.strip())
            and not _is_example_value(cls.ADMIN_PASSWORD)
            and len(cls.ADMIN_PASSWORD.strip()) >= 12
            and bool(cls.JWT_SECRET_KEY and cls.JWT_SECRET_KEY.strip())
            and not _is_example_value(cls.JWT_SECRET_KEY)
            and len(cls.JWT_SECRET_KEY.strip().encode("utf-8")) >= 32
        )
