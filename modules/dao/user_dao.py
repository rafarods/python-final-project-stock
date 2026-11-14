import config
import modules.database as database
import modules.crypt as crypt
import modules.utils as utils

def find_one(username: str) -> dict[str, str] | None:
    """
    Buscar un usuario
    """
    return database.find_one("SELECT * FROM users WHERE username = ?", (utils.normalize_text(username),))

def find_all() -> dict | None:
    """
    Buscar todos los usuario
    """
    return database.find_all("SELECT * FROM users ORDER BY username")

def exist(username: str) -> bool:
    """
    Indica si el usuario existe
    """
    return find_one(username) is not None

def insert(username: str, password: str, role: str, can_change_password: bool = True) -> int | None:
    """
    Crear un usuario
    """
    if not username or not password or exist(username):
        return None
    normalize_username = utils.normalize_text(username)
    password_hash = crypt.hash_password(password)
    return database.insert("INSERT INTO users (username, password, role, can_change_password) VALUES (?, ?, ?, ?)", (normalize_username, password_hash, role, can_change_password))

def delete(username: str) -> int:
    """
    Eliminar un registro y devuelve la cantidad eliminada
    """
    return database.delete("DELETE FROM users WHERE username = ?", (username,))

def update(username: str, params: dict[str, str | bool]) -> int | None:
    """
    Actualiza usuarios y devuelve la cantidad de filas actualizadas
    """
    if not params:
        return None
    fields: str = ""
    values: list = []
    for key in params:
        if fields:
            fields += ", "
        fields += f"{key} = ?"
        match key:
            case "can_change_password":
                values.append(params.get(key))
            case "password":
                values.append(crypt.hash_password(params.get(key)))
            case "role":
                match (params.get(key).strip().upper()):
                    case config.ROLE_ADMIN:
                        values.append(config.ROLE_ADMIN)
                    case _:
                        values.append(config.ROLE_USER)
    values += (username,)
    return database.update(f"UPDATE users SET {fields} WHERE username = ?", values)

def check_password(username: str, password: str) -> bool:
    """
    Comprueba la contraseña del usuario
    """
    user: dict = find_one(username)
    if user is None:
        return False
    return crypt.check_password(password, user["password"])

def change_password(username: str, new_password: str) -> bool:
    """
    Cambia la contraseña del usuario
    """
    return update(username, {"password": new_password}) == 1

def auth_user(username: str) -> dict | None:
    """
    Devuelve el usuario en sesión (sin contraseña)
    """
    user: dict = find_one(username)
    if user is not None:
        user.pop("password")
    return user