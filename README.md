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
APP_ENV=development
RESET_DEV_DATABASE_ON_STARTUP=false
CORS_ORIGINS=*

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=codigo_femenino
```

#### MySQL administrado en Aiven (TLS)

PyMySQL cifra la conexión y verifica el certificado y el hostname cuando se configura
el certificado CA de Aiven. Descarga el CA desde la consola de Aiven, guárdalo dentro
de `certs/` para desarrollo local (esa carpeta está excluida de Git) y configura
en `.env` la ruta absoluta al archivo:

```ini
DB_SSL_REQUIRED=true
DB_SSL_CA=C:/ruta/al/proyecto/certs/ca_aiven.pem
```

En producción, TLS con CA es obligatorio. Si falta la configuración o el archivo,
la aplicación falla al arrancar con un mensaje que no expone credenciales. Para una
base MySQL local, se pueden dejar ambas variables sin configurar.

### Reinicio automático de la base de datos (solo desarrollo)

Por defecto, el backend **no borra ni reinicia la base** al arrancar. Si necesitas
recrear el esquema y cargar los datos de ejemplo en cada inicio local, configura
estas variables en `.env`:

```ini
APP_ENV=development
RESET_DEV_DATABASE_ON_STARTUP=true
```

Esta opción elimina por completo la base indicada por `DB_NAME` y la reconstruye
ejecutando `scripts/init_db.sql`. Solo se permite con `APP_ENV=development` y solo
se ejecuta al iniciar `python app.py`, no al importar la aplicación con Gunicorn.
**Todos los datos de esa base se pierden en cada inicio o recarga de desarrollo.**
La configuración de producción rechaza esta opción.

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

## 🚀 Despliegue en Render

El repositorio incluye `render.yaml` como plantilla del servicio web. Al crear el
servicio desde el Blueprint, completá las variables marcadas como manuales en
Render. El comando de inicio configurado es:

```bash
gunicorn --workers 2 --threads 4 --bind 0.0.0.0:$PORT "app:create_app()"
```

Usa la factory Flask `create_app()`. En producción `APP_ENV=production` fuerza
debug desactivado, exige TLS verificado hacia MySQL y rechaza la inicialización
destructiva de la base. No se ejecutan `scripts/init_db.sql` ni otros scripts
automáticamente. Inicializá o migrá el esquema de Aiven por un procedimiento
manual controlado; no uses el reinicio de desarrollo contra datos reales.

### Acceso del panel administrativo

El backend entrega JWT Bearer de corta duración (15 minutos) a través de
`POST /api/admin/auth/login`, usando `ADMIN_USERNAME` y `ADMIN_PASSWORD`.
Todas las solicitudes protegidas deben incluir
`Authorization: Bearer <access_token>`. Configurá también `JWT_SECRET_KEY` con
un valor aleatorio único de al menos 32 bytes y una contraseña de administración
de al menos 12 caracteres; podés generar el secreto con:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Guardá estas variables como secretos del servicio Render, no en el frontend ni
en Git. El frontend solicita el token al backend y lo envía en las peticiones
administrativas. No compartas el token ni lo incluyas en URLs. El endpoint de login es público por necesidad; no devuelve token si las
credenciales son incorrectas, vacías, de ejemplo o no están configuradas.
Al rotar `JWT_SECRET_KEY`, todos los tokens vigentes quedan invalidados. Los JWT
son stateless y no tienen revocación individual antes de su vencimiento.

Rutas públicas de lectura: health, categorías, artículos publicados y
documentación. Los formularios de suscripción también siguen públicos.
Requieren autenticación: listado de leads, creación/actualización/eliminación de
artículos y lectura de drafts/archived mediante `status` o `preview=true`.
Actualmente no existen rutas HTTP para modificar categorías ni subir/eliminar
imágenes; si se agregan, deben protegerse con el mismo JWT.

La API pública de suscripción no requiere login. El login está limitado a 5
intentos por minuto por IP; los tres formularios comparten un cupo de 10
solicitudes por minuto y 30 por hora por IP. En producción estos contadores se
almacenan en Redis para que sean compartidos por todos los workers e instancias.
Render debe tener conectividad privada con el servicio Redis. La aplicación
confía en una cabecera de IP reenviada por el proxy de Render; no expongas Gunicorn
saltándote ese proxy.

### Variables requeridas en Render

- `APP_ENV=production`, `FLASK_DEBUG=false`,
  `RESET_DEV_DATABASE_ON_STARTUP=false`.
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` y `JWT_SECRET_KEY` para emitir tokens del
  panel; usá contraseñas fuertes y un secreto JWT aleatorio de al menos 32 bytes.
- `REDIS_URL`: URI privada de un servicio Redis compatible, preferentemente
  `rediss://` con TLS. Es obligatoria en producción; por ejemplo, usá un servicio
  Redis administrado accesible desde Render (Render Key Value o un proveedor
  compatible). No uses `memory://`: solo se usa para desarrollo local y no
  comparte los límites entre procesos.
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: datos de conexión
  de Aiven. Guardá credenciales únicamente como variables privadas del servicio.
- `DB_SSL_REQUIRED=true` y `DB_SSL_CA=/etc/secrets/aiven-ca.pem`.
- `CORS_ORIGINS`: uno o varios orígenes HTTPS exactos separados por comas, por
  ejemplo `https://codigo-femenino.vercel.app`. Agregá cada dominio de preview
  expresamente si debe acceder a la API. No se aceptan comodines en producción.
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`,
  `CLOUDINARY_API_SECRET`: opcionales para las operaciones que usan el servicio
  de carga de imágenes. Si se configura una, deben configurarse las tres.

En **Render → servicio → Environment → Secret Files**, cargá el certificado CA
descargado desde Aiven con el nombre `aiven-ca.pem`. Render lo monta como
`/etc/secrets/aiven-ca.pem`; el archivo no debe subirse a Git. `render.yaml`
configura `DB_SSL_CA` con esa ruta. En local, usá la ruta absoluta al certificado
guardado en la carpeta ignorada `certs/`.

El health check de Render usa `GET /api/health` y responde `503` si MySQL no está
disponible; comprobá que el firewall/lista de IPs de Aiven permita conexiones
desde Render y que el servicio Aiven esté activo. Luego verificá:

1. `GET /` devuelve el índice informativo de la API.
2. `GET /api/health` devuelve `200` con estado de base `connected`.
3. `GET /api/categories` y `GET /api/articles` devuelven `200`.
4. `GET /docs` y `GET /docs/openapi.yaml` sirven Swagger y su especificación.
5. `POST /api/admin/auth/login` entrega un token solo con credenciales válidas;
   sin Bearer, `GET /api/leads`, las escrituras de artículos y los previews
   responden `401`.

La API acepta `image_url`/`image_public_id` en los artículos. Aunque existe un
servicio interno de Cloudinary, actualmente no hay una ruta HTTP de carga de
archivos que lo invoque; para carga desde el panel deberá definirse e integrarse
ese flujo aparte. La API puede guardar las URLs e identificadores Cloudinary que
el panel le envíe.

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

En desarrollo local CORS permite los orígenes configurados en `.env.example`.
En producción, `CORS_ORIGINS` debe listar únicamente los orígenes HTTPS exactos
del frontend de Vercel, separados por comas. Cada URL de preview debe agregarse
explícitamente; no se habilitan comodines en producción.
