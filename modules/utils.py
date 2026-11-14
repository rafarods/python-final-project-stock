import tkinter
import unicodedata
import typing
import csv
import uuid
import config
import datetime
import pathlib
import modules.dao.product_dao as product_dao

def file_name(path: str | None) -> str:
    """
    Devuelve el nombre del archivo
    """
    if not path:
        return ""
    return pathlib.Path(path).name

def currency(index: int = 0) -> str:
    return config.CURRENCIES[index]

def now() -> str:
    """
    Devuelve la fecha y hora actual en formato ISO: yyyy-MM-dd HH:mm:ss
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_datetime(value: str | None, lang: typing.Literal["es", "en"] = config.LANG) -> str:
    if not value:
        return ""
    try:
        match lang:
            case "es":
                return datetime.datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M:%S")
            case _:
                return datetime.datetime.fromisoformat(value).strftime("%m/%d/%Y %H:%M:%S")
    except ValueError:
        return value

def format_quantity(quantity: int, lang: typing.Literal["es", "en"] = config.LANG) -> str:
    """
    Devuelve la cantidad en formato EN o ES:
    format_quantity(1250000)       => 1,250,000
    format_quantity(1250000, "es") => 1.250.000
    format_quantity(1250000, "en") => 1,250,000
    """
    value: str = f"{quantity:,}"
    match lang:
        case "es":
            return value.replace(",", ".")
        case _:
            return value

def format_price(price: float, lang: typing.Literal["es", "en"] = config.LANG) -> str:
    """
    Devuelve el precio en formato EN o ES:
    format_price(1250000.75)       => 1,250,000.75
    format_price(1250000.75, "es") => 1.250.000,75
    format_price(1250000.75, "en") => 1,250,000.75
    """
    value: str = f"{price:,.2f}"
    match lang:
        case "es":
            return value.replace(",", "_").replace(".", ",").replace("_", ".")
        case _:
            return value

"""
Centrar un ventana de la UI
"""
def center_window(window: tkinter.Tk, width: int, height: int) -> None:
    screen_width: int = window.winfo_screenwidth()
    screen_height: int = window.winfo_screenheight()
    x: int = (screen_width - width) // 2
    y: int = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def normalize_text(text: str | None) -> str:
    """
    Normalizar texto para comparaciones 
    """
    if text is None or text.strip() == "":
        return ""
    normalized: str = unicodedata.normalize("NFD", text)
    result: str = ""
    for char in normalized:
        if not unicodedata.combining(char):
            result += char
    return result.casefold().strip()

def normalize_column(key: str) -> str:
    """
    Devuelve una columna normaliza y permite utilizar o mapear los posibles nombres
    """
    key = normalize_text(key)
    for column, aliases in config.COLUMN_MAP.items():
        if key == column or key in aliases:
            return column
    return key

def stock_from_csv(filename: str) -> tuple[dict[str, str | None], ...]:
    """
    Lee productos desde un archivo CSV.
    """
    data: list[dict[str, str | None]] = []
    with open(filename, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for line, row in enumerate(reader, start=1):
            norma_row: dict[str, str | None] = {}
            for key, value in row.items():
                norma_row[normalize_column(key)] = value
            data.append({
                "name": norma_row.get("name") or "",
                "quantity": norma_row.get("quantity") or "",
                "currency": norma_row.get("currency") or currency(),
                "price": norma_row.get("price") or "",
                "category": norma_row.get("category") or "",
                "description" : norma_row.get("description") or "",
                "line" : line,
            })
    return tuple(data)


def normalize_number(value: str) -> str:
    """
    Normalizar número de entrada
    """
    value = value.strip().replace(" ", "")
    has_comma = "," in value
    has_dot = "." in value
    match has_comma, has_dot:
        # Ejemplo 1) Formatos: 1,250,000.75 / 1.250.000,75
        case True, True:
            if value.rfind(",") > value.rfind("."):
                value = value.replace(".", "").replace(",", ".")
            else:
                value = value.replace(",", "")
        # Ejemplo 2) Formatos: 1,250,000 / 1250000,75
        case True, False:
            if value.count(",") > 1:
                value = value.replace(",", "")
            else:
                left, right = value.rsplit(",", 1)
                if len(right) == 3:
                    value = value.replace(",", "")
                else:
                    value = left + "." + right
        # Ejemplo 3) Formatos: 1.250.000 / 1250000.75
        case False, True:
            if value.count(".") > 1:
                value = value.replace(".", "")
            else:
                left, right = value.rsplit(".", 1)
                if len(right) == 3:
                    value = value.replace(".", "")
        # Ejemplo 4) Formato: 1250000
        case False, False:
            pass
    return value

def to_quantity(value: str) -> int:
    number = normalize_number(value)
    return int(float(number))

def to_price(value: str) -> float:
    return float(normalize_number(value))

def is_quantity(value: str) -> bool:
    try:
        return isinstance(to_quantity(value), int)
    except ValueError:
        return False

def is_price(value: str) -> bool:
    try:
        return isinstance(to_price(value), float)
    except ValueError:
        return False
    
def import_stock_csv(username: str, filename: str, auto_create: bool = False) -> dict[str, str | int | None] | None:
    """
    Procesar los datos de productos
    """
    data: tuple[dict[str, str | None]] = stock_from_csv(filename)
    if not data:
        return None
    process_id: str = str(uuid.uuid4()) 
    params: list[tuple] = []
    for row in data:
        status: str = "SP0"
        price_text: str = row.get("price")
        quantity_text: str = row.get("quantity")
        nomalized_name = normalize_text(row.get("name"))
        currency = row.get("currency")
        category = row.get("category")
        normalized_category = normalize_text(row.get("category"))
        """
        Valores desde config
        ER1: Faltan datos requeridos
        ER2: Precio es inválida
        ER3: Cantidad es inválida
        ER4: Precio es menor que MIN_PRICE
        ER5: Precio es mayor que MAX_PRICE
        ER6: Cantidad es menor que MIN_QUANTITY
        ER7: Cantidad es mayor que MAX_QUANTITY
        ER8: Producto no encontrado
        """
        price: float = None
        quantity: int = None
        if not nomalized_name or (auto_create and not normalized_category):
            status = "ER1"
        elif not is_price(price_text):
            status = "ER2"
        elif not is_quantity(quantity_text):
            status = "ER3"
        elif currency not in (config.CURRENCIES):
            status = "ER9"
        else:
            price = to_price(price_text)
            quantity = to_quantity(quantity_text)
            if price < config.MIN_PRICE:
                status = "ER4"
            elif price > config.MAX_PRICE:
                status = "ER5"
            elif quantity < config.MIN_QUANTITY:
                status = "ER6"
            elif quantity > config.MAX_QUANTITY:
                status = "ER7"
        params.append((
            process_id,
            filename,
            username,
            row.get("name"),
            nomalized_name,
            category,
            normalized_category,
            quantity_text,
            currency,
            price_text,
            status,
            now(),
            row.get("line"),
            row.get("description"),
            price,
            quantity,
        ))
    return product_dao.save_import(process_id, params, auto_create)

def export_stock_csv(filename: str, lang: typing.Literal["es", "en"] = config.LANG, delimiter: str = ",") -> int:
    """
    Exporta productos en formato CSV.
    """
    fields: tuple[str, ...] = ("id", "name", "description", "category", "currency", "price", "quantity" )
    header: tuple[str, ...] = ("ID", "Producto", "Descripción", "Categoría", "Moneda", "Precio", "Cantidad")
    rows: list[dict] = product_dao.find_all()
    for row in rows:
        row["price"] = format_price(row["price"], lang)
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore", delimiter=delimiter)
        # zip para combinar tuplas en dict columna : título
        writer.writerow(dict(zip(fields, header)))
        writer.writerows(rows)
    return len(rows)

def is_allow_access(role: str, resource: str) -> bool:
    """
    Indica si el rol (ROLE_USER o ROLE_ADMIN) posee acceso al recurso. 
    """
    if role == config.ROLE_ADMIN:
        return True
    if role != config.ROLE_USER:
        return False
    return resource.lower().strip() in config.ROLE_USER_RESOURCES

def get_state_allow_access(role: str, resource: str) -> str:
    if is_allow_access(role, resource):
        return "active"
    return "disabled"

def statuses(prefix: str | None = None) -> tuple[str, ...]:
    if prefix is None:
        return tuple(config.STATUS_CODES.keys())
    statuses_list: tuple[str, ...] = ()
    for status in config.STATUS_CODES:
        if status.startswith(prefix):
            statuses_list += (status,)
    return statuses_list