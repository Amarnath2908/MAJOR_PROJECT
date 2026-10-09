# DesignVerse AI

An AI-powered interior/exterior design platform. Upload a room image, detect objects with GroundingDINO + SAM, edit via natural language prompts, and generate 3D models.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, TanStack Query, Zustand, Three.js |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Uvicorn |
| AI | GroundingDINO (object detection), SAM ViT-B (segmentation) |

## Project Structure

```
project_folder/
├── backend/          # FastAPI backend
├── frontend/         # React + Vite frontend
├── models/           # AI weight files (git-ignored, see below)
├── scripts/          # Developer utilities
│   └── download_models.py
└── README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd project_folder
```

### 2. Download AI model weights

> Model files are **not stored in git** (too large). Download them with:

```bash
python scripts/download_models.py
```

This downloads (~1 GB total) into `models/`:
- `models/grounding_dino/groundingdino_swint_ogc.pth` (~694 MB)
- `models/sam/sam_vit_b_01ec64.pth` (~375 MB)

### 3. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install GroundingDINO (requires C++ build tools)
pip install --no-build-isolation git+https://github.com/IDEA-Research/GroundingDINO.git

# Install SAM
pip install git+https://github.com/facebookresearch/segment-anything.git

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, and AI model paths
```

### 4. Database Setup

Make sure PostgreSQL is running, then create the database:

```sql
CREATE DATABASE designverse;
```

The backend will create all tables automatically on first startup.

### 5. Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env
# Edit .env — set VITE_API_URL=http://localhost:8000
```

### 6. Run the application

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins for CORS |
| `GROUNDING_DINO_CONFIG_PATH` | Path to GroundingDINO config `.py` file |
| `GROUNDING_DINO_CHECKPOINT_PATH` | Path to `groundingdino_swint_ogc.pth` |
| `SAM_CHECKPOINT_PATH` | Path to `sam_vit_b_01ec64.pth` |
| `DEVICE` | `cpu` or `cuda` |

See [`backend/.env.example`](backend/.env.example) for the full template.

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL (e.g., `http://localhost:8000`) |

See [`frontend/.env.example`](frontend/.env.example) for the template.

## API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Notes

- The AI pipeline (GroundingDINO + SAM) requires **at least 4 GB of RAM** on CPU mode (8 GB recommended).
- Model inference is slow on CPU. Set `DEVICE=cuda` if you have an NVIDIA GPU with CUDA installed.
