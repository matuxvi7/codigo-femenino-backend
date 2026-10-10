import re
from typing import Any, Dict, List, Tuple

ALLOWED_STATUSES = ("draft", "published", "archived")
SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(slug: str) -> bool:
    if not slug or not isinstance(slug, str):
        return False
    return bool(SLUG_REGEX.match(slug.strip()))


def validate_article_payload(data: Any, is_update: bool = False) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["El cuerpo de la solicitud debe ser un objeto JSON válido."], {}

    clean_data: Dict[str, Any] = {}

    if not is_update or "title" in data:
        title = str(data.get("title", "")).strip()
        if not title:
            errors.append("El campo 'title' es obligatorio.")
        elif len(title) > 255:
            errors.append("El campo 'title' no puede superar los 255 caracteres.")
        clean_data["title"] = title

    if not is_update or "slug" in data:
        slug = str(data.get("slug", "")).strip().lower()
        if not slug:
            errors.append("El campo 'slug' es obligatorio.")
        elif not validate_slug(slug):
            errors.append("El campo 'slug' solo puede contener letras minúsculas, números y guiones.")
        elif len(slug) > 180:
            errors.append("El campo 'slug' no puede superar los 180 caracteres.")
        clean_data["slug"] = slug

    if not is_update or "category_id" in data:
        category_id = data.get("category_id")
        try:
            category_id = int(category_id)
            if category_id <= 0:
                raise ValueError()
            clean_data["category_id"] = category_id
        except (TypeError, ValueError):
            errors.append("El campo 'category_id' debe ser un identificador entero positivo.")

    if not is_update or "excerpt" in data:
        excerpt = str(data.get("excerpt", "")).strip()
        if not excerpt:
            errors.append("El campo 'excerpt' es obligatorio.")
        clean_data["excerpt"] = excerpt

    if not is_update or "author" in data:
        author = str(data.get("author", "Redacción Código Femenino")).strip()
        if len(author) > 160:
            errors.append("El campo 'author' no puede superar los 160 caracteres.")
        clean_data["author"] = author

    if "read_time_minutes" in data or not is_update:
        read_time = data.get("read_time_minutes", 5)
        try:
            read_time = int(read_time)
            if read_time <= 0 or read_time > 255:
                raise ValueError()
            clean_data["read_time_minutes"] = read_time
        except (TypeError, ValueError):
            errors.append("El campo 'read_time_minutes' debe ser un entero entre 1 y 255.")

    if "status" in data or not is_update:
        status = str(data.get("status", "draft")).strip().lower()
        if status not in ALLOWED_STATUSES:
            errors.append(f"El campo 'status' debe ser uno de: {', '.join(ALLOWED_STATUSES)}.")
        clean_data["status"] = status

    if "published_at" in data:
        clean_data["published_at"] = data.get("published_at")

    for field, max_length in (("image_url", 500), ("image_public_id", 255)):
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, str):
                errors.append(f"El campo '{field}' debe ser texto o null.")
            elif isinstance(value, str):
                value = value.strip()
                if not value:
                    errors.append(f"El campo '{field}' no puede estar vacío; usa null para quitarlo.")
                elif len(value) > max_length:
                    errors.append(
                        f"El campo '{field}' no puede superar los {max_length} caracteres."
                    )
                else:
                    clean_data[field] = value
            else:
                clean_data[field] = None
        elif not is_update:
            clean_data[field] = None

    if "sections" in data:
        sections = data.get("sections")
        if not isinstance(sections, list):
            errors.append("El campo 'sections' debe ser una lista de secciones.")
        else:
            clean_sections = []
            for idx, sec in enumerate(sections):
                if not isinstance(sec, dict):
                    errors.append(f"La sección #{idx+1} debe ser un objeto.")
                    continue
                content = str(sec.get("content", "")).strip()
                if not content:
                    errors.append(f"La sección #{idx+1} requiere contenido en 'content'.")
                heading = sec.get("heading")
                if heading is not None:
                    heading = str(heading).strip()
                    if len(heading) > 255:
                        errors.append(f"El encabezado de la sección #{idx+1} no puede exceder 255 caracteres.")
                clean_sections.append({
                    "position": sec.get("position", idx + 1),
                    "heading": heading,
                    "content": content
                })
            clean_data["sections"] = clean_sections

    if errors:
        return False, errors, {}

    return True, [], clean_data
