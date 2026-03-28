# GCP Deployment Status Report

**Date:** March 28, 2026  
**Status:** ✅ **SETUP COMPLETE** (Partial - Manual GitHub Actions Configuration Required)

---

## ✅ Completed GCP Setup

### 1. APIs Enabled
All required Google Cloud APIs are now **ACTIVE**:
- ✅ Cloud Run API (`run.googleapis.com`)
- ✅ Firestore API (`firestore.googleapis.com`)
- ✅ Artifact Registry API (`artifactregistry.googleapis.com`)
- ✅ IAM API (`iam.googleapis.com`)

### 2. Firestore Database Created
**Details:**
- **Type:** Firestore Native
- **Location:** us-central1
- **Mode:** Pessimistic Locking (default)
- **Status:** ACTIVE and Ready
- **Database ID:** `(default)`
- **Free Tier:** Enabled (includes free quota)

### 3. Artifact Registry Repository
**Details:**
- **Repository Name:** `attendance`
- **Type:** Docker
- **Location:** us-central1
- **Format:** Docker Container Images
- **Status:** Ready for image uploads

### 4. Service Account Created
**Details:**
- **Email:** `attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com`
- **Display Name:** Attendance System Service Account
- **Status:** ACTIVE
- **IAM Roles Assigned:**
  - ✅ Cloud Run Admin (`roles/run.admin`)
  - ✅ Datastore Admin (`roles/datastore.admin`) - Firestore
  - ✅ Artifact Registry Writer (`roles/artifactregistry.writer`)

### 5. Project Configuration
- **Project ID:** `project-e553cc0c-7d4a-4519-ade`
- **Region:** us-central1
- **Current Active:** All APIs and services

---

## ⚠️ Required Manual Step: GitHub Actions Setup

### Issue: Service Account Key Creation Blocked
**Error:** Key creation is not allowed on this service account  
**Cause:** GCP project has a security policy constraint: `iam.disableServiceAccountKeyCreation`

### Solution: Use Workload Identity Federation
Instead of creating keys, use **Workload Identity Federation** (recommended for GitHub Actions):

#### Step 1: Create Workload Identity Pool
```bash
$gcPath = "$env:APPDATA\..\Local\Google\Cloud SDK\google-cloud-sdk\bin"
$env:Path += ";$gcPath"

gcloud iam workload-identity-pools create "github-pool" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --location="global" `
  --display-name="GitHub Pool"
```

#### Step 2: Create Workload Identity Provider
```bash
gcloud iam workload-identity-pools providers create-oidc "github-provider" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --location="global" `
  --workload-identity-pool="github-pool" `
  --display-name="GitHub Provider" `
  --attribute-mapping="google.subject=assertion.sub,assertion.aud=assertion.aud,assertion.repository=assertion.repository" `
  --issuer-uri="https://token.actions.githubusercontent.com"
```

#### Step 3: Create Service Account IAM Binding
```bash
gcloud iam service-accounts add-iam-policy-binding `
  "attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --role="roles/iam.workloadIdentityUser" `
  --principal="principalSet://iam.googleapis.com/projects/project-e553cc0c-7d4a-4519-ade/locations/global/workloadIdentityPools/github-pool/attribute.repository/Manureddy148/face_recognition_mlop"
```

### Alternative: Request Key Creation Exception
If Workload Identity is not available, contact your GCP administrator to:
1. Disable the `iam.disableServiceAccountKeyCreation` policy constraint
2. Create a service account key manually
3. Add to GitHub Secrets as `GCP_SA_KEY`

---

## 📋 GitHub Actions Deployment Configuration

### Option 1: Using Workload Identity Federation (Recommended)

**Update `.github/workflows/deploy.yml`** to use Workload Identity:

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v1
  with:
    workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
    service_account: 'attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com'
    token_format: 'access_token'
    access_token_lifetime: '3600s'
```

### Option 2: Request Key Creation (If Policy Can Be Disabled)

```bash
# After policy is disabled, create key:
gcloud iam service-accounts keys create gcp-key.json `
  --iam-account=attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com

