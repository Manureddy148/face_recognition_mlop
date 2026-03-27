# 🎓 FaceID — Student Face Recognition MLOps System

VGG16-based student face detection and recognition with FastAPI, SQLite, and Azure deployment.

---

## 📁 Project Structure
```
face_recognition/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── model/
│   │   ├── vgg_model.py         # VGG16 transfer learning architecture
│   │   ├── train.py             # Training pipeline + model versioning
│   │   └── predict.py           # MTCNN detection + VGG16 inference
│   ├── database/
│   │   ├── db.py                # SQLAlchemy setup
│   │   └── models.py            # Student, DetectionLog, ModelVersion tables
│   ├── utils/
│   │   └── face_crop.py         # Image preprocessing + augmentation
│   └── routers/
│       ├── students.py          # Student CRUD endpoints
│       └── detection.py         # Detection + model endpoints
├── data/
│   └── students/{reg_no}/       # Training images per student
├── saved_models/                # Versioned .keras model files
├── frontend/index.html          # Dashboard UI
├── Dockerfile
├── docker-compose.yml
├── deploy_azure.sh              # One-command Azure deployment
└── requirements.txt
```

---

## ⚡ Quick Start (Local)

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open the UI
```
http://localhost:8000/ui
```

### 4. API Docs (Swagger)
```
http://localhost:8000/docs
```

---

## 🐳 Docker (Recommended)

```bash
docker-compose up --build
```

---

## 🔄 MLOps Workflow

### Step 1 — Register students
Upload 10-20 photos per student via UI or API:

```bash
curl -X POST http://localhost:8000/students/register \
  -F "reg_no=CS2024001" \
  -F "name=John Doe" \
  -F "department=Computer Science" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg"
```

### Step 2 — Train the model
```bash
curl -X POST "http://localhost:8000/model/train?fine_tune=false"
```
Training runs in the background. Check status:
```bash
curl http://localhost:8000/model/status
```

### Step 3 — Detect faces
```bash
curl -X POST http://localhost:8000/detect/image \
  -F "image=@group_photo.jpg" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['detections'])"
```

### Step 4 — View logs
```bash
curl http://localhost:8000/detect/logs
```

---

## 🌩️ Deploy to Azure (Free Tier)

```bash
# Install Azure CLI first
az login
chmod +x deploy_azure.sh
./deploy_azure.sh
```

This creates:
- **Azure Container Registry** (Basic, ~$5/month or free first month)
- **Azure Container Apps** (scales to 0 = free when idle, ~180,000 vCPU-seconds/month free)

---

## 📡 API Reference

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students/register` | Register student with images |
| POST | `/students/register-bulk` | Register multiple students |
| GET  | `/students/` | List all students |
| GET  | `/students/{reg_no}` | Get student info |
| DELETE | `/students/{reg_no}` | Soft deactivate |
| DELETE | `/students/{reg_no}/hard` | Permanently remove |

### Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/detect/image` | Detect + identify faces in image |
| GET  | `/detect/logs` | View detection history |

### Model
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/model/train` | Trigger retraining |
| GET  | `/model/status` | Current model info |
| GET  | `/model/versions` | All model versions |

---

## 🧠 Model Architecture

```
Input (224×224×3 RGB)
  └─ VGG16 (ImageNet pretrained, base frozen)
       └─ GlobalAveragePooling2D
            └─ Dense(512) + BatchNorm + ReLU + Dropout(0.5)
                 └─ Dense(256) + BatchNorm + ReLU + Dropout(0.3)
                      └─ Dense(N_students, Softmax)
```

**Training Phases:**
- **Phase 1** (fast): Frozen VGG16 base, only top layers trained
- **Phase 2** (optional fine-tune): Last 8 VGG16 layers unfrozen, low LR

**Augmentation:** Flip, rotation ±15°, zoom, brightness, contrast

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./face_recognition.db` | DB connection |
| `DATA_DIR` | `data/students` | Training images root |
| `MODELS_DIR` | `saved_models` | Model checkpoint dir |
| `CONFIDENCE_THRESHOLD` | `0.75` | Min confidence (0-1) |
| `TRAIN_EPOCHS` | `25` | Max training epochs |

---

## 📊 Accuracy Tips

- ✅ 15–20 varied photos per student (different angles, lighting)
- ✅ Use `fine_tune=true` for best accuracy (needs ≥5 students)
- ✅ Retrain after every add/remove of students
- ✅ Set `CONFIDENCE_THRESHOLD=0.80` for stricter matching
