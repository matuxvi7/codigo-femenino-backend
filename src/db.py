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
            )
        except Exception as e:
            logger.error("Error al inicializar pool de conexiones MySQL: %s", e)
            raise e
    return _pool


@contextmanager
def get_db_cursor() -> Generator[DictCursor, None, None]:
    """
    Context manager que provee un cursor diccionario con manejo automático de
    commit en éxito, rollback en excepción y liberación de conexión al pool.
    """
    pool = get_pool()
    conn = pool.connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Error en operación de base de datos: %s", exc)
        raise exc
    finally:
        cursor.close()
        conn.close()


def check_db_connection() -> Dict[str, Any]:
    """Verifica el estado de la conexión a la base de datos."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 AS ping")
            res = cursor.fetchone()
            if res and res.get("ping") == 1:
                return {"status": "connected", "database": Config.DB_NAME}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}
    return {"status": "unknown"}
