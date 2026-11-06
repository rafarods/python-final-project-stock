# Manejo de Inventario

https://img.shields.io/badge/License-GPLv3-blue.svg](https://www.gnu.org/licenses/gpl-3.0)

Sistema de gestión de inventario desarrollado en **Python**, utilizando **SQLite 3** como base de datos y **Tkinter** para la interfaz gráfica.

El proyecto surge como entrega final de un curso de Python. Parte de los requerimientos establecidos en la consigna y los amplía mediante una implementación más completa, incorporando autenticación de usuarios, roles, categorías normalizadas, validaciones e importación de productos desde archivos CSV.

> **Estado:** proyecto actualmente en desarrollo.

---

## Información del proyecto

| Propiedad | Valor |
|---|---|
| Aplicación | Manejo de Inventario |
| Versión | 1.0 |
| Lenguaje | Python 3.10+ |
| Base de datos | SQLite 3 |
| Interfaz gráfica | Tkinter |
| Autor | Rafael Rodríguez |
| Email | rafarods@outlook.com |
| Licencia | GNU GPL v3 |

---

## Requisitos

Para ejecutar la aplicación se requiere:

- **Python 3.10 o superior**.
- **SQLite 3**, utilizado mediante el módulo `sqlite3` incluido con Python.
- **Tkinter** para la interfaz gráfica.

La aplicación utiliza una base de datos SQLite almacenada localmente, por lo que no requiere configurar un servidor de base de datos independiente.

---

## Ejecución

Desde el directorio raíz del proyecto:

```bash
python main.py
```

El archivo `main.py` constituye el punto de entrada de la aplicación.

Dependiendo del sistema operativo y de la configuración de Python, también puede utilizarse:

```bash
python3 main.py
```

---

## Objetivo

El objetivo del proyecto es desarrollar una aplicación para administrar el inventario de productos mediante una interfaz gráfica.

El sistema contempla:

- Registro de productos.
- Visualización de productos.
- Actualización de productos.
- Eliminación de productos.
- Búsqueda de productos.
- Gestión de categorías.
- Control de existencias.
- Gestión de precios.
- Reportes de inventario.
- Autenticación de usuarios.
- Control de acceso mediante roles.
- Importación de productos desde archivos CSV.
- Validación de datos importados.

---

# Consigna original

La consigna académica establece desarrollar una aplicación de inventario utilizando Python y SQLite.

## Base de datos

El modelo básico solicitado contempla productos con los siguientes datos:

- Identificador.
- Nombre.
- Descripción.
- Cantidad.
- Precio.
- Categoría.

## Gestión de productos

La aplicación debe permitir:

- Registrar nuevos productos.
- Visualizar los productos registrados.
- Actualizar productos mediante su ID.
- Eliminar productos mediante su ID.
- Buscar productos mediante su ID.
- Opcionalmente, buscar por nombre o categoría.
- Generar un reporte de productos cuya cantidad sea igual o inferior a un límite especificado por el usuario.

## Interfaz

La consigna establece como requisito básico una interfaz mediante terminal.

Este proyecto amplía dicho requisito mediante una **interfaz gráfica desarrollada con Tkinter**.

## Estructura del código

La aplicación mantiene una estructura modular, separando las diferentes responsabilidades de la lógica del programa, acceso a datos e interfaz de usuario.

---

# Implementación ampliada

Además de los requisitos básicos de la consigna, el proyecto incorpora mejoras adicionales:

- Interfaz gráfica con Tkinter.
- Autenticación de usuarios.
- Roles de usuario.
- Gestión independiente de categorías.
- Normalización de nombres.
- Prevención de productos duplicados por categoría.
- Configuración centralizada.
- Validación de cantidades.
- Validación de precios.
- Moneda configurable.
- Importación desde archivos CSV.
- Validación previa de registros importados.
- Tabla de staging para importaciones.
- Estados de procesamiento y error.
- Registro histórico del usuario que realizó una importación.

Estas extensiones permiten desarrollar los requisitos de la consigna dentro de una aplicación de inventario más completa.

---

# Configuración

Los parámetros generales de la aplicación se encuentran centralizados en:

