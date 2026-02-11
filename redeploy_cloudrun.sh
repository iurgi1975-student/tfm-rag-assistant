#!/bin/bash

# Quick redeploy script for Cloud Run after fixing port issues

set -e

echo "🔧 Quick Cloud Run Redeploy - Port Fix"
echo "======================================"

# Get project ID from gcloud config or prompt
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project configured. Please set your project ID:"
    read -r PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"rag-assistant"}
IMAGE_NAME=${IMAGE_NAME:-"rag-assistant"}

echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Build new image
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$IMAGE_NAME/$SERVICE_NAME:latest"

echo "🔨 Rebuilding image with port 8080..."
gcloud builds submit --tag="$IMAGE_TAG" --project="$PROJECT_ID" --timeout=20m

if [ $? -eq 0 ]; then
    echo "✅ Image rebuilt successfully!"
    echo ""
    echo "Cloud Run will automatically use the new image on next deployment."
    echo "The existing service should pick it up, or run: ./deploy_to_cloudrun.sh"
else
    echo "❌ Build failed. Check the logs above."
    exit 1
fi

echo ""
echo "📋 To check service status:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "📋 To view logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
