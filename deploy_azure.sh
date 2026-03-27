#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  deploy_azure.sh  –  Deploy Face Recognition API to Azure
#  Uses: Azure Container Apps (free tier) + Azure Container Registry
#
#  Prerequisites:
#    brew install azure-cli   OR   apt-get install azure-cli
#    az login
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

# ── EDIT THESE ─────────────────────────────────────────────────
APP_NAME="face-recognition-mlops"
RESOURCE_GROUP="face-rg"
LOCATION="eastus"
ACR_NAME="facerecognitionacr$(date +%s | tail -c 6)"    # must be globally unique
CONTAINER_ENV="face-env"
# ───────────────────────────────────────────────────────────────

IMAGE_TAG="latest"
IMAGE_FULL="${ACR_NAME}.azurecr.io/${APP_NAME}:${IMAGE_TAG}"

echo "=== 1. Login & create resource group ==="
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

echo "=== 2. Create Azure Container Registry (free tier) ==="
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true

ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

echo "=== 3. Build & push Docker image ==="
az acr build \
  --registry "$ACR_NAME" \
  --image "${APP_NAME}:${IMAGE_TAG}" \
  .

echo "=== 4. Create Container Apps environment ==="
az containerapp env create \
  --name "$CONTAINER_ENV" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION"

echo "=== 5. Deploy Container App ==="
az containerapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$CONTAINER_ENV" \
  --image "$IMAGE_FULL" \
  --registry-server "${ACR_NAME}.azurecr.io" \
  --registry-username "$ACR_NAME" \
  --registry-password "$ACR_PASSWORD" \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 0 \
  --max-replicas 3 \
  --env-vars \
      "DATABASE_URL=sqlite:////app/data/face_recognition.db" \
      "DATA_DIR=/app/data/students" \
      "MODELS_DIR=/app/saved_models" \
      "CONFIDENCE_THRESHOLD=0.75" \
      "TRAIN_EPOCHS=25"

APP_URL=$(az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "  ✅  Deployed!  API URL: https://${APP_URL}"
echo "  📚  Swagger:   https://${APP_URL}/docs"
echo "  🖥️   UI:        https://${APP_URL}/ui"
echo "╚══════════════════════════════════════════════════════╝"
