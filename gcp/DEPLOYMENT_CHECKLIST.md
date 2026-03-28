# Deployment Checklist - Complete Step-by-Step Guide

## Pre-Flight Check (30 minutes)

### ✅ Prerequisites
- [ ] GCP account created (with billing enabled)
- [ ] Google Cloud SDK installed
- [ ] Docker installed and running
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Git with main branch configured

### ✅ Step 1: Verify Prerequisites
```bash
# Run verification script
bash gcp/verify.sh
# Should show: "All checks passed! Ready for deployment."
```

---

## Phase 1: GCP Project Setup (15 minutes)

### ✅ Step 2: Authenticate with GCP
```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

**Expected Output:**
```
Updated property [core/project].
```

### ✅ Step 3: Run GCP Setup Script
```bash
# Run setup script
bash gcp/setup.sh
```

**What it does:**
- ✓ Enables Cloud Run API
- ✓ Enables Firestore API
- ✓ Enables Artifact Registry API
- ✓ Creates Firestore database
- ✓ Creates service account
- ✓ Configures Docker authentication

**Expected Output:**
```
✓ APIs enabled
✓ Artifact Registry ready
✓ Firestore configured
✓ Service account created with permissions
✓ Docker authenticated
✓ GCP Setup Complete!
```

### ✅ Step 4: Create Backend .env File
```bash
# Copy template
cp backend/.env.example backend/.env

# Edit with your project ID
# Replace YOUR_PROJECT_ID with actual ID from setup.sh output
```

File: `backend/.env`
```
FIRESTORE_PROJECT_ID=YOUR_PROJECT_ID
FLASK_ENV=production
CORS_ORIGINS=http://localhost:3000
```

**Verify:**
```bash
cat backend/.env
# Should show your values, not placeholders
```

### ✅ Step 5: Create Frontend .env File
```bash
# Copy template
cp frontend/.env.example frontend/.env.local

# Edit (leave API_URL for now, will update after deployment)
```

File: `frontend/.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## Phase 2: Local Testing with Docker (30 minutes)

### ✅ Step 6: Build and Run Locally
```bash
# From project root
docker-compose up

# Wait for output like:
# firestore-emulator | ⠏ Emulator started
# backend | Running on http://0.0.0.0:5000
# frontend | ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Time to wait:** 60 seconds (models loading)

### ✅ Step 7: Test Backend Health
```bash
# In a new terminal
curl http://localhost:5000/health

# Expected response:
# {"status": "ok", "firestore": true}
```

**If fails:**
```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# - Firestore emulator not ready (wait 30s more)
# - Port already in use (lsof -i :5000)
```

### ✅ Step 8: Test Frontend in Browser
```bash
# Open browser
# Visit: http://localhost:3000

# Should see:
# - Navigation bar
# - Hero section
# - Features
# - Sign up button

# Click Sign Up → Should load without errors
```

**If page won't load:**
```bash
# Check frontend logs
docker-compose logs frontend

# Check browser console (F12 → Console)
# Look for network errors
```

### ✅ Step 9: Quick Feature Test (Local)
1. **Test Student Registration:**
   - Go to http://localhost:3000/signup
   - Fill form
   - Click "Sign Up"
   - Should see success message

2. **Test API Integration:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Perform action from step 1
   - Verify API calls complete without errors

3. **Check Firestore Emulator:**
   - Visit http://localhost:8080/
   - Check if data collections exist

**If tests fail:**
```bash
# Check all container logs
docker-compose logs

# Restart everything
docker-compose down
docker-compose up
```

### ✅ Step 10: Stop Local Services
```bash
# Stop containers (Ctrl+C or in another terminal)
docker-compose down

# Verify stopped
docker ps
# Should show no attendance containers
```

---

## Phase 3: Cloud Deployment (30 minutes)

### ✅ Step 11: Verify Docker Daemon
```bash
# Make sure Docker is running
docker ps

# Expected: Shows columns (no error)
```

### ✅ Step 12: Make Deploy Script Executable
```bash
# On Mac/Linux
chmod +x gcp/deploy.sh

