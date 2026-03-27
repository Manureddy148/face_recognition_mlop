"""
ORM models for Students and Detection Logs.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.database.db import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    reg_no = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), default="")
    email = Column(String(150), default="")
    image_dir = Column(String(255), default="")   # path to their training images
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sample_count = Column(Integer, default=0)      # number of training images

    def __repr__(self):
        return f"<Student reg={self.reg_no} name={self.name}>"


class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    reg_no = Column(String(50), index=True, nullable=False)
    student_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    image_path = Column(String(255), default="")   # snapshot saved on detect
    bbox_x = Column(Integer, default=0)
    bbox_y = Column(Integer, default=0)
    bbox_w = Column(Integer, default=0)
    bbox_h = Column(Integer, default=0)
    detected_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), default="upload")  # upload | webcam | stream

    def __repr__(self):
        return f"<DetectionLog reg={self.reg_no} conf={self.confidence:.2f}>"


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    accuracy = Column(Float, default=0.0)
    num_classes = Column(Integer, default=0)
    class_labels = Column(Text, default="")         # JSON list of reg_nos
    model_path = Column(String(255), default="")
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, default="")

    def __repr__(self):
        return f"<ModelVersion v={self.version} acc={self.accuracy:.2f}>"