```text
config.py
```

## Base de datos

La ubicación del archivo SQLite se determina mediante:

```python
DB_PATH: pathlib.Path = pathlib.Path(__file__).resolve().parent / "stock.db"
```

Por lo tanto, la aplicación utiliza:

```text
stock.db
```

como base de datos local.

---

## Aplicación

```python
APP_NAME: str = "Manejo de Inventario"
APP_VERSION: str = "1.0"
```

---

## Autor

```python
AUTHOR: dict[str, str] = {
    "name": "Rafael Rodríguez",
    "email": "rafarods@outlook.com"
}
```

---

## Roles

La aplicación define actualmente dos roles:

```python
ROLE_USER: str = "ROLE_USER"
ROLE_ADMIN: str = "ROLE_ADMIN"
```

### `ROLE_USER`

Representa un usuario estándar de la aplicación.

### `ROLE_ADMIN`

Representa un usuario con privilegios administrativos.

La aplicación es responsable de determinar las operaciones permitidas para cada rol.

---

## Usuario administrador inicial

La configuración incluye un usuario administrativo inicial:

```python
ADMIN: dict[str, str] = {
    "username": "demo",
    "password": "demo"
}
```

> **Importante:** estas credenciales están destinadas al desarrollo y demostración de la aplicación.

---

## Moneda

La moneda predeterminada de la aplicación es:

```python
CURRENCY: str = "ARS"
```

Los productos pueden utilizar este valor desde la aplicación cuando corresponda asignar la moneda predeterminada.

---

## Límites de precios

```python
MIN_PRICE: float = 0.01
MAX_PRICE: float = 999_999_999.99
```

Por lo tanto:

```text
0.01 <= price <= 999999999.99
```

---

## Límites de cantidades

```python
MIN_QUANTITY: int = 0
MAX_QUANTITY: int = 999_999_999
```

Por lo tanto:

```text
0 <= quantity <= 999999999
```

Los límites, valores predeterminados y demás reglas de negocio son administrados por la aplicación y no mediante valores `DEFAULT` o restricciones `CHECK` de SQLite.

---

# Base de datos

El modelo de datos utiliza cuatro tablas:

- `categories`
- `products`
- `users`
- `product_imports`

La principal relación del modelo es:

```text
categories (1) ──────────────< (N) products
```

Una categoría puede contener múltiples productos y cada producto pertenece a una única categoría.

---

# Tabla `categories`

Almacena las categorías utilizadas para clasificar los productos.

```sql
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE,
    UNIQUE (name)
);
```

## Columnas

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Identificador único de la categoría. |
| `name` | TEXT | NOT NULL, UNIQUE | Nombre visible de la categoría. |
| `normalized_name` | TEXT | NOT NULL, UNIQUE | Nombre normalizado utilizado para búsquedas y control de duplicados. |

## Normalización

`normalized_name` contiene una representación normalizada del nombre de la categoría.

Por ejemplo:

```text
"Lácteos" -> "lacteos"
"LACTEOS" -> "lacteos"
"Lacteos" -> "lacteos"
```

Esto permite comparar categorías independientemente de diferencias como mayúsculas, minúsculas o acentos.

La restricción:

```sql
UNIQUE (normalized_name)
```

impide registrar categorías equivalentes después de aplicar la normalización.

---

# Tabla `products`

Almacena los productos registrados en el inventario.

```sql
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    currency TEXT NOT NULL,
    price FLOAT NOT NULL,
    UNIQUE (category_id, normalized_name),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);
```

## Columnas

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Identificador único del producto. |
| `category_id` | INTEGER | NOT NULL, FOREIGN KEY | Categoría a la que pertenece el producto. |
| `name` | TEXT | NOT NULL | Nombre visible del producto. |
| `normalized_name` | TEXT | NOT NULL | Nombre normalizado para búsquedas y control de duplicados. |
| `description` | TEXT | NOT NULL | Descripción del producto. |
| `quantity` | INTEGER | NOT NULL | Cantidad disponible. |
| `currency` | TEXT | NOT NULL | Moneda utilizada para expresar el precio. |
| `price` | FLOAT | NOT NULL | Precio unitario del producto. |

