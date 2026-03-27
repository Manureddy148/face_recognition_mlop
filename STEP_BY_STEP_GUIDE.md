# Complete Step-by-Step Guide

## Phase 1 - Setup Your Environment

### Step 1: Install Python 3.11
- Download from https://python.org/downloads
- During install, check "Add Python to PATH"
- Verify:

```bash
python --version
```

### Step 2: Install VS Code
- Download from https://code.visualstudio.com
- Install Python extension inside VS Code

### Step 3: Extract the project files
- Extract to a folder like `C:/face_recognition` or `~/face_recognition`

### Step 4: Create virtual environment
```bash
cd face_recognition
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

TensorFlow is large, so install may take 5-10 minutes.

## Phase 2 - Download Large Dataset (LFW Recommended)

```bash
pip install scikit-learn
python -c "
from sklearn.datasets import fetch_lfw_people
print('Downloading LFW dataset...')
lfw = fetch_lfw_people(min_faces_per_person=20, resize=1.0)
print(f'Done! {lfw.images.shape[0]} images, {len(lfw.target_names)} people')
"
```

## Phase 3 - Pretrain VGG16 on LFW

This repo includes `pretrain_lfw.py`.

```bash
python pretrain_lfw.py
```

Expected outputs:
- `saved_models/pretrained_lfw.keras`
- `saved_models/pretrain_labels.json`

## Phase 4 - Evaluate Pretrained Model

This repo includes `evaluate.py`.

```bash
python evaluate.py
```

Expected output:
- `saved_models/confusion_matrix.png`

## Phase 5 - Fine-tune on Your Students

1. Run API:
```bash
uvicorn app.main:app --port 8000 --reload
```

2. Open UI:
`http://localhost:8000/ui`

3. Register each student with 15-20 photos.
4. Trigger model fine-tuning from UI (Train tab) or API:

```bash
curl -X POST "http://localhost:8000/model/train?fine_tune=true"
```

If `saved_models/pretrained_lfw.keras` exists, training auto warm-starts from it using `PRETRAINED_MODEL_PATH`.

## Summary

1. Install Python + VS Code
2. Setup venv and install dependencies
3. Download LFW
4. Run `pretrain_lfw.py`
5. Run `evaluate.py`
6. Start API
7. Register students
8. Fine-tune model
9. Test detection
10. Deploy to Azure
