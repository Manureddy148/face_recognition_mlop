from flask import Blueprint, request, jsonify, current_app
import time
import base64
import numpy as np
from PIL import Image
import io
import logging
import traceback
from pymongo.errors import PyMongoError

student_registration_bp = Blueprint("student_registration", __name__)
logger = logging.getLogger(__name__)


def read_image_rgb(img_b64: str) -> np.ndarray:
    """Decode a base64 image string (with or without data-URI prefix) to an RGB numpy array."""
    raw = img_b64.split(",", 1)[1] if img_b64.startswith("data:") else img_b64
    img = Image.open(io.BytesIO(base64.b64decode(raw))).convert('RGB')
    return np.array(img)


def embed_image(rgb: np.ndarray) -> tuple:
    """
    Return (embedding_array, strategy_name) or (None, error_string).

    Tries three strategies in order:
      1. DeepFace internal MTCNN detection + Facenet512  (enforce_detection=False
         so it falls back to the full frame when no face found)
      2. DeepFace skip-detection on full frame  (always produces an embedding)
      3. PIL resize to 160x160 then DeepFace skip  (explicit pre-resize path)
    Returns the first strategy that yields a finite 512-d vector.
    """
    from deepface import DeepFace

    errors: list[str] = []

    # --- Strategy 1: let DeepFace run MTCNN internally ---
    try:
        rep = DeepFace.represent(
            rgb,
            model_name='Facenet512',
            detector_backend='mtcnn',
            enforce_detection=False,
        )
        if rep:
            emb = np.array(rep[0]['embedding'], dtype=np.float32)
            if emb.shape == (512,) and np.isfinite(emb).all():
                logger.info("embed_image: strategy=mtcnn succeeded")
                return emb, 'mtcnn'
    except Exception as exc:
        msg = f"mtcnn: {exc}"
        errors.append(msg)
        logger.warning(f"embed_image {msg}")

    # --- Strategy 2: skip-detection on the full-size decoded array ---
    try:
        rep = DeepFace.represent(
            rgb,
            model_name='Facenet512',
            detector_backend='skip',
            enforce_detection=False,
        )
        if rep:
            emb = np.array(rep[0]['embedding'], dtype=np.float32)
            if emb.shape == (512,) and np.isfinite(emb).all():
                logger.info("embed_image: strategy=skip_full succeeded")
                return emb, 'skip_full'
    except Exception as exc:
        msg = f"skip_full: {exc}"
        errors.append(msg)
        logger.warning(f"embed_image {msg}")

    # --- Strategy 3: PIL pre-resize to 160x160 then skip ---
    try:
        arr160 = np.array(Image.fromarray(rgb.astype('uint8')).resize((160, 160)))
        rep = DeepFace.represent(
            arr160,
            model_name='Facenet512',
            detector_backend='skip',
            enforce_detection=False,
        )
        if rep:
            emb = np.array(rep[0]['embedding'], dtype=np.float32)
            if emb.shape == (512,) and np.isfinite(emb).all():
                logger.info("embed_image: strategy=skip_160 succeeded")
                return emb, 'skip_160'
    except Exception as exc:
        msg = f"skip_160: {exc}"
        errors.append(msg)
        logger.warning(f"embed_image {msg}")

    return None, "; ".join(errors) if errors else "unknown error"
