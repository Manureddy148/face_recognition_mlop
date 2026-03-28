# GCP Deployment Guide

This folder contains scripts and documentation for deploying the Face Recognition Attendance System to Google Cloud Platform.

## Quick Start (10 Minutes)

### Prerequisites
- Google Cloud SDK installed (`gcloud` CLI)
- Docker installed locally
- Active GCP project with billing enabled
- Terminal/Command Prompt access

### 1. Setup GCP Project (2 min)

```bash
cd gcp
bash setup.sh
```

This will:
- Enable required APIs (Cloud Run, Firestore, Artifact Registry)
- Create Firestore database
- Create service account with permissions
- Setup Docker authentication

**Note on Windows:** If running on PowerShell, use `bash setup.sh` or convert to PowerShell script.

### 2. Configure Environment (1 min)

Edit `backend/.env`:
```bash
FIRESTORE_PROJECT_ID=your-project-id  # Copy from setup.sh output
FLASK_ENV=production
CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.a.run.app
```

### 3. Deploy Services (5 min)

```bash
cd gcp
bash deploy.sh
```

This will:
- Build backend Docker image
- Build frontend Docker image
- Push to Artifact Registry
- Deploy backend to Cloud Run
- Deploy frontend to Cloud Run
- Output URLs for accessing the system

### 4. Verify Deployment (2 min)

1. Visit the **Frontend URL** from deploy.sh output
2. Try registering a test student
3. Try marking attendance
4. Check Firebase Console (Firestore) for data

---

## Deployment Architecture

```
┌─────────────────────────────────────┐
│        Browser (Frontend)           │
│   https://attendance-frontend...    │
│                                     │
│  Next.js React App (Cloud Run)      │
└────────────┬────────────────────────┘
             │ HTTP/HTTPS
             ↓
┌─────────────────────────────────────┐
│       Backend API (Cloud Run)       │
│   https://attendance-backend...     │
│                                     │
│  Flask API with Face Recognition   │
└────────────┬────────────────────────┘
             │ Native Client Library
             ↓
┌─────────────────────────────────────┐
│    Google Cloud Firestore           │
│                                     │
│  ├─ students (biometric data)      │
│  ├─ attendance (records)            │
│  └─ sessions (teacher sessions)     │
└─────────────────────────────────────┘
```

---

## File Descriptions

### setup.sh
Automated setup script that:
- Checks GCP CLI installation
- Enables required services
- Creates Artifact Registry
- Creates Firestore database
- Creates service account
- Configures Docker auth

**Usage:**
```bash
bash setup.sh
```

**Output:**
- Project ID saved in gcloud config
- Service account created
- All APIs enabled

### deploy.sh
Automated deployment script that:
- Builds Docker images locally
- Pushes to Artifact Registry
- Deploys backend to Cloud Run
- Deploys frontend to Cloud Run
- Outputs service URLs

**Usage:**
```bash
bash deploy.sh
```

**Output:**
- Backend URL (REST API)
- Frontend URL (Web application)
- Credentials for Cloud Console access

### Troubleshooting Guide (Below)

---

## Manual Deployment (If Scripts Fail)

### Step 1: Build Backend Image

```bash
docker build -t us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/backend:latest ./backend
docker push us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/backend:latest
```

### Step 2: Deploy Backend to Cloud Run

```bash
gcloud run deploy attendance-backend \
  --image us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/backend:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --allow-unauthenticated \
  --set-env-vars FIRESTORE_PROJECT_ID=[PROJECT_ID],FLASK_ENV=production
```

### Step 3: Build Frontend Image

```bash
docker build -t us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/frontend:latest ./frontend
docker push us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/frontend:latest
```

### Step 4: Deploy Frontend to Cloud Run

```bash
gcloud run deploy attendance-frontend \
  --image us-central1-docker.pkg.dev/[PROJECT_ID]/attendance/frontend:latest \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://attendance-backend-xxxxx.a.run.app
```

---

## Post-Deployment

### Access Firestore Console
```bash
gcloud firestore databases list
```
Visit: https://console.cloud.google.com/firestore

