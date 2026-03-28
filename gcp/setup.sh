#!/bin/bash
# GCP Setup Script for Face Recognition Attendance System
# This script sets up all necessary GCP resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GCP Setup for Attendance System${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI not found. Please install Google Cloud SDK${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}ERROR: Project ID cannot be empty${NC}"
    exit 1
fi

echo -e "${YELLOW}Setting up project: $PROJECT_ID${NC}\n"

# Set project
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    logging.googleapis.com \
    cloudresourcemanager.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}\n"

echo -e "${YELLOW}Step 2: Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create attendance \
    --location=us-central1 \
    --repository-format=docker \
    --quiet 2>/dev/null || echo "Repository may already exist"

echo -e "${GREEN}✓ Artifact Registry ready${NC}\n"

echo -e "${YELLOW}Step 3: Creating Firestore database...${NC}"
gcloud firestore databases create \
    --location=us-central1 \
    --type=datastore-mode \
    --quiet 2>/dev/null || echo "Firestore database may already exist"

echo -e "${GREEN}✓ Firestore configured${NC}\n"

echo -e "${YELLOW}Step 4: Creating service account...${NC}"
gcloud iam service-accounts create attendance-sa \
    --display-name="Attendance System Service Account" \
    --quiet 2>/dev/null || echo "Service account may already exist"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:attendance-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:attendance-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer" \
    --quiet

echo -e "${GREEN}✓ Service account created with permissions${NC}\n"

echo -e "${YELLOW}Step 5: Configuring Docker authentication...${NC}"
gcloud auth configure-docker us-central1-docker.pkg.dev

echo -e "${GREEN}✓ Docker authenticated${NC}\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ GCP Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo "Next steps:"
echo "1. Create .env file in backend/:"
echo "   FIRESTORE_PROJECT_ID=$PROJECT_ID"
echo ""
echo "2. Build and push Docker images:"
echo "   ./gcp/deploy.sh"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: us-central1"
echo "Artifact Registry: us-central1-docker.pkg.dev/$PROJECT_ID/attendance"