---

## Relación con categorías

La relación se establece mediante:

```sql
FOREIGN KEY (category_id) REFERENCES categories (id)
```

Conceptualmente:

```text
categories.id
      │
      │ 1:N
      ▼
products.category_id
```

Esto permite administrar las categorías de forma independiente y evita almacenar repetidamente el nombre de la categoría en cada producto.

### Ejemplo

```text
categories

id | name
---|---------
1  | Lácteos
2  | Frescos


products

id | category_id | name
---|-------------|--------------------
1  | 1           | Leche 1L
2  | 1           | Yogur
3  | 2           | Carne Vacuna 1 kg
```

En este ejemplo:

- `Leche 1L` pertenece a `Lácteos`.
- `Yogur` pertenece a `Lácteos`.
- `Carne Vacuna 1 kg` pertenece a `Frescos`.

---

## Unicidad de productos

La restricción:

```sql
UNIQUE (category_id, normalized_name)
```

establece que un producto normalizado debe ser único dentro de una categoría.

Por ejemplo:

```text
category_id | normalized_name
------------|----------------
1           | premium
2           | premium
```

es válido porque pertenecen a categorías diferentes.

En cambio:

```text
category_id | normalized_name
------------|----------------
1           | premium
1           | premium
```

no es válido.

Por tanto, la combinación:

```text
category_id + normalized_name
```

determina la unicidad lógica del producto dentro de cada categoría.

---

# Tabla `users`

Almacena los usuarios registrados en la aplicación.

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
```

## Columnas

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Identificador único del usuario. |
| `username` | TEXT | NOT NULL, UNIQUE | Nombre utilizado para iniciar sesión. |
| `password` | TEXT | NOT NULL | Contraseña del usuario. |
| `role` | TEXT | NOT NULL | Rol asignado al usuario. |

Los roles disponibles actualmente son:

```text
ROLE_USER
ROLE_ADMIN
```

---

# Tabla `product_imports`

`product_imports` funciona como una tabla de **staging** para almacenar los registros provenientes de archivos CSV antes de incorporarlos definitivamente al inventario.

```sql
CREATE TABLE IF NOT EXISTS product_imports (
    id INTEGER PRIMARY KEY,
    process_id TEXT NOT NULL,
    username TEXT NOT NULL,
    filename TEXT,
    category TEXT,
    normalized_category TEXT,
    name TEXT,
    normalized_name TEXT,
    description TEXT,
    quantity TEXT,
    currency TEXT,
    price TEXT,
    status TEXT NOT NULL
);
```

## Columnas

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Identificador interno del registro importado. |
| `process_id` | TEXT | NOT NULL | Identifica el proceso de importación al que pertenece el registro. |
| `username` | TEXT | NOT NULL | Usuario que realizó la importación. |
| `filename` | TEXT |  | Nombre del archivo importado. |
| `category` | TEXT |  | Categoría recibida desde el archivo. |
| `normalized_category` | TEXT |  | Categoría normalizada. |
| `name` | TEXT |  | Nombre del producto recibido. |
| `normalized_name` | TEXT |  | Nombre normalizado del producto. |
| `description` | TEXT |  | Descripción recibida. |
| `quantity` | TEXT |  | Cantidad original antes de su validación. |
| `currency` | TEXT |  | Moneda recibida. |
| `price` | TEXT |  | Precio original antes de su validación. |
| `status` | TEXT | NOT NULL | Estado de procesamiento o error del registro. |

---

## `process_id`

`process_id` permite agrupar todos los registros pertenecientes a una misma carga.

Ejemplo:

```text
process_id | username | filename
-----------|----------|--------------
ABC123     | demo     | productos.csv
ABC123     | demo     | productos.csv
ABC123     | demo     | productos.csv
XYZ456     | demo     | precios.csv
```

Los tres primeros registros corresponden al mismo proceso de importación.

Esto permite realizar consultas como:

```sql
SELECT *
FROM product_imports
WHERE process_id = ?;
```

---

## `username`

`username` conserva históricamente el usuario que realizó la importación.

Deliberadamente no existe:

```sql
FOREIGN KEY (username) REFERENCES users (username)
```

Por tanto:

```text
product_imports.username
```

no constituye una referencia formal hacia:

```text
users.username
```

Esta decisión permite conservar la información histórica del usuario asociado con una importación independientemente de posteriores modificaciones realizadas sobre la tabla `users`.

---

## Datos importados como texto

Los campos:

```text
quantity
price
```

se almacenan inicialmente como `TEXT`.

Esto permite conservar el dato recibido antes de comprobar si puede convertirse correctamente.

Por ejemplo:

```text
quantity = "100"
quantity = "ABC"

