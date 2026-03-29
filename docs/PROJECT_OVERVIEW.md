# Project Overview

## Title

Attendance Management System Using Face Recognition

## Problem Statement

Manual attendance takes time, is error-prone, and is easy to manipulate. This project improves the process by using face recognition to mark attendance for students automatically.

## Main Objective

Build a system that can:

- register students and their face data
- start an attendance session for a class
- recognize students from the live camera feed
- mark attendance instantly
- show attendance reports with filters

## System Modules

## 1. Frontend

Located in `frontend/`

- home page
- sign in and sign up pages
- dashboard
- attendance session page
- attendance records page

## 2. Backend

Located in `backend/`

- authentication routes
- student registration and update routes
- attendance session create and end routes
- attendance reporting routes
- health endpoint for deployment checks

## 3. Face Recognition Layer

- MTCNN detects faces from camera input
- DeepFace generates embeddings
- cosine distance is used for matching stored embeddings with the live face

## 4. Database

- MongoDB stores student records
- attendance records are stored in a dedicated attendance collection
- session data stores present and absent information for each class session

## Current Workflow

1. User signs in.
2. User opens the dashboard.
3. User starts an attendance session by entering date, subject, department, year, and division.
4. Camera recognition begins.
5. Recognized students are marked present.
6. Session is ended and finalized.
7. Attendance records can be filtered and exported.

## Key Improvements Made Recently

- unified login flow instead of separate student and teacher split
- better logout behavior
- cleaner homepage and dashboard wording
- attendance records UI refinement
- fixed records lookup issue by using the correct attendance collection
- explicit end-session behavior to stop recognition correctly
- auto deployment to GCP through GitHub Actions

## Why This Project Is Useful

- reduces manual work for teachers
- improves attendance accuracy
- stores records digitally
- supports cloud deployment and live demo capability
- demonstrates AI + web + cloud integration in one project