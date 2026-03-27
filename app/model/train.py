"""
Training pipeline – handles:
  • Collecting active students from DB
  • Triggering VGG16 retraining
  • Saving model version metadata to DB
"""
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import Student, ModelVersion
from app.model.vgg_model import train as vgg_train

DATA_DIR = os.getenv("DATA_DIR", "data/students")
MODELS_DIR = os.getenv("MODELS_DIR", "saved_models")


def get_active_class_labels(db: Session) -> list[str]:
    """Return sorted list of reg_nos for all active students who have images."""
    students = (
        db.query(Student)
        .filter(Student.is_active == True, Student.sample_count >= 5)
        .order_by(Student.reg_no)
        .all()
    )
    return [s.reg_no for s in students]


def retrain(db: Session, fine_tune: bool = False) -> dict:
    """
    Full retrain pipeline called after any student add/remove.
    Returns result dict with accuracy & model path.
    """
    class_labels = get_active_class_labels(db)

    if len(class_labels) < 2:
        raise ValueError("Need at least 2 active students with ≥5 images each to train.")

    version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    print(f"[PIPELINE] Retraining v{version} with {len(class_labels)} classes...")
    result = vgg_train(
        data_dir=DATA_DIR,
        class_labels=class_labels,
        save_dir=MODELS_DIR,
        version=version,
        epochs=int(os.getenv("TRAIN_EPOCHS", "25")),
        fine_tune=fine_tune,
    )

    # Deactivate all previous versions
    db.query(ModelVersion).update({ModelVersion.is_active: False})

    # Record new version
    mv = ModelVersion(
        version=version,
        accuracy=result["accuracy"],
        num_classes=result["num_classes"],
        class_labels=json.dumps(result["class_labels"]),
        model_path=result["model_path"],
        is_active=True,
        notes=f"fine_tune={fine_tune}",
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)

    print(f"[PIPELINE] Done. Accuracy={result['accuracy']:.4f}  Model={result['model_path']}")
    return result


def get_active_model_info(db: Session) -> dict | None:
    """Return the currently active model version record as a dict."""
    mv = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
    if not mv:
        return None
    return {
        "version": mv.version,
        "accuracy": mv.accuracy,
        "num_classes": mv.num_classes,
        "class_labels": json.loads(mv.class_labels),
        "model_path": mv.model_path,
        "trained_at": mv.trained_at.isoformat(),
    }

