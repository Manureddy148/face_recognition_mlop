#!/bin/bash
# Pre-deployment verification script
# Checks all prerequisites before starting deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pre-Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}\n"

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check a command
check_command() {
    local cmd=$1
    local name=$2
    
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name installed"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $name NOT installed"
        ((CHECKS_FAILED++))
    fi
}

# Function to check file
check_file() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name exists"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $name not found"
        ((CHECKS_FAILED++))
    fi
}

# Function to check directory
check_directory() {
    local dir=$1
    local name=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir exists"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $dir NOT found"
        ((CHECKS_FAILED++))
    fi
}

echo -e "${YELLOW}1. Checking System Requirements${NC}"
check_command gcloud "Google Cloud SDK"
check_command docker "Docker"
check_command node "Node.js"
check_command python "Python"
echo ""

echo -e "${YELLOW}2. Checking Project Files${NC}"
check_directory "backend" "Backend directory"
check_directory "frontend" "Frontend directory"
check_file "docker-compose.yml" "docker-compose.yml"
check_file "backend/Dockerfile" "backend/Dockerfile"
check_file "frontend/Dockerfile" "frontend/Dockerfile"
echo ""

echo -e "${YELLOW}3. Checking GCP Files${NC}"
check_file "gcp/setup.sh" "GCP setup script"
check_file "gcp/deploy.sh" "GCP deploy script"
check_file "gcp/README.md" "GCP documentation"
check_file "gcp/migrate_to_firestore.py" "Migration script"
echo ""

echo -e "${YELLOW}4. Checking Configuration Files${NC}"
check_file "backend/firestore_service.py" "Firestore service module"
check_file "backend/requirements.txt" "Backend requirements"
check_file "backend/.env.example" "Backend env template"
check_file "frontend/.env.example" "Frontend env template"
echo ""

echo -e "${YELLOW}5. Checking Environment Variables${NC}"
if [ -z "$FIRESTORE_PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠${NC} FIRESTORE_PROJECT_ID not set (will be set during setup)"
    ((CHECKS_FAILED++))
else
    echo -e "${GREEN}✓${NC} FIRESTORE_PROJECT_ID set to: $FIRESTORE_PROJECT_ID"
    ((CHECKS_PASSED++))
fi

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠${NC} GCP project not configured"
    echo "  Run: gcloud config set project YOUR_PROJECT_ID"
else
    echo -e "${GREEN}✓${NC} GCP project: $PROJECT_ID"
    ((CHECKS_PASSED++))
fi
echo ""

echo -e "${YELLOW}6. Checking Docker${NC}"
if docker --version &> /dev/null; then
    DOCKER_RUNNING=$(docker ps &> /dev/null && echo "yes" || echo "no")
    if [ "$DOCKER_RUNNING" = "yes" ]; then
        echo -e "${GREEN}✓${NC} Docker is running"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} Docker is not running"
        echo "  Start Docker and try again"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Docker not found"
    ((CHECKS_FAILED++))
fi
echo ""

echo -e "${YELLOW}7. Checking .env Files${NC}"
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC} backend/.env exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} backend/.env not found"
    echo "  Create with: cp backend/.env.example backend/.env"
    ((CHECKS_FAILED++))
fi

if [ -f "frontend/.env.local" ]; then
    echo -e "${GREEN}✓${NC} frontend/.env.local exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} frontend/.env.local not found"
    echo "  Create with: cp frontend/.env.example frontend/.env.local"
    ((CHECKS_FAILED++))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed:${NC} $CHECKS_PASSED"
echo -e "${RED}Failed:${NC} $CHECKS_FAILED"
echo -e "${BLUE}========================================${NC}\n"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready for deployment.${NC}\n"
    echo "Next steps:"
    echo "1. bash gcp/setup.sh"
    echo "2. docker-compose up"
    echo "3. bash gcp/deploy.sh"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix above issues.${NC}\n"
    echo "Fix the issues above before proceeding with deployment."
    exit 1
fi
