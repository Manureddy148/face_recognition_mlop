"""
Face Recognition MLOps System — FastAPI App
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.db import init_db, get_db, SessionLocal
from app.model.train import get_active_model_info
from app.model.predict import load_classifier
from app.routers.students import router as students_router
from app.routers.detection import detect_router, model_router


# ── Startup / Shutdown ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[APP] Starting up...")
    init_db()

    # Auto-load the most recent trained model
    db = SessionLocal()
    try:
        info = get_active_model_info(db)
        if info:
            base        = os.path.splitext(info["model_path"])[0]
            labels_path = base.replace("model_v", "labels_v") + ".json"
            if os.path.exists(info["model_path"]) and os.path.exists(labels_path):
                load_classifier(info["model_path"], labels_path, info["version"])
                print(f"[APP] Model v{info['version']} loaded. Classes: {info['num_classes']}")
            else:
                print("[APP] Model files not found — train the model first.")
        else:
            print("[APP] No trained model found — register students and train.")
    finally:
        db.close()

    yield
    print("[APP] Shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Face Recognition MLOps",
    description="Student face detection & identification system with VGG16",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
if os.path.exists("frontend"):
    app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# Routers
app.include_router(students_router)
app.include_router(detect_router)
app.include_router(model_router)


@app.get("/")
def root():
    return {
        "service": "Face Recognition MLOps",
        "docs":    "/docs",
        "ui":      "/ui",
        "status":  "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
