# app.py - OPTIMIZED VERSION
import os
import time
import logging
import threading
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import numpy as np

# Blueprint imports
from auth.routes import auth_bp

# Optional student/teacher blueprints
try:
    from student.registration import student_registration_bp
except ImportError:
    student_registration_bp = None

try:
    from student.updatedetails import student_update_bp
except ImportError:
    student_update_bp = None

try:
    from student.demo_session import demo_session_bp
except ImportError:
    demo_session_bp = None

try:
    from student.view_attendance import attendance_bp
except ImportError:
    attendance_bp = None

try:
    from teacher.attendance_records import attendance_session_bp
except ImportError:
    attendance_session_bp = None

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb://localhost:27017/"
DB_NAME = os.getenv("DATABASE_NAME", "facerecognition")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "students")
THRESHOLD = float(os.getenv("THRESHOLD", "0.6"))

client = None
db = None
students_collection = None
attendance_collection = None

try:
    # Use shorter timeouts so DB failures do not block API responses for long periods.
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    # Force initial connectivity check during startup.
    client.admin.command("ping")
    db = client[DB_NAME]
    students_collection = db[COLLECTION_NAME]
    attendance_db = client["facerecognition_db"]
    attendance_collection = attendance_db["attendance_records"]
except PyMongoError as e:
    logger.error(f"MongoDB initialization failed: {e}")
    client = None
    db = None
    students_collection = None
    attendance_collection = None

# OPTIMIZED MODEL MANAGER CLASS
class ModelManager:
    """
    Singleton class to manage face recognition models
    Ensures models are loaded only once and shared across all requests
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        """Initialize all face recognition models with proper error handling"""
        logger.info("Starting model initialization...")
        start_time = time.time()

        self.models_ready = False
        self.detector = None
        self.deepface_ready = False
        self.initialization_error = None

        try:
            # 1. Initialize MTCNN detector with optimized parameters
            from mtcnn import MTCNN
            logger.info("Loading MTCNN detector...")
            self.detector = MTCNN()
            logger.info("MTCNN detector loaded successfully")

            # 2. Validate DeepFace import only. Do not warm models at startup,
            # because weight downloads can fail in cold-start environments.
            from deepface import DeepFace
            self.deepface_ready = True
            logger.info("DeepFace import validation successful")

            self.models_ready = True

            initialization_time = time.time() - start_time
            logger.info(f"Model initialization completed in {initialization_time:.2f} seconds")

        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"Model initialization failed: {e}")
            self.models_ready = False
            self.deepface_ready = False

    def get_detector(self):
        """Get the MTCNN detector instance"""
        if self.detector is None:
            raise RuntimeError(self.initialization_error or "MTCNN detector not initialized")
        return self.detector

    def is_ready(self):
        """Check if all models are ready"""
        return self.models_ready and self.deepface_ready

    def health_check(self):
        """Perform model health check"""
        try:
            if self.detector is None:
                return False

            # Test MTCNN
            test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            _ = self.detector.detect_faces(test_img)

            return True

        except Exception as e:
            logger.error(f"Model health check failed: {e}")
            return False

# Initialize the model manager (singleton)
logger.info("Initializing Model Manager...")
model_manager = ModelManager()

# Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask app with database and model instances
app.config["DB"] = db
app.config["COLLECTION_NAME"] = COLLECTION_NAME
app.config["THRESHOLD"] = THRESHOLD
app.config["ATTENDANCE_COLLECTION"] = attendance_collection

# CRITICAL: Pass model manager to Flask config so blueprints can access it
app.config["MODEL_MANAGER"] = model_manager
app.config["MTCNN_DETECTOR"] = model_manager.detector

bcrypt = Bcrypt(app)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify model status"""
    model_status = model_manager.is_ready()
    model_health = model_manager.health_check()
    db_connected = False
    if client is not None:
        try:
            client.admin.command("ping")
            db_connected = True
        except PyMongoError:
            db_connected = False

    is_healthy = model_status and model_health and db_connected

    payload = {
        "status": "healthy" if is_healthy else "unhealthy",
        "models_ready": model_status,
        "models_healthy": model_health,
        "db_connected": db_connected,
        "initialization_error": model_manager.initialization_error,
        "timestamp": time.time()
    }
    return payload, (200 if is_healthy else 503)

# Register blueprints
app.register_blueprint(auth_bp)

if student_registration_bp:
    app.register_blueprint(student_registration_bp)
    logger.info("✅ Student registration blueprint registered")

if student_update_bp:
    app.register_blueprint(student_update_bp)
    logger.info("✅ Student update blueprint registered")

if demo_session_bp:
    app.register_blueprint(demo_session_bp)
    logger.info("✅ Demo session blueprint registered")

if attendance_bp:
    app.register_blueprint(attendance_bp)
    logger.info("✅ Attendance blueprint registered")

if attendance_session_bp:
    app.register_blueprint(attendance_session_bp)
    logger.info("✅ Attendance session blueprint registered")

# List all registered routes
logger.info("\nRegistered Flask Routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule}")

if __name__ == "__main__":
    logger.info("Starting Flask server...")

    if not model_manager.is_ready():
        logger.warning("Starting in degraded mode: model manager is not fully ready")
    app.run(host="0.0.0.0", port=5000, debug=False)