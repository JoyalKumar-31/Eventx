import base64
import hashlib
import io
import json
import uuid
import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_qr_hash(registration_number: str, event_id: int, user_id: int) -> str:
    """Generate a tamper-resistant unique token for entry pass verification."""
    unique_entropy = f"{registration_number}:{event_id}:{user_id}:{uuid.uuid4().hex}"
    return hashlib.sha256(unique_entropy.encode()).hexdigest()


def generate_qr_image_base64(data_payload: str) -> str:
    """Generate a high-resolution base64 PNG QR code."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def build_qr_pass_payload(registration_number: str, qr_code_hash: str, event_id: int) -> str:
    payload = {
        "reg_num": registration_number,
        "token": qr_code_hash,
        "event_id": event_id
    }
    return json.dumps(payload)
