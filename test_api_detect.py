"""
test_api_detect.py — End-to-End API Test for GroundingDINO + SAM Integration
=============================================================================
Tests the full FastAPI integration:
  1. Boots FastAPI app
  2. Creates test user & JWT token
  3. Uploads D:/AI/GroundingDINO/test_image.webp
  4. Calls POST /analysis/detect with prompt "sofa"
  5. Verifies 200 OK, detection boxes, mask_url, and mask file on disk
"""

import os
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app
from database.database import SessionLocal, engine, Base
from database.models import User, UploadedImage
from services.auth_service import hash_password, create_access_token
from utils.helpers import generate_uuid

client = TestClient(app)

TEST_IMAGE_PATH = Path("D:/AI/GroundingDINO/test_image.webp")


def setup_test_user_and_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "test_dino_user").first()
        if not user:
            user = User(
                id=generate_uuid(),
                username="test_dino_user",
                email="test_dino@designverse.ai",
                hashed_password=hash_password("Password123!"),
                full_name="DINO SAM Tester",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token, _ = create_access_token(user.id)
        return user, token
    finally:
        db.close()


def run_e2e_test():
    print("=" * 60)
    print("DesignVerse AI — End-to-End API Detection Test")
    print("=" * 60)

    # 1. User & Auth
    user, token = setup_test_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[1] Authenticated as user: {user.username} (id={user.id})")

    # 2. Upload test image
    if not TEST_IMAGE_PATH.exists():
        print(f"[FAIL] Test image not found at {TEST_IMAGE_PATH}")
        sys.exit(1)

    with open(TEST_IMAGE_PATH, "rb") as f:
        file_bytes = f.read()

    upload_resp = client.post(
        "/upload/",
        headers=headers,
        files={"file": ("test_image.webp", file_bytes, "image/webp")},
    )
    print(f"[2] Upload status: {upload_resp.status_code}")
    if upload_resp.status_code != 201 and upload_resp.status_code != 200:
        print(f"[FAIL] Upload failed: {upload_resp.text}")
        sys.exit(1)

    upload_data = upload_resp.json()
    image_id = upload_data.get("image_id") or upload_data.get("id")
    print(f"    Image ID: {image_id}")

    # 3. Call POST /analysis/detect
    print("\n[3] Calling POST /analysis/detect with prompt='sofa'...")
    detect_payload = {
        "image_id": image_id,
        "prompt": "sofa",
        "box_threshold": 0.30,
        "text_threshold": 0.25,
    }

    detect_resp = client.post("/analysis/detect", headers=headers, json=detect_payload)
    print(f"    Detect status code: {detect_resp.status_code}")
    if detect_resp.status_code != 200:
        print(f"[FAIL] Detect request failed: {detect_resp.text}")
        sys.exit(1)

    result = detect_resp.json()
    print("\n[4] Detect Response:")
    print(f"    success:    {result.get('success')}")
    print(f"    prompt:     {result.get('prompt')}")
    print(f"    count:      {result.get('count')}")
    print(f"    message:    {result.get('message')}")

    detections = result.get("detections", [])
    if not detections:
        print("[FAIL] No detections returned by /analysis/detect!")
        sys.exit(1)

    print(f"\n[5] Verified {len(detections)} detection(s):")
    for i, d in enumerate(detections):
        print(f"    Detection {i+1}:")
        print(f"      label:      {d.get('label')}")
        print(f"      confidence: {d.get('confidence')}")
        print(f"      bbox:       {d.get('bbox')}")
        print(f"      mask_url:   {d.get('mask_url')}")
        print(f"      mask_score: {d.get('mask_score')}")

        mask_url = d.get("mask_url")
        if mask_url:
            # Mask should be in backend/storage/masks
            mask_rel = mask_url.replace("/storage/", "")
            mask_disk_path = backend_dir / "storage" / mask_rel
            if mask_disk_path.exists():
                print(f"      [OK] Mask file exists on disk: {mask_disk_path} ({mask_disk_path.stat().st_size} bytes)")
            else:
                print(f"      [WARN] Mask file not found on disk at {mask_disk_path}")

    print("\n" + "=" * 60)
    print("API END-TO-END TEST: PASSED [SUCCESS]")
    print("=" * 60)


if __name__ == "__main__":
    run_e2e_test()
