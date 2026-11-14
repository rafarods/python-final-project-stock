import pathlib
import logging

# Nivel de log: DEBUG, INFO, ERROR, etc.
LOG_LEVEL: int = logging.INFO

# Nombre de la DB
DB_NAME: str = "stock.db"

# Ruta la DB de SQLite usando este directorio
DB_PATH: pathlib.Path = pathlib.Path(__file__).resolve().parent / DB_NAME

# Nombre de la aplicación
APP_NAME: str = "Manejo de Inventario"

# Versión de la aplicación
APP_VERSION: str = "1.0"

# Autor o desarrollador
AUTHOR: dict[str, str] = {"name": "Rafael Rodríguez", "email": "rafarods@outlook.com"}

# Idioma por defecto
LANG: str = "es"

# Roles
ROLE_USER: str = "ROLE_USER"
ROLE_ADMIN: str = "ROLE_ADMIN"

# Acceso a los recursos del menú (sólo ROLE_USER)
ROLE_USER_RESOURCES: tuple[str, ...] = (
    # menú de producto
    "menu_stock", "add_product", "edit_product", "search_product", "delete_product", "import_list", "import_stock", "export_stock", "list_product",
    # menú de categoria
    "menu_category", "add_category", "edit_category", "delete_category", "search_category", "list_category",
    # menú de aplicación
    "menu_application", "exit", "logout", "change_password",
    # menú usuarios
    #"menu_users", "create_user", "edit_user", "delete_user", "list_users",
)

# Superusuario
ADMIN: dict[str, str] = {"username": "demo", "password": "demo"}

# Validaciones
PASSWD_MIN_LEN: int = 4 
CURRENCIES: tuple[str, ...] = ("ARS", "USD")
MIN_PRICE: float = 0.01
MAX_PRICE: float = 999_999_999
MIN_QUANTITY: int = 0
MAX_QUANTITY: int = 999_999_999

COLUMN_MAP: dict[str, tuple[str, ...]] = {
    "name": ("nombre","producto",),
    "description": ("descripcion",),
    "quantity": ("cantidad",),
    "currency": ("moneda",),
    "price": ("precio",),
    "category": ("categoria",), 
}

# Código de error al cargar un archivo CSV
STATUS_CODES: dict[str, str] = {
    "SP0": "Sin procesar",
    "PR0": "Procesado",
    "ER1": "Faltan datos requeridos",
    "ER2": "Precio inválido",
    "ER3": "Cantidad inválida",
    "ER4": f"Precio es menor que {MIN_PRICE}",
    "ER5": f"Precio es mayor que {MAX_PRICE}",
    "ER6": f"Cantidad es menor que {MIN_QUANTITY}",
    "ER7": f"Cantidad es mayor que {MAX_QUANTITY}",
    "ER8": "Nombre del producto no encontrado",
    "ER9": f"Sólo se permiten monedas: {", ".join(CURRENCIES)}",
    "ER10": "Nombre de la categoria no encontrada",
}

TEXT_FOOTER: str = f"{AUTHOR["name"]} «{AUTHOR["email"]}» | Iniciación a la Programación con Python 2026"