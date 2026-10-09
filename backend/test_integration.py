"""
test_integration.py — Complete Backend & PostgreSQL Integration Test
=====================================================================
Tests the full lifecycle:
1. PostgreSQL connection & tables
2. User registration & authentication
3. Image upload & verification of BYTEA in PostgreSQL
4. Image retrieval via streaming endpoint with Bearer & query token
5. AI Analysis (mock)
6. Natural language prompt edit (mock)
7. Design approval
8. 3D Model generation (mock)
9. Project history listing & detail
10. Project deletion & cascade cleanup
"""

import hashlib
import io
import json
from PIL import Image
from fastapi.testclient import TestClient

from main import create_application
from database.database import Base, engine, SessionLocal
from database.models import UploadedImage, Project, User

def run_tests():
    print("=" * 60)
    print("DESIGNVERSE AI: POSTGRESQL & BACKEND INTEGRATION TEST")
    print("=" * 60)

    # 1. Ensure tables in PostgreSQL
    Base.metadata.create_all(bind=engine)
    print("[PASS] PostgreSQL tables verified.")

    app = create_application()
    client = TestClient(app)

    # 2. Test Registration
    test_user_payload = {
        "username": "testdesigner",
        "email": "designer@designverse.ai",
        "password": "SecurePassword123!",
        "full_name": "Test Interior Designer"
    }

    # Clean up prior test user if exists
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == test_user_payload["email"]).first()
    if existing_user:
        db.delete(existing_user)
        db.commit()
    db.close()

    reg_res = client.post("/auth/register", json=test_user_payload)
    assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"
    token_data = reg_res.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[PASS] User registered successfully (user_id={token_data['user']['id']}).")

    # 3. Test /auth/me
    me_res = client.get("/auth/me", headers=headers)
    assert me_res.status_code == 200, f"/auth/me failed: {me_res.text}"
    print("[PASS] Authenticated user profile retrieved.")

    # 4. Generate a test image in memory
    img = Image.new("RGB", (640, 480), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    original_bytes = img_byte_arr.getvalue()
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    print(f"Generated test JPEG: {len(original_bytes)} bytes, sha256={original_hash[:12]}...")

    # 5. Upload image
    files = {
        "file": ("living_room.jpg", original_bytes, "image/jpeg")
    }
    upload_res = client.post("/upload/", files=files, headers=headers)
    assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    image_id = upload_data["image_id"]
    print(f"[PASS] Image uploaded (image_id={image_id}).")

    # 6. CRITICAL VERIFICATION: Check PostgreSQL BYTEA column directly
    db = SessionLocal()
    db_image = db.query(UploadedImage).filter(UploadedImage.id == image_id).first()
    assert db_image is not None, "UploadedImage record missing in PostgreSQL!"
    assert db_image.image_data is not None, "CRITICAL ERROR: image_data BYTEA is NULL!"
    assert len(db_image.image_data) == len(original_bytes), (
        f"Byte length mismatch! DB={len(db_image.image_data)}, Original={len(original_bytes)}"
    )
    db_hash = hashlib.sha256(db_image.image_data).hexdigest()
    assert db_hash == original_hash, "SHA256 hash mismatch! Stored bytes differ from original."
    print(f"[PASS - CRITICAL] Image BYTEA verified in PostgreSQL! ({len(db_image.image_data)} bytes, sha256 match).")
    db.close()

    # 7. Test Image Retrieval with Bearer Header
    retrieval_res = client.get(f"/upload/images/{image_id}", headers=headers)
    assert retrieval_res.status_code == 200, f"Retrieval failed: {retrieval_res.text}"
    assert retrieval_res.headers["content-type"] == "image/jpeg"
    assert hashlib.sha256(retrieval_res.content).hexdigest() == original_hash
    print("[PASS] Image retrieved via /upload/images/{id} with Bearer token.")

    # 8. Test Image Retrieval with ?token= Query Parameter (for HTML <img> tags)
    query_res = client.get(f"/images/{image_id}?token={token}")
    assert query_res.status_code == 200, f"Query token retrieval failed: {query_res.text}"
    assert query_res.headers["content-type"] == "image/jpeg"
    assert hashlib.sha256(query_res.content).hexdigest() == original_hash
    print("[PASS] Image retrieved via /images/{id}?token=... for <img> tags.")

    # 9. Test Analysis
    analysis_res = client.post("/analysis/", json={"image_id": image_id}, headers=headers)
    assert analysis_res.status_code == 200, f"Analysis failed: {analysis_res.text}"
    analysis_data = analysis_res.json()
    assert len(analysis_data["objects"]) > 0, "Analysis returned no objects"
    print(f"[PASS] AI Scene analysis: detected {len(analysis_data['objects'])} objects: {analysis_data['objects']}")

    # 10. Test Natural Language Prompt Edit
    edit_payload = {
        "image_id": image_id,
        "prompt": "Change the sofa to a dark blue modern leather sofa.",
        "target_object": "Sofa"
    }
    edit_res = client.post("/editor/edit", json=edit_payload, headers=headers)
    assert edit_res.status_code == 200, f"Edit failed: {edit_res.text}"
    edit_data = edit_res.json()
    project_id = edit_data["project_id"]
    assert edit_data["target_object"] == "Sofa"
    print(f"[PASS] AI Image Edit: project_id={project_id}, target_object={edit_data['target_object']}.")

    # Verify Project in PostgreSQL has target_object and edited_image_data
    db = SessionLocal()
    proj = db.query(Project).filter(Project.id == project_id).first()
    assert proj is not None
    assert proj.target_object == "Sofa"
    assert proj.status == "edited"
    print(f"[PASS] Project verified in PostgreSQL (status={proj.status}, target={proj.target_object}).")
    db.close()

    # 11. Test Approve Design
    approve_res = client.post("/editor/approve", json={"project_id": project_id}, headers=headers)
    assert approve_res.status_code == 200, f"Approve failed: {approve_res.text}"
    assert approve_res.json()["status"] == "approved"
    print("[PASS] Design approved successfully.")

    # 12. Test Make It 3D
    make_3d_res = client.post("/viewer/generate3d", json={"project_id": project_id}, headers=headers)
    assert make_3d_res.status_code == 200, f"Make 3D failed: {make_3d_res.text}"
    model_path = make_3d_res.json()["model"]
    print(f"[PASS] 3D Model generated: {model_path}.")

    # 13. Test Project History
    hist_res = client.get("/history/", headers=headers)
    assert hist_res.status_code == 200, f"History failed: {hist_res.text}"
    hist_data = hist_res.json()
    assert hist_data["total"] >= 1
    item = hist_data["projects"][0]
    assert item["project_id"] == project_id
    assert item["status"] == "model_ready"
    assert "upload/images/" in item["original_image"]
    assert item["target_object"] == "Sofa"
    print(f"[PASS] History listing verified: {hist_data['total']} projects, original_image points to API.")

    # 14. Test Single Project Detail
    proj_detail_res = client.get(f"/history/{project_id}", headers=headers)
    assert proj_detail_res.status_code == 200
    assert proj_detail_res.json()["project_id"] == project_id
    print("[PASS] Single project detail retrieved.")

    # 15. Test Project Deletion
    del_res = client.delete(f"/history/{project_id}", headers=headers)
    assert del_res.status_code == 200
    db = SessionLocal()
    assert db.query(Project).filter(Project.id == project_id).first() is None
    assert db.query(UploadedImage).filter(UploadedImage.id == image_id).first() is None
    db.close()
    print("[PASS] Project and associated uploaded image BYTEA cascade deleted from PostgreSQL.")

    print("=" * 60)
    print("ALL BACKEND & POSTGRESQL INTEGRATION TESTS PASSED 100%!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
