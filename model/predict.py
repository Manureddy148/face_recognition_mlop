"""
Inference engine:
  1. Detect faces in image using MTCNN
  2. Crop + preprocess each face
  3. Run VGG16 classifier
  4. Return bounding boxes + name + reg_no + confidence
  5. Log results to DB
"""
import os
import json
import uuid
import numpy as np
import cv2
from datetime import datetime
from pathlib import Path

import tensorflow as tf
from mtcnn import MTCNN
from sqlalchemy.orm import Session

from app.database.models import Student, DetectionLog

MODELS_DIR   = os.getenv("MODELS_DIR", "saved_models")
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "data/snapshots")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))

os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# ── Singletons (loaded once) ──────────────────────────────────────────────────
_detector   = None
_classifier = None
_labels     = None
_model_ver  = None


def _get_detector() -> MTCNN:
    global _detector
    if _detector is None:
        _detector = MTCNN(min_face_size=40)
    return _detector


def load_classifier(model_path: str, labels_path: str, version: str):
    """Load (or reload) the VGG16 classifier."""
    global _classifier, _labels, _model_ver
    if _model_ver == version:
        return  # already loaded
    print(f"[PREDICT] Loading model v{version} from {model_path}")
    _classifier = tf.keras.models.load_model(model_path)
    with open(labels_path) as f:
        _labels = json.load(f)
    _model_ver = version
    print(f"[PREDICT] Ready. Classes: {_labels}")


# ── Image helpers ─────────────────────────────────────────────────────────────

def _preprocess_face(face_bgr: np.ndarray) -> np.ndarray:
    """Resize, normalise, add batch dim."""
    face_rgb  = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    face_resized = cv2.resize(face_rgb, (224, 224))
    face_norm = face_resized.astype("float32") / 255.0
    return np.expand_dims(face_norm, axis=0)


def _expand_bbox(x, y, w, h, margin: float, img_h: int, img_w: int):
    """Add a margin around the MTCNN bounding box for a tighter crop."""
    mx = int(w * margin)
    my = int(h * margin)
    x1 = max(0, x - mx)
    y1 = max(0, y - my)
    x2 = min(img_w, x + w + mx)
    y2 = min(img_h, y + h + my)
    return x1, y1, x2 - x1, y2 - y1


# ── Core detect function ──────────────────────────────────────────────────────

def detect_faces(
    image_bytes: bytes,
    db: Session,
    source: str = "upload",
    save_snapshot: bool = True,
) -> dict:
    """
    Detect and identify all faces in the provided image bytes.

    Returns:
        {
          "detections": [
            {
              "reg_no": str,
              "name": str,
              "confidence": float,
              "bbox": {"x": int, "y": int, "w": int, "h": int},
              "unknown": bool,
            }, ...
          ],
          "total_faces": int,
          "identified": int,
          "snapshot_path": str | None,
        }
    """
    if _classifier is None or _labels is None:
        raise RuntimeError("Model not loaded. Train the model first.")

    # Decode image
    nparr  = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Could not decode image.")
    img_h, img_w = img_bgr.shape[:2]

    detector = _get_detector()
    img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    faces    = detector.detect_faces(img_rgb)

    detections      = []
    annotated_img   = img_bgr.copy()

    for face in faces:
        x, y, w, h = face["box"]
        x, y, w, h = _expand_bbox(x, y, w, h, margin=0.1, img_h=img_h, img_w=img_w)

        # Skip tiny detections
        if w < 30 or h < 30:
            continue

        crop  = img_bgr[y:y+h, x:x+w]
        inp   = _preprocess_face(crop)
        preds = _classifier.predict(inp, verbose=0)[0]

        top_idx   = int(np.argmax(preds))
        confidence = float(preds[top_idx])
        reg_no    = _labels[top_idx]
        unknown   = confidence < CONFIDENCE_THRESHOLD

        # Fetch student info
        student = db.query(Student).filter(Student.reg_no == reg_no).first()
        name    = student.name if (student and not unknown) else "Unknown"
        reg_no_display = reg_no if not unknown else "N/A"

        det = {
            "reg_no":     reg_no_display,
            "name":       name,
            "confidence": round(confidence * 100, 2),
            "bbox":       {"x": x, "y": y, "w": w, "h": h},
            "unknown":    unknown,
        }
        detections.append(det)

        # ── Annotate image ────────────────────
        color  = (0, 200, 50) if not unknown else (0, 60, 220)
        label1 = f"{name}" if not unknown else "Unknown"
        label2 = f"{reg_no_display}  {confidence*100:.1f}%"

        cv2.rectangle(annotated_img, (x, y), (x+w, y+h), color, 2)
        # Background bar for text
        cv2.rectangle(annotated_img, (x, y-45), (x+w, y), color, -1)
        cv2.putText(annotated_img, label1, (x+4, y-26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        cv2.putText(annotated_img, label2, (x+4, y-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        # ── Log to DB ─────────────────────────
        if not unknown and student:
            log = DetectionLog(
                reg_no=reg_no,
                student_name=name,
                confidence=confidence,
                bbox_x=x, bbox_y=y, bbox_w=w, bbox_h=h,
                source=source,
            )
            db.add(log)

    db.commit()

    # ── Save annotated snapshot ───────────────
    snapshot_path = None
    if save_snapshot and len(detections) > 0:
        fname = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
        snapshot_path = os.path.join(SNAPSHOT_DIR, fname)
        cv2.imwrite(snapshot_path, annotated_img)

        # Update log with snapshot path
        db.query(DetectionLog).filter(
            DetectionLog.image_path == "",
            DetectionLog.source == source,
        ).update({DetectionLog.image_path: snapshot_path})
        db.commit()

    identified = sum(1 for d in detections if not d["unknown"])

    return {
        "detections":   detections,
        "total_faces":  len(faces),
        "identified":   identified,
        "snapshot_path": snapshot_path,
        "annotated_image": annotated_img,
    }
