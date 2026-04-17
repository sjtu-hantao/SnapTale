# SnapTale

SnapTale is an agent-native social storytelling MVP.

This repository focuses on three core abilities:

- one-click social post generation from a photo set
- adaptive voice tuning through feedback
- long-term growth tracking through memory retrieval

The current implementation is a rebuilt MVP based on the original SnapTale idea. It does not aim to reproduce the full hardware plus journaling system. Instead, it keeps the product scope tight around multimodal understanding, personalized writing, and memory-enhanced generation.

## Demo Goals

This MVP is designed to demonstrate:

1. A user uploads 2-8 photos as one collection.
2. The agent analyzes the collection and infers a story arc.
3. The system generates multiple social post variants in different voices.
4. The user gives feedback through like, dislike, select, and rewrite actions.
5. The system updates prompt memory and retrieves relevant past memories in future generations.

## Current Features

### 1. One-click social content generation

- Upload a photo collection from the web UI.
- Analyze each image with either a real ARK OpenAI-compatible multimodal model or a local heuristic fallback.
- Generate a story summary, narrative arc, emotional tone, and four candidate social posts.

Current writing styles:

- `Storyteller`
- `Warm Diary`
- `Growth Reflection`
- `Playful Lifestyle`

### 2. Adaptive user personalization

- Capture feedback signals: `like`, `dislike`, `select`, `rewrite`
- Store user preference memory: style weights, top tags, voice notes, exemplar rewrites
- Use these signals in subsequent generations to adjust prompt context and preferred writing style

### 3. Growth tracking and lightweight RAG

- Store each generated collection as a structured long-term memory item
- Retrieve related memories using token overlap, memory strength, and recency bonus
- Visualize growth data in the frontend: collection count, memory count, feedback count, timeline of memories, current prompt memory summary

## Architecture

### Backend

- FastAPI
- SQLModel / SQLAlchemy
- SQLite for local MVP storage
- local media storage for uploaded files
- ARK OpenAI-compatible model provider for image and text generation

### Frontend

- React 18
- TypeScript
- Ant Design
- Axios

## Generation Pipeline

The current `/api/mvp/generate` flow is:

1. Bootstrap or load the user profile.
2. Store uploaded photos locally.
3. Analyze each photo.
4. Retrieve related memories.
5. Build a collection-level story summary.
6. Generate multiple post candidates.
7. Store collection, assets, posts, and memory items.
8. Return generation metadata to the UI.

The frontend shows whether the current result came from:

- full LLM generation
- mixed mode
- heuristic fallback

## Project Structure

```text
SnapTale/
- backend/      FastAPI app, database models, generation pipeline
- frontend/     React app for Create + Growth views
- firmware/     Optional hardware-related area kept from the original project context
- scripts/      Windows startup helpers
- README.md
- GITHUB_UPLOAD.md
```

## Main Backend Modules

- `backend/app/api/mvp.py`
  API routes for bootstrap, generate, feedback, and growth
- `backend/app/api/mvp_service.py`
  Main product logic: upload pipeline, memory retrieval, feedback adaptation
- `backend/app/api/model_provider.py`
  ARK OpenAI-compatible model calls and fallback handling
- `backend/database/database.py`
  SQLModel schemas and database initialization

## Data Model

The MVP mainly revolves around these tables:

- `UserPreference`
- `PhotoCollection`
- `CollectionAsset`
- `GeneratedPost`
- `FeedbackEvent`
- `MemoryItem`

These tables power the full loop of generation, personalization, and growth tracking.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd SnapTale
```

### 2. Backend dependencies

Install backend dependencies into `backend/pydeps`:

```powershell
python -m pip install fastapi uvicorn sqlmodel sqlalchemy python-dotenv python-multipart pillow --target backend\pydeps
```

You may also install from `backend/requirements.txt`, but the MVP startup scripts expect `backend/pydeps` to exist.

### 3. Frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

### 4. Configure the model provider

Create `backend/.env` from `backend/.env.example` and configure ARK:

```powershell
MODEL_PROVIDER=auto
ARK_API_KEY=your-api-key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=your-ark-model-or-endpoint-id
MODEL_TIMEOUT_SECONDS=90
```

Notes:

- If one ARK model handles both image and text, `ARK_MODEL` is enough.
- If you want separate models, use `ARK_VISION_MODEL` and `ARK_TEXT_MODEL`.
- If no valid key or model is present, the app falls back to the local heuristic pipeline.

### 5. Start the backend

```powershell
.\scripts\start_backend.cmd
```

If you prefer PowerShell directly:

```powershell
.\scripts\start_backend.ps1
```

### 6. Start the frontend

```powershell
.\scripts\start_frontend.cmd -NoBrowser
```

Then open:

- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:8000`

## API Endpoints

- `POST /api/mvp/bootstrap`
- `POST /api/mvp/generate`
- `POST /api/mvp/posts/{post_id}/feedback`
- `GET /api/mvp/users/{user_id}/growth`

## Current Limitations

- The current "RAG" implementation is lightweight memory retrieval, not a vector-database pipeline yet.
- The current "RLHF" implementation is an application-level feedback loop, not parameter-level policy optimization.
- The repository still contains `firmware/`, but the current MVP centers on the web-based social storytelling workflow.

## Why This Repo Exists

This version is intentionally scoped for fast iteration and demo clarity. It is meant to show how an agent system can connect:

- multimodal input
- structured memory
- adaptive prompts
- personalized copy generation

into one coherent product loop.

## Publishing Note

This repository is now organized as a single monorepo for easier sharing on GitHub.

If you want a final pre-push checklist, see [GITHUB_UPLOAD.md](./GITHUB_UPLOAD.md).
