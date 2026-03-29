# Deployment Notes

## Current Deployment Model

This project is deployed using GitHub Actions and Google Cloud Run.

## Live Services

- Frontend: `https://attendance-frontend-aqwtwzewvq-uc.a.run.app`
- Backend: `https://attendance-backend-aqwtwzewvq-uc.a.run.app`
- Region: `us-central1`
- GCP Project: `project-e553cc0c-7d4a-4519-ade`

## Deployment Trigger

The deployment workflow runs automatically when code is pushed to `main`.

Workflow file:

- `.github/workflows/deploy.yml`

## Deployment Steps

1. GitHub Actions checks out the repository.
2. It authenticates to GCP using Workload Identity Federation.
3. Backend Docker image is built and pushed.
4. Backend is deployed to Cloud Run.
5. Frontend Docker image is built using the backend URL.
6. Frontend is deployed to Cloud Run.
7. Smoke tests validate backend health and frontend availability.

## Important Cloud Components

- Cloud Run service: `attendance-backend`
- Cloud Run service: `attendance-frontend`
- Artifact Registry repository: `attendance`
- Service account: `attendance-sa@project-e553cc0c-7d4a-4519-ade.iam.gserviceaccount.com`
- Workload identity provider: `github-provider`

## Current Health Status

Verified on March 29, 2026:

- latest GitHub deploy run: success
- backend `/health`: healthy
- database connection: true
- model readiness: true
- frontend response: HTTP 200

## What To Say If Asked About Deployment

"The project is not deployed manually every time. We push changes to GitHub main, and GitHub Actions automatically builds and deploys both backend and frontend to Google Cloud Run. After deployment, smoke tests confirm the services are running correctly."