# On Windows PowerShell (should work as-is)
bash gcp/deploy.sh
```

### ✅ Step 13: Deploy to Cloud Run
```bash
# From project root
bash gcp/deploy.sh

# This will take 3-5 minutes
# Shows progress:
# - Building backend image...
# - Pushing backend image...
# - Deploying backend to Cloud Run...
# - Building frontend image...
# - Pushing frontend image...
# - Deploying frontend to Cloud Run...
```

**Expected Output:**
```
✓ Backend image pushed
✓ Backend deployed: https://attendance-backend-xxxxx.a.run.app
✓ Frontend deployed: https://attendance-frontend-xxxxx.a.run.app
```

**Save these URLs!** You'll need them next.

### ✅ Step 14: Verify Backend Deployment
```bash
# Test backend health
curl https://attendance-backend-xxxxx.a.run.app/health

# Expected:
# {"status": "ok", "firestore": true}

# Check logs (if error)
gcloud run logs read attendance-backend --limit 50
```

**If health check fails:**
```bash
# Check logs for errors
gcloud run logs read attendance-backend --limit 100

# Common issues:
# - Firestore project ID not set (check FIRESTORE_PROJECT_ID env var)
# - Service account permissions (re-run gcp/setup.sh)
# - Container image corruption (rebuild with: docker system prune -a)
```

### ✅ Step 15: Update Frontend Configuration
Now that you have the backend URL, update frontend:

```bash
# Edit frontend/.env.local
nano frontend/.env.local  # or use VS Code

# Change NEXT_PUBLIC_API_URL to your backend URL
NEXT_PUBLIC_API_URL=https://attendance-backend-xxxxx.a.run.app
```

[No need to redeploy frontend, it's already deployed.]

Actually, the frontend was deployed with old API URL. You need to UPDATE and REDEPLOY:

```bash
# Rebuild frontend with new API URL
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/attendance/frontend:latest ./frontend
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/attendance/frontend:latest

# Redeploy frontend
gcloud run deploy attendance-frontend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/attendance/frontend:latest \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --allow-unauthenticated \
  --quiet
```

### ✅ Step 16: Test Frontend in Browser
```bash
# Visit frontend URL
https://attendance-frontend-xxxxx.a.run.app

# Should see:
# - Home page loads
# - Navigation works
# - Sign up page accessible
# - No 504 Gateway Errors
```

**If page shows error:**
```bash
# Check frontend logs
gcloud run logs read attendance-frontend --limit 50

# Common issues:
# - Still using old API URL (redo Step 15)
# - Backend service not running (check Step 14)
```

---

## Phase 4: End-to-End Testing (30 minutes)

### ✅ Step 17: Test Student Registration Flow

**Part A: Sign Up**
1. Visit frontend URL
2. Click "Sign Up"
3. Fill form:
   - Email: test@example.com
   - Password: Test@123
   - ID: 12345
   - Name: Test Student
4. Click "Sign Up"
5. Should see success message

**Part B: Login**
1. Click "Sign In"
2. Enter credentials from Part A
3. Should see dashboard

**Part C: Register Face**
1. Click "Register for Attendance"
2. Allow camera access
3. Capture face (50 images)
4. Should see "Registration Complete"

**If fails:**
- Check browser console for errors (F12)
- Check backend logs: `gcloud run logs read attendance-backend --limit 50`

### ✅ Step 18: Test Attendance Marking

1. Go to "Demo Session"
2. Click "Start Session"
3. Enter subject: "Test Subject"
4. Click "Mark Attendance"
5. Face camera for 5 seconds
6. Should see "Attendance Marked"

**If fails:**
- Check backend logs for face detection errors
- Verify Firestore has student data: Cloud Console → Firestore

### ✅ Step 19: Verify Firestore Data

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Firestore Database
4. Check collections:
   - `students` should have registered student
   - `attendance` should have attendance record

**If collections empty:**
- Backend not connected to Firestore (check FIRESTORE_PROJECT_ID)
- API calls failing (check backend logs)

### ✅ Step 20: Test CSV Export

1. Go to "View Attendance"
2. Select subject from Step 18
3. Click "Export as CSV"
4. File should download

---

## Phase 5: Final Verification (10 minutes)

### ✅ Step 21: Performance Check
```bash
# Test response time
time curl https://attendance-backend-xxxxx.a.run.app/health

