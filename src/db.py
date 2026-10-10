import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from src.config import Config

logger = logging.getLogger(__name__)

_pool = None


def get_pool() -> PooledDB:
    global _pool
    if _pool is None:
        try:
            _pool = PooledDB(
                creator=pymysql,
                mincached=Config.DB_POOL_MIN_CACHED,
                maxconnections=Config.DB_POOL_MAX_CONNECTIONS,
                blocking=True,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False,
                **Config.DB_SSL_OPTIONS,
            )
        except Exception as exc:
            logger.error(
                "No se pudo inicializar el pool MySQL (%s).",
                type(exc).__name__,
            )
            raise
    return _pool


@contextmanager
def get_db_cursor() -> Generator[DictCursor, None, None]:
    """
    Context manager que provee un cursor diccionario con manejo automático de
    commit en éxito, rollback en excepción y liberación de conexión al pool.
    """
    pool = get_pool()
    conn = pool.connection()
    try:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error(
                "Falló una operación de base de datos (%s).",
                type(exc).__name__,
            )
            raise
        finally:
            cursor.close()
    finally:
        conn.close()


def check_db_connection() -> Dict[str, Any]:
    """Verifica el estado de la conexión a la base de datos."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 AS ping")
            res = cursor.fetchone()
            if res and res.get("ping") == 1:
                return {"status": "connected", "database": Config.DB_NAME}
    except Exception as exc:
        logger.warning(
            "La comprobación de salud no pudo conectarse a MySQL (%s).",
            type(exc).__name__,
        )
        return {
            "status": "disconnected",
            "error": "No se pudo establecer conexión con la base de datos.",
        }
    return {"status": "unknown"}