price = "2500.90"
price = "incorrecto"
```

Después de la validación, los valores aceptados pueden convertirse a los tipos definitivos utilizados por `products`:

```text
product_imports.quantity TEXT  -> products.quantity INTEGER
product_imports.price    TEXT  -> products.price    FLOAT
```

---

# Estados de importación

Los códigos utilizados para identificar el estado de cada registro importado se encuentran centralizados en `config.py`.

| Código | Descripción |
|---|---|
| `SP0` | Sin procesar |
| `PR0` | Procesado |
| `ER1` | Faltan datos requeridos |
| `ER2` | Precio inválido |
| `ER3` | Cantidad inválida |
| `ER4` | Precio menor que el mínimo permitido |
| `ER5` | Precio mayor que el máximo permitido |
| `ER6` | Cantidad menor que el mínimo permitido |
| `ER7` | Cantidad mayor que el máximo permitido |

La configuración correspondiente es:

```python
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
}
```

---

# Flujo de importación

El proceso general de importación contempla las siguientes etapas:

```text
Archivo CSV
     │
     ▼
product_imports
     │
     ├── Validación de campos requeridos
     ├── Normalización de categoría
     ├── Normalización del producto
     ├── Validación de cantidad
     ├── Validación de precio
     └── Asignación de estado
     │
     ▼
Registro válido
     │
     ├── categories
     └── products
```

`product_imports` actúa como una capa intermedia entre los datos externos y las tablas definitivas del inventario.

Esto permite validar los registros antes de incorporarlos a `categories` y `products`.

---

# Datos de ejemplo

La aplicación contiene productos iniciales definidos mediante `SAMPLE_DATA`.

```python
SAMPLE_DATA: tuple[dict[str, str | int | float], ...] = (
    {
        "name": "Leche 1L",
        "description": "Leche de cartón",
        "quantity": 12,
        "currency": CURRENCY,
        "price": 2500.90,
        "category": "Lácteos"
    },
    {
        "name": "Carne Vacuna 1 kg",
        "description": "Carne Vacuna Novillo",
        "quantity": 100,
        "currency": CURRENCY,
        "price": 160000.23,
        "category": "Frescos"
    },
)
```

La moneda utiliza la constante:

```python
CURRENCY
```

en lugar de repetir directamente el valor `"ARS"` en cada registro.

---

# Modelo de datos

El modelo puede resumirse de la siguiente manera:

```text
categories
├── id
├── name
└── normalized_name
      │
      │ 1:N
      ▼
products
├── id
├── category_id
├── name
├── normalized_name
├── description
├── quantity
├── currency
└── price


users
├── id
├── username
├── password
└── role


