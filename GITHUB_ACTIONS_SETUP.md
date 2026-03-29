# GitHub Actions CI/CD Setup Guide

## ✅ Files Created

Three workflow files are in `.github/workflows/`:
- `deploy.yml` - Deploys to Cloud Run from `main` or manual runs
- `verify.yml` - Verifies PR changes without touching production
- `schedule-backup.yml` - Runs scheduled Firestore backups

## 🔑 Required GitHub Secrets

Configure these repository secrets in GitHub:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `project-e553cc0c-7d4a-4519-ade` |
| `MONGODB_URI` | Your production MongoDB connection string |

The workflows no longer require `GCP_SA_KEY`. Authentication is handled with Workload Identity Federation.

## 🔐 Workload Identity Settings

The repo workflows expect these GCP resources to exist:

- Workload identity provider: `projects/149325054934/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- Service account: `attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com`

If they do not exist yet, create them with the commands in `DEPLOYMENT_ACTION_PLAN.md`.

## 📋 Next Steps

### Step 1: Install Google Cloud SDK

```bash
# Download from: https://cloud.google.com/sdk/docs/install
# Or install via PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe"); & $env:Temp\GoogleCloudSDKInstaller.exe
```

### Step 2: Verify or create Workload Identity

Use the PowerShell commands documented in `DEPLOYMENT_ACTION_PLAN.md` to create:
- `github-pool`
- `github-provider`
- The `roles/iam.workloadIdentityUser` binding for the GitHub repository

### Step 3: Initialize GCP Project

```bash
gcloud --version
gcloud config set project project-e553cc0c-7d4a-4519-ade
bash gcp/verify.sh
bash gcp/setup.sh
```

### Step 4: Add GitHub Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add `GCP_PROJECT_ID`
3. Add `MONGODB_URI`

### Step 5: Push to `main`

```bash
git add .github/ frontend/Dockerfile GITHUB_ACTIONS_SETUP.md DEPLOYMENT_ACTION_PLAN.md
git commit -m "Fix Cloud Run GitHub Actions deployment flow"
git push origin main
```

### Step 6: Monitor Deployment

1. Open the GitHub repository Actions tab
2. Watch `Deploy to Cloud Run`
3. Confirm both services deploy successfully
4. Download the `deployment-urls` artifact if needed

## 🚀 What The Deploy Workflow Does

1. Builds the backend image
2. Pushes the backend image to Artifact Registry
3. Deploys the backend to Cloud Run
4. Reads the live backend URL
5. Builds the frontend image with `NEXT_PUBLIC_API_URL` set to that backend URL
6. Pushes the frontend image to Artifact Registry
7. Deploys the frontend to Cloud Run
8. Runs smoke tests against both services

## 📊 Workflow Triggers

- `deploy.yml`
  - Push to `main`
  - Manual trigger from GitHub Actions
- `verify.yml`
  - Pull requests targeting `main`
- `schedule-backup.yml`
  - Sunday at 2 AM UTC
  - Manual trigger from GitHub Actions

PRs do not deploy production anymore.

## 📌 Troubleshooting

### Authentication fails
- Verify the workload identity pool and provider exist
- Verify the IAM binding includes the correct GitHub repository

### Deployment fails with missing secret
- Add `GCP_PROJECT_ID` and `MONGODB_URI` in repository secrets

### Images fail to push
- Verify the service account still has `Artifact Registry Writer`
- Verify `GCP_PROJECT_ID` matches the actual GCP project

### Frontend points to the wrong backend
- Check the `Build frontend Docker image` step logs
- Confirm the backend URL was resolved before the frontend build step ran

## 🎯 Success Indicators

Deployment is healthy when:
- The workflow finishes with green checks
- `deployment-urls.txt` is uploaded as an artifact
- The backend `/health` endpoint returns successfully
- The frontend URL responds successfully

## 📚 Useful Commands

```bash
gcloud run services list --region us-central1
gcloud run logs read attendance-backend --limit 50
gcloud run logs read attendance-frontend --limit 50
```

---

**Timeline:** ~30-45 minutes including GCP setup and first deploy  
**Estimated cost:** $10-20/month
