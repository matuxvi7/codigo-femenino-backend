from typing import Any, Dict, List, Tuple
from src.validators.common import validate_email

ALLOWED_SOURCES = ("newsletter", "guia_gratuita")


def validate_lead_payload(data: Any) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["El cuerpo de la solicitud debe ser un objeto JSON válido."], {}

    email = str(data.get("email", "")).strip().lower()
    full_name = data.get("full_name")
    source = str(data.get("source", "newsletter")).strip().lower()

    if not email:
        errors.append("El campo 'email' es obligatorio.")
    elif not validate_email(email):
        errors.append("El correo electrónico proporcionado no es válido.")

    if source not in ALLOWED_SOURCES:
        errors.append(f"El campo 'source' debe ser uno de: {', '.join(ALLOWED_SOURCES)}.")

    if full_name is not None:
        full_name = str(full_name).strip()
        if len(full_name) > 160:
            errors.append("El campo 'full_name' no puede superar los 160 caracteres.")
        if len(full_name) == 0:
            full_name = None

    if errors:
        return False, errors, {}

    return True, [], {
        "email": email,
        "full_name": full_name,
        "source": source
    }
