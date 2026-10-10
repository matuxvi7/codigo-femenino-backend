from typing import Any, Dict, Optional, Tuple

import cloudinary
import cloudinary.uploader

from src.config import Config

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif", "avif"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class ImageUploadError(Exception):
    """Error al validar o subir una imagen."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _configure() -> None:
    if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY or not Config.CLOUDINARY_API_SECRET:
        raise ImageUploadError(
            "El servicio de imágenes no está configurado. Revisa las variables CLOUDINARY_*.",
            status_code=503,
        )
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True,
    )


class ImageService:
    @staticmethod
    def upload_article_image(file_storage: Any) -> Dict[str, str]:
        """Sube una imagen de artículo a Cloudinary y devuelve su URL y public_id."""
        if file_storage is None or not getattr(file_storage, "filename", ""):
            raise ImageUploadError("Debes adjuntar un archivo de imagen en el campo 'image'.")

        filename = file_storage.filename or ""
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise ImageUploadError(
                f"Formato no permitido. Usa: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            )

        # Validar tamaño leyendo el stream
        data = file_storage.read()
        if not data:
            raise ImageUploadError("El archivo está vacío.")
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise ImageUploadError("La imagen no puede superar los 5 MB.")

        _configure()
        try:
            result = cloudinary.uploader.upload(
                data,
                folder="codigo-femenino/articles",
                resource_type="image",
                transformation=[{"quality": "auto", "fetch_format": "auto"}],
            )
        except Exception as exc:
            raise ImageUploadError(f"No se pudo subir la imagen: {exc}", status_code=502)

        return {
            "image_url": result["secure_url"],
            "image_public_id": result["public_id"],
        }

    @staticmethod
    def delete_image(public_id: Optional[str]) -> None:
        """Elimina una imagen de Cloudinary (mejor esfuerzo, sin romper el flujo)."""
        if not public_id:
            return
        try:
            _configure()
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass
