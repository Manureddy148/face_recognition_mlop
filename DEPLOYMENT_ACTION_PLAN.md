# 🚀 Deployment Next Steps - Quick Guide

## ✅ Current State

GCP resources are already in place:

```
✅ Cloud Run API enabled
✅ Firestore database created in us-central1
✅ Artifact Registry repository created
✅ Service account created
✅ IAM roles assigned
```

The repo workflows are also present and now aligned with Workload Identity Federation.

## ⚠️ Remaining Blocker

The GitHub Actions workflows assume the GCP Workload Identity pool, provider, and IAM binding already exist. If they do not exist yet, create them now.

## 🔐 Required GCP Commands

Run these in PowerShell:

```bash
$gcPath = "$env:APPDATA\..\Local\Google\Cloud SDK\google-cloud-sdk\bin"
$env:Path += ";$gcPath"

gcloud iam workload-identity-pools create "github-pool" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --location="global" `
  --display-name="GitHub Pool"

gcloud iam workload-identity-pools providers create-oidc "github-provider" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --location="global" `
  --workload-identity-pool="github-pool" `
  --display-name="GitHub Provider" `
  --attribute-mapping="google.subject=assertion.sub,assertion.aud=assertion.aud,assertion.repository=assertion.repository" `
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding `
  "attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com" `
  --project="project-e553cc0c-7d4a-4519-ade" `
  --role="roles/iam.workloadIdentityUser" `
  --principal="principalSet://iam.googleapis.com/projects/149325054934/locations/global/workloadIdentityPools/github-pool/attribute.repository/Manureddy148/face_recognition_mlop"
```

If your organization requires key-based auth, that can still be done as a fallback, but the committed workflows do not use it anymore.

## 🔑 Required GitHub Secrets

Add these in GitHub repository → Settings → Secrets and variables → Actions:

```text
GCP_PROJECT_ID = project-e553cc0c-7d4a-4519-ade
MONGODB_URI = <your production MongoDB connection string>
```

## ▶️ Trigger Deployment

```bash
git push new-repo main
```

Or trigger manually from GitHub Actions.

## 🔍 What The Fixed Deploy Flow Does

1. Builds and pushes the backend image.
2. Deploys the backend to Cloud Run.
3. Reads the live backend URL.
4. Builds the frontend image with that backend URL baked into the Next.js build.
5. Pushes and deploys the frontend.
6. Runs smoke tests.

PRs no longer deploy to production.

## ⏱️ Remaining Timeline

| Task | Estimated Time | Status |
|------|-----------------|--------|
| Create or verify Workload Identity | 15 min | ⏳ Pending |
| Add GitHub secrets | 5 min | ⏳ Pending |
| Trigger deployment | 1 min | ⏳ Pending |
| Monitor workflow | 10 min | ⏳ Pending |
| Verify live services | 5 min | ⏳ Pending |
| **TOTAL** | **~35 min** | ⏳ Remaining |

## 🔑 Key Details

| Item | Value |
|------|-------|
| GCP Project | project-e553cc0c-7d4a-4519-ade |
| Service Account | attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com |
| Workload Identity Provider | projects/149325054934/locations/global/workloadIdentityPools/github-pool/providers/github-provider |
| Firestore Location | us-central1 |
| Artifact Registry | us-central1-docker.pkg.dev/project-e553cc0c-7d4a-4519-ade/attendance |
| Backend Service | attendance-backend |
| Frontend Service | attendance-frontend |
| GitHub Repo | https://github.com/Manureddy148/face_recognition_mlop |

## 📞 Verification Commands

```bash
gcloud run services list --region us-central1
gcloud run logs read attendance-backend --limit 50
gcloud run logs read attendance-frontend --limit 50
```

---

**Status:** Repo-side deployment flow is fixed. GCP Workload Identity and GitHub secrets are the remaining external steps.