### View Service Logs
```bash
# Backend logs
gcloud run logs read attendance-backend --limit 50

# Frontend logs
gcloud run logs read attendance-frontend --limit 50
```

### Scale Services
```bash
# Update backend memory/CPU
gcloud run services update attendance-backend \
  --memory 4Gi \
  --cpu 4
```

### Delete Services (Cleanup)
```bash
gcloud run services delete attendance-backend --quiet
gcloud run services delete attendance-frontend --quiet
```

---

## Troubleshooting

### Error: "Docker image not found"
**Solution:** Make sure you're in the project root and Docker is running
```bash
docker --version  # Verify Docker is installed
docker images     # List built images
```

### Error: "Permission denied" on setup.sh
**Solution:** Make script executable
```bash
chmod +x gcp/setup.sh
chmod +x gcp/deploy.sh
```

### Error: "Google Cloud SDK not installed"
**Solution:** Install from https://cloud.google.com/sdk/docs/install

### Error: "Project not set"
**Solution:** Configure project
```bash
gcloud config set project your-project-id
```

### Error: "Artifact Registry not found"
**Solution:** Run setup.sh first
```bash
bash gcp/setup.sh
```

### Backend returns 500 errors
**Cause:** Firestore not initialized or credentials missing

**Solution:**
1. Check environment variables: `echo $FIRESTORE_PROJECT_ID`
2. Verify service account has Firestore permissions
3. Check logs: `gcloud run logs read attendance-backend --limit 50`

### Frontend can't reach backend
**Cause:** CORS or incorrect API URL

**Solution:**
1. Verify backend is running: `curl https://backend-url/health`
2. Check frontend env var: `NEXT_PUBLIC_API_URL=https://backend-url`
3. Check backend CORS config in app.py

### Firestore quota exceeded
**Cause:** Too many read/write operations

**Solution:**
1. Check quota: GCP Console → Firestore → Usage
2. Wait for quota reset (typically hourly)
3. Consider upgrading billing plan

---

## Cost Estimation

### Monthly Cost (Small Scale)
- Cloud Run (backend): ~$5-10/month
- Cloud Run (frontend): ~$2-5/month
- Firestore: ~$1-5/month (free tier may apply)
- **Total: ~$10-20/month**

### Cost Optimization
1. Use Cloud Run (serverless) - scales to zero
2. Configure Firestore indexes only as needed
3. Monitor resource usage in GCP Console
4. Set billing alerts

---

## Local Testing Before Cloud Deployment

### Test with docker-compose (Firestore Emulator)
```bash
docker-compose up

# In browser:
# Frontend: http://localhost:3000
# Backend: http://localhost:5000

# Firestore Emulator: http://localhost:8080
```

### Test Against Real Firestore
```bash
# Set environment variables
export FIRESTORE_PROJECT_ID=your-project-id
export FLASK_ENV=development

# Run locally
cd backend && python app.py
cd ../frontend && npm run dev
```

---

## Next Steps

1. ✅ Run `bash gcp/setup.sh`
2. ✅ Run `bash gcp/deploy.sh`
3. ✅ Visit frontend URL and test
4. ✅ Monitor logs: `gcloud run logs read attendance-backend`
5. ✅ Backup data: `gcloud firestore export gs://your-bucket`

---

## Support

For issues not covered here:
1. Check GCP Cloud Run documentation: https://cloud.google.com/run/docs
2. Check Firestore documentation: https://cloud.google.com/firestore/docs
3. Review backend logs for detailed error messages
4. Check frontend browser console for client-side errors

---

## Rollback (If Needed)

### Rollback to previous version
```bash
# Cloud Run automatically keeps previous versions
gcloud run services describe attendance-backend --region=us-central1
gcloud run services update-traffic attendance-backend --to-revisions=PREVIOUS=100
```

### Delete entire deployment
```bash
gcloud run services delete attendance-backend attendance-frontend
gcloud firestore databases delete
```

---

**Last Updated:** March 2026
**Status:** Ready for production deployment