product_imports
├── id
├── process_id
├── username
├── filename
├── category
├── normalized_category
├── name
├── normalized_name
├── description
├── quantity
├── currency
├── price
└── status
```

## Relaciones formales

| Tabla origen | Columna | Tabla destino | Columna | Relación |
|---|---|---|---|---|
| `products` | `category_id` | `categories` | `id` | N:1 |

La única relación formal mediante clave foránea en el modelo actual es:

```text
products.category_id -> categories.id
```

`product_imports.username` no constituye una clave foránea porque su finalidad es conservar información histórica.

---

# Separación de responsabilidades

El proyecto separa las responsabilidades correspondientes a SQLite y a la aplicación Python.

## SQLite

La base de datos garantiza principalmente las restricciones estructurales y de integridad:

```text
PRIMARY KEY
FOREIGN KEY
NOT NULL
UNIQUE
```

## Aplicación

La aplicación gestiona las reglas de negocio:

- Valores predeterminados.
- Normalización de nombres.
- Validación de cantidades.
- Validación de precios.
- Moneda predeterminada.
- Autenticación.
- Roles.
- Gestión del inventario.
- Gestión de categorías.
- Importaciones CSV.
- Estados de procesamiento.
- Interfaz gráfica.

Esta separación permite mantener el esquema SQLite enfocado en la integridad de los datos y administrar las reglas específicas del negocio desde Python.

---

# Diferencias respecto de la consigna

La consigna original propone una implementación mínima basada conceptualmente en:

```text
inventario.db
└── productos
```

La implementación de este proyecto utiliza un modelo ampliado:

```text
stock.db
├── categories
├── products
├── users
└── product_imports
```

## Categorías

En lugar de almacenar el nombre de la categoría directamente dentro del producto, se utiliza una relación:

```text
products.category_id -> categories.id
```

Esto permite gestionar las categorías independientemente de los productos.

## Interfaz gráfica

La consigna requiere una interfaz básica mediante terminal.

La implementación amplía este requisito mediante una interfaz gráfica utilizando **Tkinter**.

## Usuarios

Se incorpora autenticación y control de acceso mediante:

```text
ROLE_USER
ROLE_ADMIN
```

## Importación

Se incorpora un mecanismo para la carga y validación de productos mediante archivos CSV.

---

# Cumplimiento de la consigna

El proyecto busca cumplir los requisitos obligatorios y complementarlos con funcionalidades adicionales.

| Requerimiento | Implementación |
|---|---|
| Python | Python 3.10+ |
| Base de datos SQLite | `stock.db` |
| Productos | `products` |
| Identificador | `products.id` |
| Nombre | `products.name` |
| Descripción | `products.description` |
| Cantidad | `products.quantity` |
| Precio | `products.price` |
| Categoría | Relación con `categories` |
| Registrar productos | Gestión de productos |
| Visualizar productos | Gestión de productos |
| Actualizar productos | Gestión de productos |
| Eliminar productos | Gestión de productos |
| Buscar productos | Gestión de productos |
| Reportes de existencias | Contemplado por la aplicación |
| Interfaz | Tkinter |
| Código modular | Separación de responsabilidades |

> La documentación de reportes, consultas y funcionalidades adicionales será incorporada a medida que estos componentes sean finalizados y estabilizados.

---

# Mejoras adicionales

Respecto de los requerimientos mínimos de la consigna, el proyecto incorpora:

1. **Tkinter** para proporcionar una interfaz gráfica.
2. **Modelo relacional** para separar productos y categorías.
3. **Normalización de nombres** para mejorar búsquedas y prevenir duplicados.
4. **Usuarios y roles** para controlar el acceso.
5. **Validaciones** para precios y cantidades.
6. **Configuración centralizada** mediante `config.py`.
7. **Importación CSV** para cargas masivas de productos.
8. **Staging de importaciones** para validar los datos antes de modificar el inventario.
9. **Códigos de estado** para identificar el resultado de cada registro importado.
10. **Trazabilidad** mediante el registro del usuario y proceso asociados a cada importación.

---

# Estado del proyecto

El proyecto se encuentra actualmente **en desarrollo**.

La estructura de la base de datos y la configuración general ya forman parte del diseño de la aplicación.

Las funcionalidades, reportes, consultas, pantallas y documentación podrán continuar evolucionando durante el desarrollo del proyecto.

---

# Autor

**Rafael Rodríguez**

Email: `rafarods@outlook.com`

---

# Licencia

Este proyecto se distribuye bajo la **GNU General Public License v3.0 (GPL-3.0)**.

La licencia permite utilizar, estudiar, modificar y redistribuir el software bajo los términos establecidos por la GNU GPL v3.

El texto completo de la licencia debe encontrarse en el archivo:

```text
LICENSE
```

ubicado en la raíz del repositorio.

Copyright © 2026 Rafael Rodríguez.

Más información:

https://www.gnu.org/licenses/gpl-3.0.html
