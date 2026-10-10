import os
from flask import Blueprint, Response, render_template_string, send_from_directory

docs_bp = Blueprint("docs", __name__)

SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Código Femenino API - Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/favicon-32x32.png" sizes="32x32" />
  <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/favicon-16x16.png" sizes="16x16" />
  <style>
    html {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *, *:before, *:after {
      box-sizing: inherit;
    }
    body {
      margin: 0;
      background: #fafafa;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .topbar {
      display: none !important;
    }
    .swagger-ui .info {
      margin: 25px 0 20px 0;
    }
    .swagger-ui .info .title {
      font-size: 32px;
      color: #701a75;
    }
    .custom-header {
      background: linear-gradient(135deg, #701a75 0%, #a21caf 100%);
      color: #ffffff;
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .custom-header h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    .custom-header a {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.2);
      padding: 6px 12px;
      border-radius: 6px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: background 0.2s;
    }
    .custom-header a:hover {
      background: rgba(255, 255, 255, 0.35);
    }
  </style>
</head>
<body>
  <header class="custom-header">
    <h1>Código Femenino &bull; API Documentation</h1>
    <div>
      <a href="/docs/openapi.yaml" download="openapi.yaml" target="_blank">&darr; Descargar openapi.yaml</a>
    </div>
  </header>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" charset="UTF-8"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
  <script>
    window.onload = function() {
      window.ui = SwaggerUIBundle({
        url: "/docs/openapi.yaml",
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        docExpansion: "list",
        filter: true,
        tryItOutEnabled: true
      });
    };
  </script>
</body>
</html>
"""


@docs_bp.get("/docs")
def swagger_ui():
    """Sirve la interfaz interactiva de Swagger UI."""
    return render_template_string(SWAGGER_UI_HTML)


@docs_bp.get("/docs/openapi.yaml")
@docs_bp.get("/openapi.yaml")
def serve_openapi_spec():
    """Devuelve el archivo de especificación OpenAPI 3.0."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return send_from_directory(
        repo_root,
        "openapi.yaml",
        mimetype="application/yaml"
    )
