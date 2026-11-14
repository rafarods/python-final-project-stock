import sqlite3
import config
import logging
import modules.crypt as crypt
import modules.utils as utils

logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s -- %(message)s")
logger = logging.getLogger(__name__)

def _init_db(connection: sqlite3.Connection) -> None:
    """
    Inicialización:
    * Creación de tablas: categories, products y users.
    * Inserción del superusuario.
    """
    sqls: tuple = (
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        normalized_name TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        normalized_name TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL,
        currency TEXT NOT NULL,
        price FLOAT NOT NULL,
        UNIQUE (category_id, normalized_name),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        can_change_password BOOL NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS product_imports (
        id INTEGER PRIMARY KEY,
        process_id TEXT NOT NULL,
        line INTEGER NOT NULL,
        username TEXT NOT NULL,
        filename TEXT,
        name TEXT,
        normalized_name TEXT,
        description TEXT,
        category TEXT,
        normalized_category TEXT,
        quantity TEXT,
        quantity_value INT,
        currency TEXT,
        price TEXT,
        price_value FLOAT,
        status TEXT NOT NULL,
        create_at TEXT NOT NULL,
        UNIQUE (process_id, line)
    )
    """,
    "CREATE INDEX IF NOT EXISTS product_imports_idx1 ON product_imports (process_id, status)"
    )
    # Ejecutar sentencias SQL para la creación de la DB
    for sql in sqls:
        logger.debug("SQL: %r", sql)
        connection.execute(sql)
    add_admin_user(connection)
    connection.commit()

def add_admin_user(connection: sqlite3.Connection) -> None:
    """
    Agrega o actualiza el administrador.
    """
    username: str = utils.normalize_text(config.ADMIN["username"])
    password_hash: str = crypt.hash_password(config.ADMIN["password"])
    row = connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        count: int = connection.execute(
            "INSERT INTO users (username, password, role, can_change_password) VALUES (?, ?, ?, ?)",
            (username, password_hash, config.ROLE_ADMIN, False)
        ).rowcount
    else:
        count: int = connection.execute(
            "UPDATE users SET password = ?, role = ?, can_change_password = ? WHERE username = ?",
            (password_hash, config.ROLE_ADMIN, False, username)
        ).rowcount
    if count == 0:
        raise RuntimeError(f"Fallo al insertar o actualizar el usuario {config.ADMIN['username']}")

def get_connection() -> sqlite3.Connection:
    """
    Devuelve una conexión a la DB e inicializa la DB.
    """
    connection: sqlite3.Connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    _init_db(connection)
    return connection

def find_one(sql: str, params: tuple = ()) -> dict[str, str | int | float | bool] | None:
    """
    Devuelve una fila de una consulta.
    """
    connection: sqlite3.Connection | None = None
    try:
        connection = get_connection()
        cursor: sqlite3.Cursor = connection.execute(sql, params)
        row: sqlite3.Row | None = cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        if connection is not None:
            connection.close()

def find_all(sql: str, params: tuple = ()) -> list[dict]:
    """
    Devuelve todas las filas de una consulta.
    """
    logging.debug("SQL: %r => %r", sql, params)
    connection: sqlite3.Connection | None = None
    try:
        connection = get_connection()
        cursor: sqlite3.Cursor = connection.execute(sql, params)
        rows: list[sqlite3.Row] = cursor.fetchall()
        result: list[dict] = []
        for row in rows:
            result.append(dict(row))
        logger.debug("Returned %r rows", result)
        return result
    finally:
        if connection is not None:
            connection.close()

def execute_one(sql: str, params: tuple = (), ret_count: str = "rowcount") -> int:
    """
    Ejecutar una sentencia SQL: Update, Insert o Delete.
    """
    logging.debug("SQL: %r => %r", sql, params)
    connection: sqlite3.Connection | None = None
    try:
        connection = get_connection()
        cursor: sqlite3.Cursor = connection.execute(sql, params)
        connection.commit()
        result: int = 0
        if ret_count.casefold() == "lastrowid":
            result = cursor.lastrowid
            logger.debug("Last row ID [%r]", result)
        else:
            result = cursor.rowcount
            logger.debug("Affected %r rows", result)
        return result
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()

def execute_many(sql: str, params: list[tuple] = ()) -> int | None:
    """
    Ejecutar una consulta con una lista de parámetros
    """
    connection: sqlite3.Connection | None = None
    try:
        connection = get_connection()
        cursor: sqlite3.Cursor = connection.executemany(sql, params)
        connection.commit()
        return cursor.rowcount
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()

def insert(sql: str, params: tuple = ()) -> int | None:
    """
    Insertar un registro
    """
    return execute_one(sql, params, "lastrowid")

def update(sql: str, params: tuple = ()) -> int | None:
    """
    Actualizar un registro
    """
    return execute_one(sql, params)

def delete(sql: str, params: tuple = ()) -> int | None:
    """
    Eliminar un registro
    """
    return execute_one(sql, params)