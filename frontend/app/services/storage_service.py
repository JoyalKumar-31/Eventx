import os
import uuid
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io

from app.core.config import settings

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class BaseStorageService(ABC):
    @abstractmethod
    def save_file(self, file_bytes: bytes, original_filename: str, subfolder: str = "events") -> Tuple[str, str, int, int]:
        """
        Saves file and returns (storage_path, public_url, width, height).
        """
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage."""
        pass


class LocalStorageService(BaseStorageService):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(self, file_bytes: bytes, original_filename: str, subfolder: str = "events") -> Tuple[str, str, int, int]:
        target_dir = os.path.join(self.base_path, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        _, ext = os.path.splitext(original_filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": f"Unsupported file extension '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}", "error_code": "INVALID_FILE_EXTENSION"}
            )

        # Generate non-colliding cryptographically safe filename
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        storage_path = os.path.join(target_dir, safe_filename)

        # Extract dimensions and verify integrity using Pillow
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()
            # Reopen for dimensions after verify
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "message": "Corrupted or invalid image file", "error_code": "INVALID_IMAGE"}
            )

        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        # Public URL format exposed through FastAPI StaticFiles mount
        public_url = f"/uploads/{subfolder}/{safe_filename}"
        return storage_path, public_url, width, height

    def delete_file(self, storage_path: str) -> bool:
        try:
            if os.path.exists(storage_path):
                # Ensure no path traversal
                real_path = os.path.abspath(storage_path)
                if real_path.startswith(self.base_path):
                    os.remove(real_path)
                    return True
        except Exception:
            pass
        return False


def get_storage_service() -> BaseStorageService:
    # Pluggable: easily swap or instantiate S3StorageService if EVENT_MEDIA_STORAGE == 's3'
    storage_type = settings.EVENT_MEDIA_STORAGE.lower()
    if storage_type == "local":
        base_dir = settings.EVENT_MEDIA_PATH.split("/")[0] if "/" in settings.EVENT_MEDIA_PATH else "uploads"
        return LocalStorageService(base_path=base_dir)
    return LocalStorageService(base_path="uploads")
