# Código Femenino - Backend API (Flask + MySQL)

Backend RESTful modular desarrollado en Python con **Flask** y **MySQL 8.0**, diseñado específicamente para dar soporte a la revista digital **Código Femenino** según sus especificaciones editoriales y de negocio.

---

## 🚀 Arquitectura Modular

El proyecto implementa una arquitectura por capas desacoplada:

```
codigo-femenino-backend/
├── app.py                      # Punto de entrada y configuración de la app Flask
├── openapi.yaml                # Especificación OpenAPI 3.0 completa de la API
├── requirements.txt            # Dependencias del proyecto
├── .env.example                # Plantilla de variables de entorno
├── scripts/
│   └── init_db.sql             # Script DDL y datos semilla para MySQL 8.0
└── src/
    ├── config.py               # Carga y validación de variables de entorno
    ├── db.py                   # Pool de conexiones con DBUtils y PyMySQL
    ├── repositories/           # Capa de acceso a datos (consultas SQL)
    │   ├── category_repository.py
    │   ├── article_repository.py
    │   └── lead_repository.py
    ├── services/               # Lógica de negocio y orquestación
    │   ├── category_service.py
    │   ├── article_service.py
    │   └── lead_service.py
    ├── utils/                  # Utilidades compartidas y HATEOAS
    │   └── hateoas.py          # Generador de enlaces hypermedia de navegación
    ├── validators/             # Validación y sanitización de datos de entrada
    │   ├── common.py
    │   ├── article_validators.py
    │   └── lead_validators.py
    └── routes/                 # Controladores y endpoints REST
        ├── docs.py             # Swagger UI interactivo (/docs y /docs/openapi.yaml)
        ├── health.py           # Estado de la API y de la conexión a MySQL
        ├── categories.py       # Endpoints de categorías
        ├── articles.py         # Endpoints de artículos, secciones y búsqueda
        └── leads.py            # Captación de newsletter y descarga de guía gratuita
```

---

## 📖 Documentación Interactiva (Swagger / OpenAPI)

El backend incluye interfaz visual de Swagger UI y especificación estándar OpenAPI 3.0:

- **Swagger UI interactivo:** `http://localhost:5000/docs` (permite probar todos los endpoints y schemas en vivo).
- **Especificación OpenAPI 3.0 (YAML):** `http://localhost:5000/docs/openapi.yaml` (o directo en la raíz `openapi.yaml`, compatible para importar en Postman, Insomnia o Swagger Editor).

---

## 🛠️ Requisitos Previos

- **Python**: 3.10 o superior
- **MySQL Server**: 8.0 o superior (compatible también con MariaDB)

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Clonar el repositorio y crear entorno virtual
```bash
git clone https://github.com/matuxvi7/codigo-femenino-backend.git
cd codigo-femenino-backend

python3 -m venv venv
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia el archivo `.env.example` como `.env` y configura los accesos a tu base de datos:
```bash
cp .env.example .env
```
Ejemplo de configuración:
```ini
PORT=5000
FLASK_DEBUG=True
CORS_ORIGINS=*

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=codigo_femenino
```

#### MySQL administrado en Aiven (TLS)

PyMySQL cifra la conexión y verifica el certificado y el hostname cuando se configura
el certificado CA de Aiven. Descarga el CA desde la consola de Aiven, guárdalo como
`certs/aiven-ca.pem` en el proyecto (ese archivo está excluido de Git) y configura
en `.env` la ruta absoluta al archivo:

```ini
DB_SSL_REQUIRED=true
DB_SSL_CA=C:/ruta/al/proyecto/certs/aiven-ca.pem
```

En Linux/macOS usa la ruta absoluta correspondiente, por ejemplo
`/ruta/al/proyecto/certs/aiven-ca.pem`. Si `DB_SSL_REQUIRED=true` pero falta
`DB_SSL_CA`, el backend falla explícitamente al cargar la configuración en lugar
de conectarse sin TLS. Para una base MySQL local, se pueden dejar ambas variables
sin configurar.

### Reinicio automático de la base de datos (solo desarrollo)

Por defecto, el backend **no borra ni reinicia la base** al arrancar. Si necesitas
recrear el esquema y cargar los datos de ejemplo en cada inicio local, configura
estas variables en `.env`:

```ini
APP_ENV=development
RESET_DEV_DATABASE_ON_STARTUP=true
```

Esta opción elimina por completo la base indicada por `DB_NAME` y la reconstruye
ejecutando `scripts/init_db.sql`. Se ejecuta una sola vez cuando inicia el proceso
del servidor (no en el proceso padre del recargador de Flask). **Todos los datos
de esa base se pierden en cada inicio o recarga de desarrollo.** No la habilites
en producción; el backend se negará a ejecutarla si `APP_ENV` no es `development`.

### 4. Inicializar la base de datos
Ejecuta el script SQL incluido para crear las tablas (`categories`, `articles`, `article_sections`, `lead_signups`) e insertar los artículos de demostración:
```bash
mysql -u root -p < scripts/init_db.sql
```

### 5. Iniciar el servidor
```bash
python app.py
```
El servidor quedará disponible en `http://localhost:5000` y la documentación en `http://localhost:5000/docs`.

---

---

## 🔗 Paginación HATEOAS

Los endpoints de colecciones (`GET /api/articles` y `GET /api/leads`) implementan el principio **HATEOAS** (*Hypermedia as the Engine of Application State*). Cada respuesta paginada incluye enlaces de navegación calculados dinámicamente preservando los filtros aplicados:

- `self`: URL de la página actual solicitada.
- `first`: Enlace a la primera página (`page=1`).
- `prev`: Enlace a la página anterior (`null` si se encuentra en la primera página).
- `next`: Enlace a la página siguiente (`null` si se encuentra en la última página).
- `last`: Enlace a la última página disponible.

Ejemplo de estructura de respuesta:

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 2,
    "per_page": 10,
    "total_items": 35,
    "total_pages": 4,
    "has_next": true,
    "has_prev": true,
    "links": {
      "self": "/api/articles?category=finanzas&page=2&per_page=10",
      "first": "/api/articles?category=finanzas&page=1&per_page=10",
      "prev": "/api/articles?category=finanzas&page=1&per_page=10",
      "next": "/api/articles?category=finanzas&page=3&per_page=10",
      "last": "/api/articles?category=finanzas&page=4&per_page=10"
    }
  },
  "_links": {
    "self": "/api/articles?category=finanzas&page=2&per_page=10",
    "first": "/api/articles?category=finanzas&page=1&per_page=10",
    "prev": "/api/articles?category=finanzas&page=1&per_page=10",
    "next": "/api/articles?category=finanzas&page=3&per_page=10",
    "last": "/api/articles?category=finanzas&page=4&per_page=10"
  }
}
```

---

## 📡 Referencia de Endpoints de la API

Todos los endpoints están prefijados con `/api` (a excepción de la documentación en `/docs`).

### 1. Estado del Sistema
- `GET /api/health`: Comprueba el estado del servicio y la conectividad activa con MySQL.

### 2. Categorías
- `GET /api/categories`: Lista todas las categorías con el conteo de artículos publicados en cada una.
- `GET /api/categories/<slug>`: Detalle de una categoría específica (`relaciones`, `autoestima`, `psicologia`, `belleza`).

### 3. Artículos
- `GET /api/articles`: Lista artículos con filtros y paginación HATEOAS. Parámetros opcionales (query string):
  - `category`: slug de la categoría (ej. `?category=relaciones`)
  - `search`: búsqueda de texto en título o resumen (ej. `?search=limites`)
  - `status`: `published` (por defecto), `draft`, `archived` o `all`
  - `page`: número de página (por defecto `1`)
  - `per_page` o `limit`: cantidad de elementos por página (por defecto `10`, máx `50`)
- `GET /api/articles/<slug>`: Obtiene el artículo completo con sus secciones ordenadas por `position`. Permite `?preview=true` para borradores.
- `POST /api/articles`: Crea un artículo nuevo con sus secciones.
- `PUT /api/articles/<slug>`: Actualiza metadatos y/o secciones del artículo.
- `DELETE /api/articles/<slug>`: Elimina un artículo y sus secciones en cascada.

### 4. Suscriptoras y Leads (Newsletter / Ebook Gratuito)
- `POST /api/leads`: Registro general de captación.
  ```json
  {
    "email": "lectora@ejemplo.com",
    "full_name": "Sofía García",
    "source": "guia_gratuita"
  }
  ```
- `POST /api/newsletter`: Acceso directo para el formulario de newsletter.
  ```json
  {
    "email": "lectora@ejemplo.com",
    "full_name": "Sofía García"
  }
  ```
- `POST /api/guia-gratuita`: Acceso directo para la descarga del ebook gratuito inicial.
  ```json
  {
    "email": "lectora@ejemplo.com",
    "full_name": "Sofía García"
  }
  ```
- `GET /api/leads`: Consulta el listado de leads con paginación HATEOAS. Parámetros opcionales:
  - `source`: filtrar por canal (`newsletter` o `guia_gratuita`)
  - `page`: número de página (por defecto `1`)
  - `per_page` o `limit`: cantidad de registros por página (por defecto `10`, máx `50`)

---

## 🌐 Conexión con el Frontend

La API tiene **CORS habilitado** por defecto para todos los orígenes (`*`), permitiendo que cualquier aplicación frontend (React, Next.js, Vue o HTML estático) pueda consumir los endpoints sin problemas de políticas de origen cruzado. Para producción, puedes restringir los dominios autorizados en la variable `CORS_ORIGINS` del archivo `.env`.
