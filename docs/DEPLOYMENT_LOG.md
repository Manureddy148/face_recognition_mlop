# Deployment Log

## Date

April 3, 2026

## Change Summary (Branch Validation)

- Attendance session controls updated in teacher flow.
- Stop Face Recognition control removed.
- End Attendance Session retained as the single stop action.
- Camera stream teardown hardened to stop webcam tracks when ending session.

## IDs Tracking (No Keys)

### GitHub

- Repository: Manureddy148/face_recognition_mlop
- Working branch: chore/next-changes
- Base commit before this docs update: 4552cc3
- New commit ID for this update: PENDING
- PR ID (if created): PENDING
- GitHub Actions deploy run ID: PENDING

### Deployment

- Deploy target branch: main
- Deploy trigger: push to main
- Deployment execution ID: PENDING

### Cloud

- GCP project ID: project-e553cc0c-7d4a-4519-ade
- Region: us-central1
- Backend service: attendance-backend
- Frontend service: attendance-frontend
- Backend revision after next deploy: PENDING
- Frontend revision after next deploy: PENDING

## Date

March 29, 2026

## Deployment Method

GitHub Actions auto deployment on push to `main`

## Verified Production Endpoints

- Backend: `https://attendance-backend-aqwtwzewvq-uc.a.run.app`
- Frontend: `https://attendance-frontend-aqwtwzewvq-uc.a.run.app`

## Latest Verified State

- GitHub Actions deploy workflow completed successfully
- backend health check returned healthy status
- backend database connection returned true
- backend model readiness returned true
- frontend responded with HTTP 200

## Latest Known Cloud Run Revisions

- Backend revision: `attendance-backend-00032-4px`
- Frontend revision: `attendance-frontend-00027-67g`

## Deployment Flow Summary

1. Developer pushes code to `main`
2. GitHub Actions starts deployment
3. Backend image builds and deploys
4. Frontend image builds using backend URL
5. Frontend deploys
6. Smoke tests confirm service health

## Useful Demo Statement

"This is not only a local project. It is deployed on GCP Cloud Run and updated automatically through GitHub Actions whenever code is pushed to main."