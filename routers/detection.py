"""
Detection & Model endpoints:
  POST  /detect/image        – upload image for face recognition
  GET   /detect/logs         – get detection history
  POST  /model/train         – trigger retraining
  GET   /model/status        – current model info
  GET   /model/versions      – all model versions
"""
import io
import base64
import numpy as np
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import DetectionLog, ModelVersion
from app.model.predict import detect_faces, load_classifier
from app.model.train import retrain, get_active_model_info

detect_router = APIRouter(prefix="/detect", tags=["Detection"])
model_router  = APIRouter(prefix="/model",  tags=["Model"])


# ── Load model on first request ────────────────────────────────────────────────

def _ensure_model_loaded(db: Session):
    info = get_active_model_info(db)
    if not info:
        raise HTTPException(503, "No trained model available. Register students and train first.")

    labels_path = info["model_path"].replace(".keras", "").replace(
        "model_", "labels_"
    ) + ".json"
    # Derive labels path properly
    import os, json
    base = os.path.splitext(info["model_path"])[0]          # …/model_v20240101_120000
    labels_path = base.replace("model_v", "labels_v") + ".json"

    load_classifier(info["model_path"], labels_path, info["version"])
    return info


# ── Detect endpoint ────────────────────────────────────────────────────────────

@detect_router.post("/image")
async def detect_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a photo.  Returns JSON with all detected faces:
      reg_no, name, confidence (%), bounding box.
    Also returns base64-encoded annotated image.
    """
    _ensure_model_loaded(db)

    img_bytes = await image.read()
    if len(img_bytes) == 0:
        raise HTTPException(400, "Empty file uploaded.")

    try:
        result = detect_faces(img_bytes, db, source="upload")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    # Encode annotated image → base64 so frontend can display it
    _, buf = cv2.imencode(".jpg", result["annotated_image"])
    b64    = base64.b64encode(buf.tobytes()).decode("utf-8")

    return {
        "detections":    result["detections"],
        "total_faces":   result["total_faces"],
        "identified":    result["identified"],
        "annotated_image_b64": b64,
    }


@detect_router.get("/logs")
def detection_logs(
    skip: int = 0,
    limit: int = 50,
    reg_no: str = None,
    db: Session = Depends(get_db),
):
    """Paginated detection history, optionally filtered by reg_no."""
    q = db.query(DetectionLog)
    if reg_no:
        q = q.filter(DetectionLog.reg_no == reg_no)
    logs = q.order_by(DetectionLog.detected_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id":           l.id,
            "reg_no":       l.reg_no,
            "name":         l.student_name,
            "confidence":   round(l.confidence * 100, 2),
            "bbox":         {"x": l.bbox_x, "y": l.bbox_y, "w": l.bbox_w, "h": l.bbox_h},
            "source":       l.source,
            "detected_at":  l.detected_at.isoformat(),
        }
        for l in logs
    ]


# ── Model endpoints ────────────────────────────────────────────────────────────

@model_router.post("/train")
async def trigger_train(
    fine_tune: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Trigger retraining in background. Set fine_tune=true for better accuracy (slower)."""
    background_tasks.add_task(_bg_retrain, db, fine_tune)
    return {"message": "Training started in background.", "fine_tune": fine_tune}


@model_router.get("/status")
def model_status(db: Session = Depends(get_db)):
    info = get_active_model_info(db)
    if not info:
        return {"status": "no_model", "message": "No trained model yet."}
    return {"status": "ready", **info}


@model_router.get("/versions")
def model_versions(db: Session = Depends(get_db)):
    versions = db.query(ModelVersion).order_by(ModelVersion.trained_at.desc()).all()
    return [
        {
            "version":     v.version,
            "accuracy":    round(v.accuracy * 100, 2),
            "num_classes": v.num_classes,
            "is_active":   v.is_active,
            "trained_at":  v.trained_at.isoformat(),
            "notes":       v.notes,
        }
        for v in versions
    ]


def _bg_retrain(db: Session, fine_tune: bool = False):
    try:
        retrain(db, fine_tune=fine_tune)
        # Reload model after training
        info = get_active_model_info(db)
        if info:
            import os
            base = os.path.splitext(info["model_path"])[0]
            labels_path = base.replace("model_v", "labels_v") + ".json"
            load_classifier(info["model_path"], labels_path, info["version"])
    except Exception as e:
        print(f"[BG RETRAIN ERROR] {e}")
