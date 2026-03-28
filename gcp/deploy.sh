#!/bin/bash
# Deploy script for Face Recognition Attendance System to GCP Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying to GCP Cloud Run${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Get project ID from gcloud config
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}ERROR: No GCP project configured${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

REGION="us-central1"
REGISTRY="us-central1-docker.pkg.dev"
BACKEND_IMAGE="$REGISTRY/$PROJECT_ID/attendance/backend:latest"
FRONTEND_IMAGE="$REGISTRY/$PROJECT_ID/attendance/frontend:latest"

echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"
echo -e "${YELLOW}Region: $REGION${NC}\n"

# Step 1: Build and push backend
echo -e "${YELLOW}Step 1: Building and pushing backend image...${NC}"
docker build -t $BACKEND_IMAGE ./backend
docker push $BACKEND_IMAGE
echo -e "${GREEN}✓ Backend image pushed${NC}\n"

# Step 2: Build and push frontend
echo -e "${YELLOW}Step 2: Building and pushing frontend image...${NC}"
docker build -t $FRONTEND_IMAGE ./frontend
docker push $FRONTEND_IMAGE
echo -e "${GREEN}✓ Frontend image pushed${NC}\n"

# Step 3: Deploy backend to Cloud Run
echo -e "${YELLOW}Step 3: Deploying backend to Cloud Run...${NC}"
gcloud run deploy attendance-backend \
    --image $BACKEND_IMAGE \
    --platform managed \
    --region $REGION \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --allow-unauthenticated \
    --set-env-vars FIRESTORE_PROJECT_ID=$PROJECT_ID,FLASK_ENV=production \
    --quiet

BACKEND_URL=$(gcloud run services describe attendance-backend --region=$REGION --format='value(status.url)')
echo -e "${GREEN}✓ Backend deployed: $BACKEND_URL${NC}\n"

# Step 4: Deploy frontend to Cloud Run
echo -e "${YELLOW}Step 4: Deploying frontend to Cloud Run...${NC}"
gcloud run deploy attendance-frontend \
    --image $FRONTEND_IMAGE \
    --platform managed \
    --region $REGION \
    --memory 1Gi \
    --allow-unauthenticated \
    --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL \
    --quiet

FRONTEND_URL=$(gcloud run services describe attendance-frontend --region=$REGION --format='value(status.url)')
echo -e "${GREEN}✓ Frontend deployed: $FRONTEND_URL${NC}\n"

# Step 5: Test endpoints
echo -e "${YELLOW}Step 5: Testing endpoints...${NC}"
echo "Backend health check:"
curl -s $BACKEND_URL/health | jq . || echo "Could not reach backend"
echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""
echo "Next steps:"
echo "1. Visit: $FRONTEND_URL"
echo "2. Test student registration"
echo "3. Test attendance marking"
echo ""
echo "To view logs:"
echo "  gcloud run logs read attendance-backend --limit 50"
echo "  gcloud run logs read attendance-frontend --limit 50"
