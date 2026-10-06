import io
import pytest
from datetime import datetime, timezone, timedelta
from PIL import Image


def get_token(client, email, password, role="STUDENT", name="User"):
    client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": name,
        "role": role
    })
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def create_dummy_image_bytes():
    image = Image.new("RGB", (800, 450), color="blue")
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def test_event_lifecycle_and_media_upload(client):
    admin_token = get_token(client, "admin_media@fest.edu", "Pass1234!", "ADMIN", "Admin User")
    coord_token = get_token(client, "coord_a@fest.edu", "Pass1234!", "EVENT_COORDINATOR", "Coord A")
    coord_b_token = get_token(client, "coord_b@fest.edu", "Pass1234!", "EVENT_COORDINATOR", "Coord B")
    student_token = get_token(client, "student_media@fest.edu", "Pass1234!", "STUDENT", "Student User")

    # 1. Admin creates category
    cat_res = client.post("/api/events/categories", json={
        "name": "Hackathons",
        "description": "Tech competitions",
        "icon": "Code"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]

    # 2. Coordinator A creates event
    now = datetime.now(timezone.utc)
    event_payload = {
        "title": "Perceptron AI Hackathon",
        "description": "Build real production agentic AI systems.",
        "category_id": cat_id,
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=3)).isoformat(),
        "registration_deadline": (now + timedelta(days=1)).isoformat(),
        "max_participants": 100,
        "registration_fee": 250.0,
        "prize_pool": "₹50,000",
        "is_team_event": False
    }
    create_res = client.post("/api/events", json=event_payload, headers={"Authorization": f"Bearer {coord_token}"})
    assert create_res.status_code == 201
    event_id = create_res.json()["id"]

    # 3. Coordinator A uploads custom event cover image
    img_bytes = create_dummy_image_bytes()
    upload_res = client.post(
        f"/api/events/{event_id}/media",
        files={"file": ("cover.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {coord_token}"}
    )
    assert upload_res.status_code == 201
    media_data = upload_res.json()
    assert media_data["is_primary"] is True
    assert "public_url" in media_data

    # 4. Student attempts to upload event image -> 403 Forbidden
    student_upload = client.post(
        f"/api/events/{event_id}/media",
        files={"file": ("cover.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert student_upload.status_code == 403

    # 5. Coordinator B attempts to upload to Coordinator A's event -> 403 Forbidden
    coord_b_upload = client.post(
        f"/api/events/{event_id}/media",
        files={"file": ("cover.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {coord_b_token}"}
    )
    assert coord_b_upload.status_code == 403

    # 6. Coordinator A publishes event
    pub_res = client.post(f"/api/events/{event_id}/publish", headers={"Authorization": f"Bearer {coord_token}"})
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"

    # 7. Public event detail reflects uploaded cover image URL
    detail_res = client.get(f"/api/events/{event_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["cover_image"] is not None
    assert detail_res.json()["cover_image"]["url"] == media_data["public_url"]
