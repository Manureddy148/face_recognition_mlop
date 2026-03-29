# Presentation Notes

## 1 Minute Introduction

"Good morning sir. Our project is an Attendance Management System Using Face Recognition. The goal is to automate attendance by identifying students from a live camera feed instead of taking attendance manually. The project combines AI, web development, backend APIs, database storage, and cloud deployment."

## Problem

- manual attendance is slow
- proxy attendance is possible
- paper or spreadsheet handling is inefficient

## Solution

- register student details and face data
- create an attendance session for a class and subject
- recognize students through the camera
- mark attendance automatically
- store records digitally and view them later with filters

## Tech Explanation

- frontend is built with Next.js
- backend is built with Flask
- face recognition uses MTCNN and DeepFace
- data is stored in MongoDB
- deployment is done on GCP Cloud Run
- CI/CD is handled by GitHub Actions

## Key Features To Mention

- single login flow
- attendance session by subject and class
- live face recognition
- attendance records page with filters
- export support
- cloud deployment with auto updates

## What We Improved Recently

- fixed logout and navigation flow
- improved attendance records UI
- corrected attendance records backend lookup
- added proper end-session behavior so camera and recognition stop cleanly
- cleaned homepage and dashboard wording
- merged file reorganization changes into main

## Short Demo Flow

1. Open homepage
2. Sign in
3. Open dashboard
4. Start attendance session
5. Enter date, subject, department, year, division
6. Start camera recognition
7. Recognize students and mark attendance
8. End session
9. Open attendance records and filter by date and subject

## Questions Sir May Ask

## Why use face recognition?

It reduces manual effort and improves attendance authenticity.

## Why cloud deployment?

It makes the project accessible online and shows real deployment capability beyond local execution.

## What was the biggest challenge?

Matching the real-time face recognition flow, session handling, attendance storage, and deployment pipeline in one consistent system.

## Final Closing Line

"This project demonstrates how AI can be applied to a practical college use case by combining computer vision, web application development, database design, and cloud deployment into one complete system."