"""
Utility to process uploaded images for a student:
  - Detect face with MTCNN
  - Crop + resize to 224x224
  - Save as training sample
  - Returns count of valid faces found
"""
import os
import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image

DATA_DIR = os.getenv("DATA_DIR", "data/students")
_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        _detector = MTCNN(min_face_size=40)
    return _detector


def save_student_face_samples(
    reg_no: str,
    image_bytes_list: list[bytes],
    augment: bool = True,
) -> int:
    """
    Process a list of raw image bytes for one student.
    Detects the face in each, crops it, saves to data/students/{reg_no}/.
    Returns the number of valid face samples saved.
    """
    save_dir = os.path.join(DATA_DIR, reg_no)
    os.makedirs(save_dir, exist_ok=True)

    detector = _get_detector()
    saved = 0

    for idx, img_bytes in enumerate(image_bytes_list):
        nparr   = np.frombuffer(img_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = detector.detect_faces(img_rgb)

        if not results:
            # Try the whole image if MTCNN misses (for portrait uploads)
            face_rgb = cv2.resize(img_rgb, (224, 224))
        else:
            # Use the highest-confidence detection
            results.sort(key=lambda r: r["confidence"], reverse=True)
            x, y, w, h = results[0]["box"]
            x, y = max(0, x), max(0, y)
            face_rgb = img_rgb[y:y+h, x:x+w]
            face_rgb = cv2.resize(face_rgb, (224, 224))

        # Save original crop
        out_path = os.path.join(save_dir, f"{idx:04d}.jpg")
        Image.fromarray(face_rgb).save(out_path, quality=95)
        saved += 1

        # Light augmentation variants for small datasets
        if augment:
            # Horizontal flip
            flipped = np.fliplr(face_rgb)
            Image.fromarray(flipped).save(
                os.path.join(save_dir, f"{idx:04d}_flip.jpg"), quality=90
            )
            saved += 1

            # Slight brightness shift
            bright = np.clip(face_rgb.astype(np.int16) + 20, 0, 255).astype(np.uint8)
            Image.fromarray(bright).save(
                os.path.join(save_dir, f"{idx:04d}_bright.jpg"), quality=90
            )
            saved += 1

    return saved


def remove_student_images(reg_no: str) -> bool:
    """Delete all training images for a student."""
    import shutil
    student_dir = os.path.join(DATA_DIR, reg_no)
    if os.path.exists(student_dir):
        shutil.rmtree(student_dir)
        return True
    return False


def count_student_samples(reg_no: str) -> int:
    """Return how many training images exist for a student."""
    student_dir = os.path.join(DATA_DIR, reg_no)
    if not os.path.exists(student_dir):
        return 0
    return len([f for f in os.listdir(student_dir) if f.endswith(".jpg")])
