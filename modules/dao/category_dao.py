import modules.database as database
import modules.utils as utils

def insert(name: str) -> int | None:
    """
    Crea una categoría
    """
    return database.insert("INSERT INTO categories (name, normalized_name) VALUES (?, ?)", (name, utils.normalize_text(name)))

def delete(name: str) -> int | None:
    """
    Elimina una categoría
    """
    return database.delete("DELETE FROM categories WHERE normalized_name = ?", (utils.normalize_text(name),))

def update(old_name: str, new_name: str) -> int | None:
    """
    Actualizar el nombre una categoría
    """
    return database.update("""
    UPDATE categories SET name = ?, normalized_name = ? WHERE normalized_name = ?
    """, (new_name, utils.normalize_text(new_name), utils.normalize_text(old_name),))

def find_all() -> list[dict]:
    """
    Devuelve todas las categorías
    """
    return database.find_all("""
    SELECT c.id, c.name, count(p.category_id) AS total_products 
    FROM categories AS c 
        LEFT JOIN products AS p
            ON c.id = p.category_id
    GROUP BY c.id, c.name
    ORDER BY c.normalized_name
    """)

def find_one(name: str) -> dict | None:
    """
    Devuelve una categoría por nombre
    """
    return database.find_one("SELECT id, name FROM categories WHERE normalized_name = ?", (utils.normalize_text(name),))

def exist(name: str) -> bool:
    """
    Comprueba si existe el nombre de una categoría
    """
    return find_one(name) is not None

def has_products(name: str) -> bool:
    """
    Comprueba si existe el nombre de una categoría
    """
    row: dict = database.find_one("""
    SELECT count(p.id) AS total
    FROM products AS p
        JOIN categories AS c
            ON p.category_id = c.id
    WHERE c.normalized_name = ?
    """, (utils.normalize_text(name),))
    return row is not None and row.get("total", 0) >= 1