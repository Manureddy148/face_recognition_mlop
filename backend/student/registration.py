from flask import Blueprint, request, jsonify, current_app
import time
import base64
import numpy as np
from PIL import Image
import io
import logging
from pymongo.errors import PyMongoError

student_registration_bp = Blueprint("student_registration", __name__)
logger = logging.getLogger(__name__)

def read_image_from_bytes(b):
    img = Image.open(io.BytesIO(b)).convert('RGB')
    return np.array(img)

def detect_faces_rgb(rgb_image, detector):
    detections = detector.detect_faces(rgb_image)
    faces = []
    img_h, img_w = rgb_image.shape[:2]
    for d in detections:
        if d['confidence'] > 0.85:
            x, y, w, h = d['box']
            if w <= 0 or h <= 0:
                continue

            # Clamp bounding box to image boundaries and skip invalid/empty crops.
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(img_w, x + w), min(img_h, y + h)
            crop_w, crop_h = x2 - x1, y2 - y1
            if crop_w > 40 and crop_h > 40:
                face_rgb = rgb_image[y1:y2, x1:x2]
                if face_rgb.size == 0:
                    continue
                faces.append({'box': (x1, y1, crop_w, crop_h), 'face': face_rgb, 'confidence': d['confidence']})
    return faces

def extract_embedding(face_rgb):
    try:
        face_pil = Image.fromarray(face_rgb.astype('uint8')).resize((160, 160))
        face_array = np.array(face_pil)
        from deepface import DeepFace

        rep = DeepFace.represent(
            face_array,
            model_name='Facenet512',
            detector_backend='skip',
            enforce_detection=False,
        )
        return np.array(rep[0]['embedding'], dtype=np.float32)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None

@student_registration_bp.route('/api/register-student', methods=['POST'])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON data"}), 400

    # Get logged-in user info from headers
    # Simplified: only validate fields and ensure uniqueness of studentId and email
    db = current_app.config.get("DB")
    model_manager = current_app.config.get("MODEL_MANAGER")
    if db is None:
        return jsonify({"success": False, "error": "Database unavailable"}), 503
    if not model_manager or not model_manager.is_ready():
        return jsonify({"success": False, "error": "Face models are not ready"}), 503

    detector = model_manager.get_detector()
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
    if not isinstance(images, list) or len(images) != 5:
        return jsonify({"success": False, "error": "Exactly 5 images are required"}), 400

    embeddings = []
    for idx, img_b64 in enumerate(images):
        try:
            if img_b64.startswith("data:"):
                img_b64 = img_b64.split(",", 1)[1]
            rgb = read_image_from_bytes(base64.b64decode(img_b64))
        except Exception:
            return jsonify({"success": False, "error": f"Invalid image data at index {idx}"}), 400

        faces = detect_faces_rgb(rgb, detector)
        if len(faces) != 1:
            return jsonify({"success": False, "error": f"Ensure exactly one face in each image (failed at image {idx+1})"}), 400

        emb = extract_embedding(faces[0]['face'])
        if emb is None:
            return jsonify({"success": False, "error": f"Failed to extract face features for image {idx+1}"}), 500
        embeddings.append(emb.tolist())

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
