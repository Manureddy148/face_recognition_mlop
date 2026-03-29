# Deployment Log

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