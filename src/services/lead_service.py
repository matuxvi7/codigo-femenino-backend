from typing import Any, Dict, List, Optional
from src.repositories.lead_repository import LeadRepository


class LeadService:
    @staticmethod
    def register_lead(email: str, full_name: Optional[str], source: str) -> Dict[str, Any]:
        result = LeadRepository.create(email=email, full_name=full_name, source=source)
        if result.get("already_registered"):
            return {
                "success": True,
                "already_registered": True,
                "message": f"Tu correo {email} ya se encuentra registrado para '{source}'. ¡Gracias por formar parte!",
                "data": {
                    "email": email,
                    "source": source
                }
            }

        return {
            "success": True,
            "already_registered": False,
            "message": "Suscripción confirmada correctamente. ¡Bienvenida a Código Femenino!",
            "data": {
                "id": result.get("id"),
                "email": email,
                "full_name": full_name,
                "source": source
            }
        }

    @staticmethod
    def list_leads(
        source: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        return LeadRepository.get_paginated(source=source, page=page, per_page=per_page)