@student_registration_bp.route('/api/register-student', methods=['POST'])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON data"}), 400

    db = current_app.config.get("DB")
    model_manager = current_app.config.get("MODEL_MANAGER")
    if db is None:
        return jsonify({"success": False, "error": "Database unavailable"}), 503
    if not model_manager or not model_manager.is_ready():
        deepface_error = getattr(model_manager, "deepface_error", None)
        return jsonify({
            "success": False,
            "error": "Face models are not ready",
            "details": deepface_error,
        }), 503

    students_col = db.students

    # Check required fields
    required_fields = ['studentName', 'studentId', 'department', 'year', 'division', 'semester', 'email', 'phoneNumber', 'images']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"{field} is required"}), 400

    # Check uniqueness of studentId and email
    if students_col.find_one({'studentId': data['studentId']}):
        return jsonify({"success": False, "error": "Student ID already exists"}), 400
    if students_col.find_one({'email': data['email']}):
        return jsonify({"success": False, "error": "Email already registered"}), 400

    # Validate images
    images = data.get('images')
    if not isinstance(images, list) or len(images) < 3:
        return jsonify({"success": False, "error": "At least 3 images are required"}), 400

    embeddings = []
    skipped = []
    decode_failed = 0
    embedding_failed = 0
    embed_errors: list[str] = []

    for idx, img_b64 in enumerate(images):
        # --- decode ---
        try:
            rgb = read_image_rgb(img_b64)
        except Exception as exc:
            logger.warning(f"Image {idx+1}: decode failed: {exc}")
            skipped.append(idx + 1)
            decode_failed += 1
            continue

        # --- embed (three-strategy cascade) ---
        emb, strategy = embed_image(rgb)
        if emb is None:
            logger.warning(f"Image {idx+1}: all embedding strategies failed: {strategy}")
            skipped.append(idx + 1)
            embedding_failed += 1
            embed_errors.append(f"img{idx+1}: {strategy}")
            continue

        logger.info(f"Image {idx+1}: embedding OK via {strategy}")
        embeddings.append(emb.tolist())

    if len(embeddings) < 3:
        return jsonify({
            "success": False,
            "error": f"Could not extract face features from enough images ({len(embeddings)}/{len(images)} succeeded). "
                     "Please ensure good lighting, face fully in frame, and try again.",
            "debug": {
                "decode_failed": decode_failed,
                "embedding_failed": embedding_failed,
                "accepted_embeddings": len(embeddings),
                "total_images": len(images),
                "errors": embed_errors,
            }
        }), 400


@student_registration_bp.route('/api/debug/embed-test', methods=['POST'])
def debug_embed_test():
    """Diagnostic: run the full embed pipeline on a single image and return results."""
    model_manager = current_app.config.get("MODEL_MANAGER")
    if not model_manager or not model_manager.is_ready():
        return jsonify({"ready": False, "deepface_error": getattr(model_manager, "deepface_error", "no manager")}), 503

    data = request.get_json() or {}
    img_b64 = data.get('image', '')
    if not img_b64:
        # If no image provided, run a synthetic test with a gray 640×480 image
        rgb = np.full((480, 640, 3), 128, dtype=np.uint8)
        img_b64 = None
    else:
        try:
            rgb = read_image_rgb(img_b64)
        except Exception as exc:
            return jsonify({"success": False, "error": f"decode failed: {exc}"}), 400

    emb, strategy = embed_image(rgb)
    return jsonify({
        "success": emb is not None,
        "strategy": strategy,
        "embedding_shape": list(emb.shape) if emb is not None else None,
        "embedding_sample": emb[:5].tolist() if emb is not None else None,
        "image_shape": list(rgb.shape),
        "image_dtype": str(rgb.dtype),
    })
    if skipped:
        logger.info(f"Registration: skipped images {skipped}, accepted {len(embeddings)} embeddings")

    student_data = {
        "studentId": data['studentId'],
        "studentName": data['studentName'],
        "department": data['department'],
        "year": data['year'],
        "division": data['division'],
        "semester": data['semester'],
        "email": data['email'],
        "phoneNumber": data['phoneNumber'],
        "status": "active",
        "embeddings": embeddings,
        "face_registered": True,
        "created_at": time.time(),
        "updated_at": time.time()
    }

    result = students_col.insert_one(student_data)
    return jsonify({"success": True, "studentId": data['studentId'], "record_id": str(result.inserted_id)})

@student_registration_bp.route('/api/students/count', methods=['GET'])
def get_student_count():
    db = current_app.config.get("DB")
    if db is None:
        return jsonify({"success": False, "error": "Database unavailable"}), 503
    try:
        return jsonify({"success": True, "count": db.students.count_documents({})})
    except PyMongoError as e:
        logger.error(f"Count query failed: {e}")
        return jsonify({"success": False, "error": "Database connection failed"}), 503

@student_registration_bp.route('/api/students/departments', methods=['GET'])
def get_departments():
    db = current_app.config.get("DB")
    if db is None:
        return jsonify({"success": False, "error": "Database unavailable"}), 503
    try:
        departments = db.students.distinct("department")
        return jsonify({"success": True, "departments": departments, "count": len(departments)})
    except PyMongoError as e:
        logger.error(f"Departments query failed: {e}")
        return jsonify({"success": False, "error": "Database connection failed"}), 503
