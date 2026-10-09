# DesignVerse AI — Backend

> **AI-powered interior & exterior design platform**
> Upload a room image → Analyse objects → Edit with natural language → Generate a 3D model.

---

## 🏗️ Architecture Overview

```
backend/
├── main.py                   ← FastAPI app factory + Uvicorn entry point
├── config.py                 ← All settings loaded from .env (Pydantic BaseSettings)
├── requirements.txt          ← Python dependencies
├── .env                      ← Environment variables (copy & fill before running)
│
├── api/                      ← HTTP route handlers (thin — no business logic)
│   ├── auth.py               ← POST /auth/register | login | GET /auth/me | POST /auth/logout
│   ├── upload.py             ← POST /upload/ | GET /upload/{image_id}
│   ├── analysis.py           ← POST /analysis/
│   ├── editor.py             ← POST /editor/edit
│   ├── viewer.py             ← POST /viewer/generate3d
│   └── history.py            ← GET /history/ | GET /history/{id} | DELETE /history/{id}
│
├── services/                 ← Business logic layer
│   ├── auth_service.py       ← Password hashing, JWT, register, login
│   ├── upload_service.py     ← File validation, Pillow, DB record creation
│   ├── analysis_service.py   ← Image analysis pipeline (mock → real AI)
│   ├── editor_service.py     ← Prompt-based editing pipeline (mock → real AI)
│   ├── viewer_service.py     ← 3D generation pipeline (mock → real AI)
│   └── history_service.py    ← Paginated project history, delete
│
├── ai/                       ← AI module interfaces (ALL MOCK at this stage)
│   ├── grounding_dino.py     ← Object detection placeholder → Grounding DINO
│   ├── sam.py                ← Segmentation placeholder → SAM
│   ├── image_editor.py       ← Editing placeholder → Stable Diffusion / FLUX
│   ├── depth_estimation.py   ← Depth map placeholder → Depth Anything V2
│   └── mesh_generator.py     ← 3D mesh placeholder → InstantMesh
│
├── database/
│   ├── database.py           ← SQLAlchemy engine, session factory, Base, get_db()
│   └── models.py             ← User, UploadedImage, Project ORM tables
│
├── schemas/
│   ├── auth_schema.py        ← Register/login request & token response schemas
│   ├── upload_schema.py      ← Upload request & image metadata schemas
│   ├── prompt_schema.py      ← Analysis, Edit, Generate3D request/response schemas
│   └── response_schema.py    ← Generic success/error envelopes, history schemas
│
├── middleware/
│   ├── auth.py               ← JWT Bearer authentication dependency (get_current_user)
│   └── exception_handler.py  ← Global 401/404/422/500 error handlers
│
├── utils/
│   ├── logger.py             ← Centralised logging factory (get_logger)
│   ├── file_utils.py         ← File storage abstraction (save, delete, get)
│   └── helpers.py            ← UUID, datetime, pagination, masking utilities
│
└── storage/
    ├── uploads/              ← Original user-uploaded images
    ├── edited/               ← AI-edited output images
    ├── masks/                ← SAM segmentation masks
    ├── depth/                ← Depth Anything depth maps
    ├── models3d/             ← Generated .glb 3D models
    └── thumbnails/           ← Project preview thumbnails
```

---

## 🚀 Quick Start

### 1. Create & activate a virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

The `.env` file is pre-filled with development defaults. For production, update:

```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:///./database/designverse.db
```

### 4. Start the server

```bash
# Method 1 — direct Python
python main.py

# Method 2 — Uvicorn CLI (recommended for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open API docs

| Interface | URL |
|-----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | ❌ | Register a new account |
| `POST` | `/auth/login` | ❌ | Login — returns JWT |
| `GET` | `/auth/me` | ✅ | Get current user profile |
| `POST` | `/auth/logout` | ✅ | Logout placeholder |

### Upload

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/upload/` | ✅ | Upload an image (max 20 MB) |
| `GET` | `/upload/{image_id}` | ✅ | Get image metadata |

