# Short Live Project Snapshot

## Date

April 3, 2026

## Project Status

- Web app is live on Google Cloud Run.
- Attendance session UI has been updated.
- Stop Face Recognition menu action removed from teacher session controls.
- End Attendance Session remains as the single session-stop action.
- Camera shutdown flow improved so webcam stream is stopped when ending session.

## Live Endpoints

- Frontend: https://attendance-frontend-aqwtwzewvq-uc.a.run.app
- Backend: https://attendance-backend-aqwtwzewvq-uc.a.run.app

## IDs Snapshot (No Keys)

### GitHub IDs

- Repository: Manureddy148/face_recognition_mlop
- Base branch for production deploys: main
- Working branch for current update: chore/next-changes
- Latest local commit before new docs commit: 4552cc3
- New docs commit ID: 6a751a3
- GitHub Actions deploy run ID: PENDING

### Deployment IDs

- Deployment date target: April 2026
- Deploy environment: production (Cloud Run)
- Deployment execution ID: PENDING

### Cloud IDs

- GCP project ID: project-e553cc0c-7d4a-4519-ade
- Region: us-central1
- Cloud Run service (backend): attendance-backend
- Cloud Run service (frontend): attendance-frontend
- Backend revision ID after next deploy: PENDING
- Frontend revision ID after next deploy: PENDING

## Test Scope After Deploy

1. Create attendance session.
2. Start attendance session and confirm camera starts.
3. Click End Attendance Session and confirm camera turns off immediately.
4. Verify session close status message and records behavior.