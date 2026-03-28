# GitHub Actions CI/CD Setup Guide

## ✅ Files Created

Three workflow files are now in `.github/workflows/`:
- `deploy.yml` - Main deployment to Cloud Run
- `verify.yml` - PR verification checks
- `schedule-backup.yml` - Weekly Firestore backups

## 🔑 Required GitHub Secrets (CRITICAL STEP)

Before pushing to GitHub, configure these secrets in your repository:

### Step 1: Get GCP Credentials

```bash
# On your Windows terminal, get the service account key:
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com
```

### Step 2: Create GitHub Secrets

1. Go to **GitHub repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add these:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `project-e553cc0c-7d4a-4519-ade` |
| `GCP_SA_KEY` | (Contents of gcp-key.json file) |
| `GCP_SERVICE_ACCOUNT_EMAIL` | `attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com` |

**How to add GCP_SA_KEY:**
- Open `gcp-key.json` in a text editor
- Copy entire JSON content
- Paste into GitHub secret value field

## 📋 Next Steps

### Step 1: Install Google Cloud SDK (if not already done)

```bash
# Download from: https://cloud.google.com/sdk/docs/install
# Or install via PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe"); & $env:Temp\GoogleCloudSDKInstaller.exe
```

### Step 2: Initialize GCP Project

```bash
# Verify gcloud is installed
gcloud --version

# Set project
gcloud config set project project-e553cc0c-7d4a-4519-ade

# Run setup script from gcp folder
bash gcp/verify.sh        # Check prerequisites
bash gcp/setup.sh         # Initialize GCP resources
```

### Step 3: Commit and Push to GitHub

```bash
# Add all workflow files
git add .github/

# Commit
git commit -m "Add GitHub Actions CI/CD workflows for Cloud Run deployment"

# Push to main branch (this triggers the first deployment!)
git push origin main
```

### Step 4: Monitor First Deployment

1. Go to GitHub repository → **Actions** tab
2. Watch the `Deploy to Cloud Run` workflow run
3. Check the logs for any errors
4. Once successful, you'll see deployment URLs in the workflow summary

## 🚀 What Happens Next

When you push to GitHub:
1. GitHub Actions automatically builds your app
2. Docker images are created and pushed to GCP Artifact Registry
3. Backend deployed to Cloud Run (2 CPU, 2GB RAM)
4. Frontend deployed to Cloud Run (1 CPU, 1GB RAM)
5. Health checks verify both services are running
6. URLs appear in PR comments (for PRs) or workflow artifacts

## 📊 Workflow Triggers

- **Deploy workflow** triggers on:
  - Push to `main` branch (auto-deploys)
  - Pull request (preview deployment)
  - Manual trigger via GitHub Actions tab

- **Verify workflow** triggers on:
  - Every pull request (checks dependencies)

- **Backup workflow** triggers on:
  - Every Sunday at 2 AM UTC (scheduled)
  - Manual trigger via GitHub Actions tab

## 🔍 Expected Deployment Flow

```
git push origin main
  ↓
GitHub Actions triggered
  ↓
Build backend Docker image
  ↓
Build frontend Docker image
  ↓
Push to Artifact Registry
  ↓
Deploy backend to Cloud Run
  ↓
Deploy frontend to Cloud Run
  ↓
Run health checks
  ↓
✅ Deployment complete! URLs ready to use
```

## 📌 Troubleshooting

### Workflow fails with "gcloud not found"
- Verify `GCP_SA_KEY` secret is properly configured (JSON content)

### Deploy fails with authentication error
- Check `GCP_SERVICE_ACCOUNT_EMAIL` secret is correct
- Verify service account has "Cloud Run Admin" role in GCP Console

### Images won't push to Artifact Registry
- Ensure `GCP_PROJECT_ID` is correct
- Check service account has "Artifact Registry Writer" role

### Frontend can't connect to backend
- Update `NEXT_PUBLIC_API_URL` in deploy.yml with actual backend URL after first deployment

## 🎯 Success Indicators

✅ Deployment successful when you see:
- All workflow steps complete (green checkmarks)
- Artifact contains `deployment-urls.txt`
- `Backend URL` and `Frontend URL` are accessible
- GitHub PR comment shows deployment links

## 📚 Useful Commands

### View deployment logs
```bash
gcloud run logs read attendance-backend --limit 50
gcloud run logs read attendance-frontend --limit 50
```

### Trigger workflow manually
- Go to GitHub → Actions → Select workflow → Run workflow

### View deployed services
```bash
gcloud run services list --region us-central1
```

### Rollback to previous version
```bash
# List revisions
gcloud run revisions list --service attendance-backend

# Deploy specific revision
gcloud run deploy attendance-backend --revision <revision-name>
```

---

**Timeline for Complete Setup:** ~45 minutes
- Google Cloud SDK setup: 10 min
- GCP project initialization: 15 min
- GitHub secrets configuration: 5 min
- First deployment via CI/CD: 15 min

**Cost Impact:** $10-20/month (Cloud Run + Firestore)