### Analysis (Mock)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/analysis/` | ✅ | Detect objects in an image |

**Request:**
```json
{ "image_id": "<uuid>" }
```
**Response:**
```json
{
  "image_id": "<uuid>",
  "objects": ["Wall", "Window", "Floor", "Sofa", "Coffee Table"],
  "status": "success"
}
```

### Editor (Mock)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/editor/edit` | ✅ | Edit image with a text prompt |

**Request:**
```json
{ "image_id": "<uuid>", "prompt": "Change the sofa to dark navy blue" }
```
**Response:**
```json
{
  "project_id": "<uuid>",
  "edited_image": "storage/edited/sample.png",
  "status": "success"
}
```

### 3D Viewer (Mock)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/viewer/generate3d` | ✅ | Generate a .glb 3D model |

**Request:**
```json
{ "project_id": "<uuid>" }
```
**Response:**
```json
{
  "project_id": "<uuid>",
  "model": "storage/models3d/sample.glb",
  "status": "success"
}
```

### History

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/history/` | ✅ | Get paginated project list |
| `GET` | `/history/{project_id}` | ✅ | Get single project detail |
| `DELETE` | `/history/{project_id}` | ✅ | Delete a project |

---

## 🔐 Authentication Flow

```
1. POST /auth/register  →  { "access_token": "eyJ..." }
2. POST /auth/login     →  { "access_token": "eyJ..." }
3. All protected routes: Authorization: Bearer eyJ...
```

---

## 🤖 AI Integration Guide

The `ai/` module contains **interface-only placeholder classes**.  
When integrating a real model, only that class's file changes — nothing else in the codebase needs modification.

| File | Replace When | Model |
|------|-------------|-------|
| `ai/grounding_dino.py` | Object detection phase | Grounding DINO |
| `ai/sam.py` | Segmentation phase | SAM (ViT-H) |
| `ai/image_editor.py` | Image editing phase | Stable Diffusion / FLUX |
| `ai/depth_estimation.py` | 3D prep phase | Depth Anything V2 |
| `ai/mesh_generator.py` | 3D generation phase | InstantMesh |

**Integration pattern:**
```python
# Before (mock):
def detect(self, image: str) -> List[str]:
    return ["Wall", "Sofa", "Window"]   # mock

# After (real):
def detect(self, image: str) -> List[str]:
    model = load_model(config, checkpoint)
    boxes, logits, phrases = predict(model, image, text_prompt)
    return phrases
```

---

## 🗄️ Database Schema

```
users
  id (UUID PK) | username | email | hashed_password | full_name
  is_active | is_verified | created_at | updated_at

uploaded_images
  id (UUID PK) | user_id (FK→users) | original_filename | stored_filename
  file_path | file_size_mb | mime_type | width | height | status | created_at

projects
  id (UUID PK) | user_id (FK→users) | image_id (FK→uploaded_images)
  title | prompt | analysis_result (JSON) | edited_image_path
  model_3d_path | thumbnail_path | status | created_at | updated_at
```

---

## 🧪 Testing the API

Use the Swagger UI at `http://localhost:8000/docs` or cURL:

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test1234!"}'

# 2. Upload image (use the token from step 1)
curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/room.jpg"

# 3. Analyse
curl -X POST http://localhost:8000/analysis/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"image_id":"<image_id_from_step_2>"}'

# 4. Edit
curl -X POST http://localhost:8000/editor/edit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"image_id":"<image_id>","prompt":"Paint the walls light grey"}'

# 5. Generate 3D
curl -X POST http://localhost:8000/viewer/generate3d \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"project_id":"<project_id_from_step_4>"}'

# 6. View history
curl http://localhost:8000/history/ \
  -H "Authorization: Bearer <token>"
```

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI 0.111 |
| Server | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Image Processing | Pillow + OpenCV |
| Configuration | python-dotenv + pydantic-settings |

---

*Built with ❤️ for DesignVerse AI — Final Year Project*
