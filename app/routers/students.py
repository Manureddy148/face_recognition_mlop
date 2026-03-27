"""
Student management endpoints:
  POST   /students/register          – register one student + upload face images
  POST   /students/register-bulk     – register multiple students at once
  GET    /students/                  – list all students
  GET    /students/{reg_no}          – get single student
  DELETE /students/{reg_no}          – deactivate student (soft delete)
  DELETE /students/{reg_no}/hard     – permanently remove student + images
  GET    /students/{reg_no}/samples  – count training images
"""
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.db import get_db
from app.database.models import Student
from app.utils.face_crop import save_student_face_samples, remove_student_images, count_student_samples
from app.model.train import retrain

router = APIRouter(prefix="/students", tags=["Students"])


class StudentInfo(BaseModel):
    reg_no: str
    name: str
    department: Optional[str] = ""
    email: Optional[str] = ""


@router.post("/register")
async def register_student(
    reg_no: str = Form(...),
    name: str = Form(...),
    department: str = Form(""),
    email: str = Form(""),
    images: list[UploadFile] = File(...),
    auto_train: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Register a student with face images. Pass auto_train=true to retrain immediately."""
    existing = db.query(Student).filter(Student.reg_no == reg_no).first()
    if existing and existing.is_active:
        raise HTTPException(400, f"Student {reg_no} already registered.")

    image_bytes_list = [await img.read() for img in images]
    saved = save_student_face_samples(reg_no, image_bytes_list)

    if saved < 5:
        raise HTTPException(400, f"Only {saved} valid face images found. Upload at least 5 clear photos.")

    if existing:
        existing.name = name
        existing.department = department
        existing.email = email
        existing.is_active = True
        existing.sample_count = saved
        db.commit()
    else:
        student = Student(
            reg_no=reg_no, name=name, department=department,
            email=email, image_dir=f"data/students/{reg_no}",
            sample_count=saved,
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    result = {
        "message": "Student registered successfully.",
        "reg_no": reg_no,
        "name": name,
        "samples_saved": saved,
        "auto_train": auto_train,
    }

    if auto_train:
        background_tasks.add_task(_bg_retrain, db)
        result["train_status"] = "Retraining started in background."

    return JSONResponse(result)


@router.post("/register-bulk")
async def register_bulk(
    students_json: str = Form(...),
    images: list[UploadFile] = File(...),
    auto_train: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    try:
        students_data = json.loads(students_json)
    except Exception:
        raise HTTPException(400, "Invalid students_json format.")

    results = []

    image_map: dict[str, list[bytes]] = {}
    for img in images:
        prefix = img.filename.split("_")[0] if "_" in img.filename else "shared"
        image_map.setdefault(prefix, []).append(await img.read())

    for sdata in students_data:
        reg_no = sdata.get("reg_no", "")
        name = sdata.get("name", "")
        if not reg_no or not name:
            results.append({"reg_no": reg_no, "status": "error", "reason": "Missing reg_no or name"})
            continue

        imgs = image_map.get(reg_no, [])
        if not imgs:
            results.append({"reg_no": reg_no, "status": "error", "reason": "No images found for this reg_no"})
            continue

        saved = save_student_face_samples(reg_no, imgs)
        existing = db.query(Student).filter(Student.reg_no == reg_no).first()
        if existing:
            existing.name = name
            existing.is_active = True
            existing.sample_count = saved
            db.commit()
        else:
            db.add(Student(
                reg_no=reg_no, name=name,
                department=sdata.get("department", ""),
                email=sdata.get("email", ""),
                image_dir=f"data/students/{reg_no}",
                sample_count=saved
            ))
            db.commit()

        results.append({"reg_no": reg_no, "name": name, "status": "ok", "samples": saved})

    if auto_train:
        background_tasks.add_task(_bg_retrain, db)

    return {"registered": results, "auto_train": auto_train}


@router.get("/")
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.is_active == True).offset(skip).limit(limit).all()
    return [
        {
            "reg_no": s.reg_no, "name": s.name,
            "department": s.department, "email": s.email,
            "sample_count": s.sample_count, "created_at": s.created_at,
        }
        for s in students
    ]


@router.get("/{reg_no}")
def get_student(reg_no: str, db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.reg_no == reg_no).first()
    if not s:
        raise HTTPException(404, "Student not found.")
    return s


@router.delete("/{reg_no}")
def deactivate_student(
    reg_no: str,
    auto_train: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    s = db.query(Student).filter(Student.reg_no == reg_no).first()
    if not s:
        raise HTTPException(404, "Student not found.")
    s.is_active = False
    db.commit()
    if auto_train:
        background_tasks.add_task(_bg_retrain, db)
    return {"message": f"Student {reg_no} deactivated.", "auto_train": auto_train}


@router.delete("/{reg_no}/hard")
def hard_delete_student(
    reg_no: str,
    auto_train: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    s = db.query(Student).filter(Student.reg_no == reg_no).first()
    if not s:
        raise HTTPException(404, "Student not found.")
    remove_student_images(reg_no)
    db.delete(s)
    db.commit()
    if auto_train:
        background_tasks.add_task(_bg_retrain, db)
    return {"message": f"Student {reg_no} permanently removed.", "auto_train": auto_train}


@router.get("/{reg_no}/samples")
def sample_count(reg_no: str):
    count = count_student_samples(reg_no)
    return {"reg_no": reg_no, "sample_count": count}


def _bg_retrain(db: Session):
    try:
        retrain(db)
    except Exception as e:
        print(f"[BG RETRAIN ERROR] {e}")

