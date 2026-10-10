# Código Femenino - Backend API (Flask + MySQL)

Backend RESTful modular desarrollado en Python con **Flask** y **MySQL 8.0**, diseñado específicamente para dar soporte a la revista digital **Código Femenino** según sus especificaciones editoriales y de negocio.

---

## 🚀 Arquitectura Modular

El proyecto implementa una arquitectura por capas desacoplada:

```
codigo-femenino-backend/
├── app.py                      # Punto de entrada y configuración de la app Flask
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
    ├── validators/             # Validación y sanitización de datos de entrada
    │   ├── common.py
    │   ├── article_validators.py
    │   └── lead_validators.py
    └── routes/                 # Controladores y endpoints REST (/api)
        ├── health.py           # Estado de la API y de la conexión a MySQL
        ├── categories.py       # Endpoints de categorías
        ├── articles.py         # Endpoints de artículos, secciones y búsqueda
        └── leads.py            # Captación de newsletter y descarga de guía gratuita
```

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

### 4. Inicializar la base de datos
Ejecuta el script SQL incluido para crear las tablas (`categories`, `articles`, `article_sections`, `lead_signups`) e insertar los artículos de demostración:
```bash
mysql -u root -p < scripts/init_db.sql
```

### 5. Iniciar el servidor
```bash
python app.py
```
El servidor quedará disponible en `http://localhost:5000`.

---

## 📡 Referencia de Endpoints de la API

Todos los endpoints están prefijados con `/api`.

### 1. Estado del Sistema
- `GET /api/health`: Comprueba el estado del servicio y la conectividad activa con MySQL.

### 2. Categorías
- `GET /api/categories`: Lista todas las categorías con el conteo de artículos publicados en cada una.
- `GET /api/categories/<slug>`: Detalle de una categoría específica (`relaciones`, `autoestima`, `psicologia`, `belleza`).

### 3. Artículos
- `GET /api/articles`: Lista artículos paginados. Parámetros opcionales (query string):
  - `category`: slug de la categoría (ej. `?category=relaciones`)
  - `search`: búsqueda de texto en título o resumen (ej. `?search=limites`)
  - `status`: `published` (por defecto), `draft`, `archived` o `all`
  - `page`: número de página (por defecto `1`)
  - `per_page`: cantidad de elementos por página (por defecto `10`, máx `50`)
- `GET /api/articles/<slug>`: Obtiene el artículo completo con sus secciones ordenadas por `position` y una lista de artículos relacionados de la misma categoría.
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
- `GET /api/leads`: Consulta el listado de leads registrados (parámetro opcional `?source=newsletter` o `?source=guia_gratuita`).

---

## 🌐 Conexión con el Frontend

La API tiene **CORS habilitado** por defecto para todos los orígenes (`*`), permitiendo que cualquier aplicación frontend (React, Next.js, Vue o HTML estático) pueda consumir los endpoints sin problemas de políticas de origen cruzado. Para producción, puedes restringir los dominios autorizados en la variable `CORS_ORIGINS` del archivo `.env`.