# Should be < 2 seconds
```

### ✅ Step 22: Monitor Cloud Resources
```bash
# Check Cloud Run services
gcloud run services list

# Expected output should show:
# NAME                    STATUS   LAST_DEPLOYED
# attendance-backend      ✓        2 minutes ago
# attendance-frontend     ✓        2 minutes ago
```

### ✅ Step 23: View Cost Estimates
```bash
# Open Cloud Console
# Navigation → Billing
# Should show estimated cost (~$10-20/month for small scale)
```

### ✅ Step 24: Document Deployment

Create a file: `DEPLOYMENT_INFO.md`
```markdown
# Deployment Information

## URLs
- Backend: https://attendance-backend-xxxxx.a.run.app
- Frontend: https://attendance-frontend-xxxxx.a.run.app

## Project ID
- YOUR_PROJECT_ID

## Region
- us-central1

## Created On
- [Date]

## Key Services
- Cloud Run: attendance-backend, attendance-frontend
- Firestore: facerecognition database
- Artifact Registry: us-central1-docker.pkg.dev/YOUR_PROJECT_ID/attendance
```

### ✅ Step 25: Communicate Links
Share with stakeholders:
- ✓ Frontend URL for access
- ✓ Instructions for first login
- ✓ Support contact

---

## Success! ✅

| Component | Status |
|-----------|--------|
| GCP Project | ✅ Configured |
| Firestore Database | ✅ Active |
| Backend Service | ✅ Running |
| Frontend Service | ✅ Running |
| Student Registration | ✅ Working |
| Attendance Marking | ✅ Working |
| Data Persistence | ✅ Firestore |

---

## Post-Deployment (Days 2+)

### [ ] Data Migration (If Needed)
```bash
export FIRESTORE_PROJECT_ID=YOUR_PROJECT_ID
python gcp/migrate_to_firestore.py
```

### [ ] Setup Monitoring
- GCP Console → Cloud Run → select service → Metrics
- Set up alerts for:
  - Error rate > 1%
  - Response time > 2s
  - Out-of-memory errors

### [ ] Backup Data
```bash
# Export Firestore
gcloud firestore export gs://your-backup-bucket
```

### [ ] Scale Configuration
```bash
# Increase max instances if needed
gcloud run services update attendance-backend \
  --max-instances 50
```

### [ ] Setup SSL Certificate (If Custom Domain)
```bash
gcloud run services update attendance-backend \
  --add-domain yourdomain.com
```

### [ ] Enable CI/CD (Optional)
- Connect GitHub repo
- Push changes → auto-deploy
- See: `.github/workflows` (future implementation)

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Backend 500 error | `gcloud run logs read attendance-backend --limit 50` |
| Frontend blank page | Check .env.local has correct NEXT_PUBLIC_API_URL |
| Can't register face | Camera permissions in browser |
| Firestore empty | Check if backend actually posting data (backend logs) |
| Slow response | Cloud Run cold start (normal first time) |
| "Project not set" | `gcloud config set project YOUR_PROJECT_ID` |

---

## Final Notes

✅ **You now have:**
- Production deployment on GCP Cloud Run
- Firestore database for persistent storage
- Frontend accessible from anywhere
- Automatic HTTPS
- Auto-scaling infrastructure
- ~$10-20/month cost

🎉 **Deployment Complete!**

For questions, refer to:
- gcp/README.md - Full documentation
- gcp/QUICKSTART.md - Quick reference
- Backend logs - Debugging

---

**Creation Date:** [Your Date]
**Last Updated:** [Date]
**Status:** Production Ready
