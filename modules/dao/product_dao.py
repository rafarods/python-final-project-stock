import config
import modules.database as database
import modules.utils as utils

def insert(params: dict[str, str | float | int | None]) -> int | None:
    """
    Inserta un producto
    """
    values: tuple = (
        params.get("category_id"),
        params.get("name"),
        utils.normalize_text(params.get("name")),
        params.get("description"),
        params.get("quantity"),
        params.get("currency"),
        params.get("price"),
    )
    return database.insert("""
    INSERT INTO products (category_id, name, normalized_name, description, quantity, currency, price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, values)

def count() -> int:
    """
    Devuelve el total de productos
    """
    row: dict = database.find_one("SELECT count(*) AS total FROM products")
    if row is None:
        return -1
    return row.get("total")

def count_imports() -> int:
    """
    Devuelve el total de productos importados
    """
    row: dict = database.find_one("SELECT count(*) AS total FROM product_imports")
    if row is None:
        return -1
    return row.get("total")

def delete(id: int) -> int | None:
    """
    Eliminar un producto
    """
    return database.delete("DELETE FROM products WHERE id = ?", id)

def delete_all() -> int:
    """
    Eliminar todos los productos
    """
    return database.delete("DELETE FROM products")

def delete_all_imports() -> int:
    """
    Eliminar todos los productos importados
    """
    return database.delete("DELETE FROM product_imports")

def update(id: int, params: dict[str, str | float | int]) -> int | None:
    """
    Actualizar los datos del producto
    """
    if "name" in params and "normalized_name" not in params:
        params["normalized_name"] = utils.normalize_text(str(params["name"]))
    fields: str = ""
    values: list = []
    for key in params:
        if fields:
            fields += ", "
        fields += f"{key} = ?"
        values.append(params.get(key))
    values += (id,)
    return database.update(f"UPDATE products SET {fields} WHERE id = ?", values)

def search_one(text: str | int) -> dict | None:
    """
    Buscar por ID o por palabras claves
    """
    nomalized_name = utils.normalize_text(text)
    if not nomalized_name:
        return None
    return database.find_one("""
    SELECT 
        pr.id, 
        pr.name, 
        pr.description,
        pr.currency, 
        pr.price,
        pr.quantity, 
        pr.category_id, 
        ct.name AS category
    FROM products AS pr
        JOIN categories AS ct
            ON pr.category_id = ct.id
    WHERE pr.normalized_name LIKE ? OR CAST(pr.id AS TEXT) = ?
    ORDER BY pr.name, ct.name
    """, (f"%{nomalized_name}%", str(text),))

def find_all(params: dict[str, str | int | bool] = {}) -> list[dict]:
    """
    Devuelve todos los productos
    """
    
    where: str = ""
    values: tuple = []
    if params:
        where += "WHERE "
        for key, value in params.items():
            if values:
                where += " AND "
            match key:
                case "category":
                    where += f"ct.name = ?"
                    values += (value,)
                case "search":
                    where += f"(pr.normalized_name LIKE ? OR LOWER(pr.description) LIKE ? OR CAST(pr.id AS TEXT) = ?)"
                    values += (
                        f"%{utils.normalize_text(value)}%", 
                        f"%{utils.normalize_text(value)}%", value,
                    )
                case _:
                    where += f"pr.{key} = ?"
                    values += (value,)
    return database.find_all(f"""
    SELECT 
        pr.id, 
        pr.name, 
        pr.description,
        pr.currency, 
        pr.price,
        pr.quantity, 
        pr.category_id, 
        ct.name AS category
    FROM products AS pr
        JOIN categories AS ct
            ON pr.category_id = ct.id
    {where}
    ORDER BY pr.normalized_name, ct.normalized_name
    """, values)

def exists(name: str) -> bool:
    """
    Indica si existe un producto
    """
    return database.find_one("SELECT id FROM products WHERE normalized_name = ? LIMIT 1", (utils.normalize_text(name),)) is not None

def save_import(process_id: str, params: list[tuple], auto_create: bool = False) -> dict[str, str | int | None] | None:
    """
    Importa los productos
    """
    connection = None
    try:
        connection = database.get_connection()
        connection.execute("BEGIN")
        
        # Insertar registros en la tabla de importación
        connection.executemany("""
        INSERT INTO product_imports (process_id, filename, username, name, normalized_name, category, normalized_category, quantity, currency, price, 
            status, create_at, line, description, price_value, quantity_Value) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, params)
        
        if auto_create:
            # Actualizar como erróneo los productos no encontrados
            connection.execute("""
            INSERT INTO categories (name, normalized_name)
                SELECT DISTINCT category, normalized_category
                FROM product_imports AS pi
                WHERE pi.process_id = ? 
                    AND pi.status = ? 
                    AND (pi.normalized_name IS NOT NULL OR pi.normalized_name <> '')
                    AND (pi.normalized_category IS NOT NULL OR pi.normalized_category <> '') 
                    AND NOT EXISTS (
                        SELECT 1
                        FROM categories AS c
                        WHERE pi.normalized_category = c.normalized_name
                    )
            """, (process_id, "SP0"))
            
            # Insertar nuevos productos
            connection.execute("""
            INSERT INTO products (category_id, name, normalized_name, description, quantity, currency, price)
                SELECT c.id, pi.name, pi.normalized_name, pi.description, CAST(pi.quantity AS INTEGER), pi.currency, CAST(pi.price AS FLOAT)
                FROM product_imports AS pi
                    JOIN categories AS c
                        ON pi.normalized_category = c.normalized_name
                WHERE pi.process_id = ? 
                    AND pi.status = ? 
                    AND (pi.normalized_name IS NOT NULL OR pi.normalized_name <> '') AND NOT EXISTS (
                        SELECT 1
                        FROM products AS p
                        WHERE pi.normalized_name = p.normalized_name
                    )
            """, (process_id, "SP0"))
        else:
            # Actualizar como erróneo los productos no encontrados
            connection.execute("""
            UPDATE product_imports
            SET status = ?
            WHERE product_imports.process_id = ? AND product_imports.status = ? AND (NOT EXISTS (
                SELECT 1
                FROM products
                WHERE product_imports.normalized_name = products.normalized_name
            ))
            """, ("ER8", process_id, "SP0"))
        
        # Insertar o actualizar nuevo productos con status=SP0
        connection.execute("""
        UPDATE products
        SET quantity = product_imports.quantity_value, 
            price = product_imports.price_value, 
            currency = product_imports.currency
        FROM product_imports
        WHERE products.normalized_name = product_imports.normalized_name AND product_imports.process_id = ? AND product_imports.status = ?
        """, (process_id, "SP0"))
        
        # Actualizar el estatus=PR0 de los registros importados
        connection.execute("""
        UPDATE product_imports
        SET status = ? 
        FROM products
        WHERE product_imports.normalized_name = products.normalized_name AND product_imports.process_id = ? AND product_imports.status = ?
        """, ("PR0", process_id, "SP0"))
        connection.commit()
        
        # Obtener estádisticas
        row_stats: dict = dict(connection.execute("""
        SELECT
            count(*) AS total_rows, 
            sum(status LIKE ?) AS total_valid,
            sum(status LIKE ?) AS total_invalid,
            sum(status LIKE ?) AS total_non_processing
        FROM product_imports 
        WHERE process_id = ?
        """, ("PR%", "ER%", "SP%", process_id)).fetchone())
        
        num_total: int = row_stats.get("total_rows", 0)
        num_valid: int = row_stats.get("total_valid", 0)
        num_invalid: int = row_stats.get("total_invalid", 0)
        num_pending: int  = row_stats.get("total_non_processing", 0)
        
        # Comprobar resultados
        if num_total != (num_valid + num_invalid + num_pending):
            print(row_stats)
            raise "Fallo la comprobación de la importación de datos."
        return {
            "process_id": process_id,
            "num_total" : num_total,
            "num_valid" : num_valid,
            "num_invalid" : num_invalid,
            "num_pending" : num_pending
        }
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()

