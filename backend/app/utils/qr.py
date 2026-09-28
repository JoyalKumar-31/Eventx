import os
import qrcode
from io import BytesIO
import base64
from app.core.config import settings


def generate_qr_code_image(token: str) -> str:
    """
    Generates a QR code image for a fest pass token.
    Saves the PNG to the uploads directory and returns the relative file path.
    Also provides data URL if needed.
    """
    qr_dir = os.path.join(settings.UPLOAD_DIR, "passes")
    os.makedirs(qr_dir, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E1B4B", back_color="white")  # Festora indigo theme
    file_name = f"pass_{token}.png"
    file_path = os.path.join(qr_dir, file_name)
    img.save(file_path)

    return f"/uploads/passes/{file_name}"


def generate_qr_code_base64(token: str) -> str:
    """Returns a base64 encoded data URI string for instant inline image rendering in React."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E1B4B", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
