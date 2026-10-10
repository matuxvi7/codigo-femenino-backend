"""
Módulo de utilidades para HATEOAS (Hypermedia as the Engine of Application State).
Proporciona funciones para generar enlaces de navegación en colecciones paginadas
y enriquecer respuestas RESTful.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode


def generate_pagination_links(
    endpoint: str,
    page: int,
    per_page: int,
    total_pages: int,
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Optional[str]]:
    """
    Genera los enlaces HATEOAS estándar de navegación para colecciones paginadas:
      - self: URL de la página actual solicitada
      - first: URL de la primera página (página 1)
      - prev: URL de la página anterior (None si está en la primera página o si page <= 1)
      - next: URL de la página siguiente (None si está en la última página o más allá)
      - last: URL de la última página disponible

    Preserva los parámetros de búsqueda o filtros (category, search, status, source, etc.),
    asegurando que los enlaces de navegación mantengan el contexto de la consulta activa.
    """
    params: Dict[str, Any] = {}
    if extra_params:
        for k, v in extra_params.items():
            # Excluir parámetros de paginación para inyectarlos dinámicamente
            if k not in ("page", "per_page", "limit") and v is not None and v != "":
                params[k] = v

    def make_url(target_page: int) -> str:
        query = dict(params)
        query["page"] = target_page
        query["per_page"] = per_page
        qs = urlencode(query)
        clean_endpoint = endpoint.split("?")[0]
        return f"{clean_endpoint}?{qs}" if qs else clean_endpoint

    safe_total_pages = max(1, total_pages)

    return {
        "self": make_url(page),
        "first": make_url(1),
        "prev": make_url(page - 1) if page > 1 else None,
        "next": make_url(page + 1) if page < safe_total_pages else None,
        "last": make_url(safe_total_pages),
    }


def build_hateoas_pagination(
    endpoint: str,
    pagination: Dict[str, Any],
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Enriquece un diccionario de paginación existente agregándole la clave 'links'
    con los enlaces de navegación calculados.
    """
    page = int(pagination.get("page", 1))
    per_page = int(pagination.get("per_page", 10))
    total_pages = int(pagination.get("total_pages", 1))

    links = generate_pagination_links(
        endpoint=endpoint,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        extra_params=extra_params,
    )

    enriched = dict(pagination)
    enriched["links"] = links
    return enriched


def build_paginated_response(
    data: List[Any],
    pagination: Dict[str, Any],
    endpoint: str,
    extra_params: Optional[Dict[str, Any]] = None,
    success: bool = True,
) -> Dict[str, Any]:
    """
    Construye la estructura completa de respuesta RESTful paginada con HATEOAS:
    - data: lista de recursos
    - pagination: metadatos numéricos más objeto 'links'
    - _links: enlaces HATEOAS en la raíz del payload (estándar HAL / JSON hypermedia)
    """
    enriched_pagination = build_hateoas_pagination(
        endpoint=endpoint,
        pagination=pagination,
        extra_params=extra_params,
    )

    return {
        "success": success,
        "data": data,
        "pagination": enriched_pagination,
        "_links": enriched_pagination["links"],
    }
