"""
view_db.py - Helper script to quickly view PostgreSQL database contents.
"""
from database.database import SessionLocal
from database.models import User, UploadedImage, Project

db = SessionLocal()
try:
    print("=" * 60)
    print(" DESIGNVERSE AI - POSTGRESQL DATABASE INSPECTOR")
    print("=" * 60)

    users = db.query(User).all()
    print(f"\n[*] USERS ({len(users)}):")
    for u in users:
        print(f"  - ID: {u.id} | Username: {u.username} | Email: {u.email}")

    images = db.query(UploadedImage).all()
    print(f"\n[*] UPLOADED IMAGES (BYTEA STORED) ({len(images)}):")
    for img in images:
        size_kb = len(img.image_data) / 1024.0 if img.image_data else 0.0
        print(f"  - ID: {img.id}")
        print(f"    File: {img.original_filename} ({img.mime_type})")
        print(f"    BYTEA Size in DB: {size_kb:.2f} KB | Dimensions: {img.width}x{img.height}")

    projects = db.query(Project).all()
    print(f"\n[*] PROJECTS ({len(projects)}):")
    for p in projects:
        print(f"  - ID: {p.id}")
        print(f"    Title: {p.title} | Status: {p.status}")
        print(f"    Prompt: {p.prompt}")
        print(f"    Target: {p.target_object} | 3D: {p.model_3d_path}")

    print("\n" + "=" * 60)
finally:
    db.close()
