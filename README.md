# Attendance Management System Using Face Recognition

This project is a face-recognition-based attendance management system with a modern web frontend, a Flask backend, and automated deployment to Google Cloud Run.

## What This Project Does

- Registers student details and face data
- Starts an attendance session for a selected class and subject
- Recognizes faces and marks attendance in real time
- Lets users view attendance by date, subject, department, year, division, and student ID
- Deploys automatically from GitHub `main` to Google Cloud Run

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Flask, Python
- Face Recognition: DeepFace, MTCNN
- Database: MongoDB
- Cloud: Google Cloud Run, Artifact Registry
- CI/CD: GitHub Actions

## Current Production Status

- Frontend URL: `https://attendance-frontend-aqwtwzewvq-uc.a.run.app`
- Backend URL: `https://attendance-backend-aqwtwzewvq-uc.a.run.app`
- Deployment mode: Auto deploy on push to `main`
- Current main commit at time of documentation: `3550e84`

## Documentation For Sir And Class

- `docs/PROJECT_OVERVIEW.md` - project summary, modules, and workflow
- `docs/DEPLOYMENT_NOTES.md` - deployment architecture and live cloud details
- `docs/PRESENTATION_NOTES.md` - short explanation script for presentation
- `docs/CHANGELOG_CLASS.md` - recent changes and important commits
- `docs/DEPLOYMENT_LOG.md` - deployment status and verification log

## Project Structure

- `frontend/` - Next.js frontend
- `backend/` - Flask backend APIs and face recognition flow
- `.github/workflows/` - CI/CD workflows
- `gcp/` - deployment scripts and cloud setup notes
- legacy Python scripts at root - original desktop attendance flow files kept for reference

## Deployment Flow

1. Code is pushed to GitHub `main`.
2. GitHub Actions workflow `deploy.yml` starts automatically.
3. Backend and frontend Docker images are built.
4. Images are pushed to Artifact Registry.
5. Cloud Run services are updated.
6. Smoke tests verify the deployment.

## Quick Note

The repo now contains both legacy desktop attendance scripts and the newer deployed web application. For class explanation, focus on the web app flow and mention the legacy files as the earlier version of the project.

