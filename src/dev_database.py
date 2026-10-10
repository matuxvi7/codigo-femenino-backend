import logging
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT

from src.config import Config

logger = logging.getLogger(__name__)


def reset_development_database() -> None:
    if not Config.RESET_DEV_DATABASE_ON_STARTUP:
        return
    if Config.APP_ENV != "development":
        raise RuntimeError(
            "RESET_DEV_DATABASE_ON_STARTUP solo se permite con APP_ENV=development."
        )

    database_name = Config.DB_NAME.replace("`", "``")
    init_script = Path(__file__).resolve().parent.parent / "scripts" / "init_db.sql"
    sql = init_script.read_text(encoding="utf-8")

    logger.warning("Reiniciando la base de datos de desarrollo '%s'.", Config.DB_NAME)
    connection = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        autocommit=True,
        client_flag=CLIENT.MULTI_STATEMENTS,
        **Config.DB_SSL_OPTIONS,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{database_name}`")
            cursor.execute(sql)
            while cursor.nextset() is not None:
                pass
    finally:
        connection.close()
    logger.warning("Base de datos de desarrollo lista con los datos de ejemplo.")