# Add to GitHub Secrets:
# Name: GCP_SA_KEY
# Value: (paste entire gcp-key.json content)
```

---

## 🚀 Next Steps

### 1. **Choose Authentication Method**
- **Recommended:** Workload Identity Federation (more secure)
- **Fallback:** Request policy exception for key creation

### 2. **Update GitHub Actions Workflows**
Modify `.github/workflows/deploy.yml` to use your chosen authentication method

### 3. **Configure GitHub Secrets** (Required)
Go to GitHub Repo → Settings → Secrets → Add:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `project-e553cc0c-7d4a-4519-ade` |
| `GCP_SERVICE_ACCOUNT_EMAIL` | `attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com` |
| `GCP_SA_KEY` | (Key file content - only if using key, not Workload Identity) |

### 4. **Test Deployment**
```bash
cd "C:\Users\Dell\Downloads\Attendance-Management-system-using-face-recognition"

# Option A: Push to GitHub
git push new-repo main

# Option B: Manually trigger GitHub Actions
# Go to GitHub → Actions → Deploy to Cloud Run → Run workflow
```

### 5. **Verify Deployment**
Once GitHub Actions completes:
```bash
# Check Cloud Run services
gcloud run services list --region us-central1

# Get backend URL
gcloud run services describe attendance-backend --region us-central1 --format='value(status.url)'

# Get frontend URL
gcloud run services describe attendance-frontend --region us-central1 --format='value(status.url)'

# Check logs
gcloud run logs read attendance-backend --limit 50
gcloud run logs read attendance-frontend --limit 50
```

---

## 📊 GCP Resources Inventory

| Resource | Status | Details |
|----------|--------|---------|
| Cloud Run API | ✅ Enabled | Backend & Frontend deployment |
| Firestore Database | ✅ Created | Native mode, us-central1, Free Tier |
| Artifact Registry | ✅ Created | Docker repository `attendance` |
| Service Account | ✅ Created | attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com |
| IAM Roles | ✅ Assigned | Run Admin, Datastore Admin, Artifact Registry Writer |

---

## 💡 Cost Estimates

| Service | Estimated Monthly Cost |
|---------|----------------------|
| Cloud Run (Backend: 2 CPU, 2GB) | $5-10 |
| Cloud Run (Frontend: 1 CPU, 1GB) | $2-3 |
| Firestore | $1-5 (includes free quota: 50k reads/day) |
| Artifact Registry | ~$0.10 |
| **Total** | **$10-20/month** |

---

## 🔐 Security Notes

✅ **Completed:**
- Service account uses principle of least privilege (specific roles only)
- Firestore uses free tier with automatic scaling
- APIs enabled only as needed
- IAM policies properly configured

⚠️ **Recommended for Production:**
- Enable Firestore backup routine
- Configure VPC Service Controls
- Enable Cloud Armor for DDoS protection
- Set up Cloud Monitoring & Alerting
- Rotate service account credentials regularly

---

## 📞 Troubleshooting

### Issue: "Key creation is not allowed on this service account"
**Solution:** Use Workload Identity Federation OR request policy exception from GCP admin

### Issue: GitHub Actions fails to authenticate
**Solution:** Verify GitHub Secrets are configured correctly (copy entire content without extra spaces)

### Issue: Cloud Run deployment fails
**Solution:** Check logs: `gcloud run logs read attendance-backend --limit 50`

### Issue: Firestore connection errors
**Solution:** Verify service account has `roles/datastore.admin` role assigned

---

## 📚 Related Documentation

- **GitHub Actions Setup:** See `GITHUB_ACTIONS_SETUP.md`
- **Deployment Guide:** See `DEPLOYMENT_SUMMARY.md`
- **GCP Guide:** See `gcp/README.md`
- **Quick Start:** See `gcp/QUICKSTART.md`

---

## ✅ Deployment Readiness Checklist

- [x] GCP Project initialized
- [x] All required APIs enabled
- [x] Firestore database created
- [x] Artifact Registry configured
- [x] Service account created with proper roles
- [ ] GitHub Actions authentication configured (Pending)
- [ ] GitHub Secrets added (Pending)
- [ ] Deployment triggered (Pending)
- [ ] Services verified online (Pending)

---

**Last Updated:** March 28, 2026, 22:50 UTC  
**Project:** Attendance Management System - Face Recognition  
**GCP Project:** project-e553cc0c-7d4a-4519-ade
