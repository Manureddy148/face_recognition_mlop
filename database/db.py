"""
Database setup using SQLAlchemy with SQLite (swappable to PostgreSQL via env var).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./face_recognition.db")

# SQLite needs check_same_thread=False; ignored for other DBs
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.database.models import Student, DetectionLog  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("[DB] Tables created/verified.")