def find_all_imports(id: str, filter_statuses: str | None = None) -> list[dict]:
    """
    Devuelve todos los registros históricos de importación
    """
    
    values: str = ", ".join(["(?, ?)"] * len(config.STATUS_CODES))
    params: tuple = ()
    
    for code, text in config.STATUS_CODES.items():
        params += (code, text)
    params += (id,)
        
    where_status: str = ""
    statuses: tuple[str, ...] = utils.statuses(filter_statuses)
    placeholders: str = ", ".join(["?"] * len(statuses))
    where_status = f" AND pi.status IN ({placeholders})"
    params += statuses
    
    sql: str = f"""
    WITH status_codes(code, description) AS (
        VALUES {values}
    )
    SELECT pi.line,
        pi.process_id,
        pi.filename,
        pi.username,
        pi.name,
        pi.normalized_name,
        pi.description,
        pi.category,
        pi.normalized_category,
        pi.quantity,
        pi.currency,
        pi.price,
        pi.status,
        sc.description AS status_description,
        pi.create_at
    FROM product_imports AS pi
        LEFT JOIN status_codes AS sc 
            ON pi.status = sc.code
    WHERE pi.process_id = ?{where_status}
    ORDER BY pi.line
    """
    return database.find_all(sql, params)

def find_all_import_processes() -> list[dict[str, str]]:
    """
    Devolver lista de procesos ejecutados
    """
    return database.find_all("SELECT process_id, min(create_at) AS create_at FROM product_imports GROUP BY process_id ORDER BY create_at DESC, process_id")