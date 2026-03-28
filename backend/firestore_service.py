import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# Initialize Firebase
if not firebase_admin.apps:
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    # For local development
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        import firebase_admin.db
        firebase_admin.initialize_app(options={'projectId': project_id})
    else:
        # For production - use service account from environment
        try:
            credential = credentials.ApplicationDefault()
            firebase_admin.initialize_app(credential, {'projectId': project_id})
        except Exception as e:
            print(f"Warning: Could not initialize Firebase with ApplicationDefault: {e}")

try:
    db = firestore.client()
except Exception as e:
    print(f"Warning: Could not get Firestore client: {e}")
    db = None

def save_student_embedding(student_id, name, embedding):
    """Save student with face embedding to Firestore"""
    if not db:
        return False
    try:
        db.collection("students").document(str(student_id)).set({
            "student_id": str(student_id),
            "name": name,
            "embedding": embedding,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        return True
    except Exception as e:
        print(f"Error saving student: {e}")
        return False

def get_student(student_id):
    """Get student from Firestore"""
    if not db:
        return None
    try:
        doc = db.collection("students").document(str(student_id)).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting student: {e}")
        return None

def get_all_students():
    """Get all students from Firestore"""
    if not db:
        return []
    try:
        docs = db.collection("students").stream()
        students = []
        for doc in docs:
            students.append(doc.to_dict())
        return students
    except Exception as e:
        print(f"Error getting students: {e}")
        return []

def log_attendance(student_id, student_name, subject, session_id=None):
    """Log attendance to Firestore"""
    if not db:
        return False
    try:
        db.collection("attendance").add({
            "student_id": str(student_id),
            "student_name": student_name,
            "subject": subject,
            "session_id": session_id,
            "timestamp": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        return True
    except Exception as e:
        print(f"Error logging attendance: {e}")
        return False

def get_attendance_records(subject=None, date=None):
    """Get attendance records from Firestore"""
    if not db:
        return []
    try:
        query = db.collection("attendance")
        if subject:
            query = query.where("subject", "==", subject)
        if date:
            query = query.where("date", "==", date)
        docs = query.stream()
        records = []
        for doc in docs:
            records.append(doc.to_dict())
        return records
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return []

def create_attendance_session(subject, teacher_id):
    """Create new attendance session"""
    if not db:
        return None
    try:
        session_ref = db.collection("attendance_sessions").add({
            "subject": subject,
            "teacher_id": teacher_id,
            "created_at": datetime.now(),
            "status": "active"
        })
        return session_ref[1].id
    except Exception as e:
        print(f"Error creating session: {e}")
        return None

def export_attendance_to_dict(subject, date=None):
    """Export attendance records as dictionary for CSV generation"""
    if not db:
        return []
    try:
        records = get_attendance_records(subject, date)
        return records
    except Exception as e:
        print(f"Error exporting attendance: {e}")
        return []
