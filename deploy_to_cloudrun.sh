#!/bin/bash

# Deploy RAG Assistant to Google Cloud Run
# This script builds and deploys the Docker image to Google Cloud Run

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Google Cloud Run Deployment Script${NC}"
echo "======================================"

# Configuration variables
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"rag-assistant"}
IMAGE_NAME=${IMAGE_NAME:-"rag-assistant"}
MEMORY=${MEMORY:-"2Gi"}
CPU=${CPU:-"2"}
MAX_INSTANCES=${MAX_INSTANCES:-"10"}
MIN_INSTANCES=${MIN_INSTANCES:-"0"}
TIMEOUT=${TIMEOUT:-"300"}
PORT=8080

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for Project ID if not set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}📝 Please enter your Google Cloud Project ID:${NC}"
    read -r PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Error: Project ID is required${NC}"
        exit 1
    fi
fi

echo -e "\n${BLUE}Configuration:${NC}"
echo "  Project ID:    $PROJECT_ID"
echo "  Region:        $REGION"
echo "  Service Name:  $SERVICE_NAME"
echo "  Memory:        $MEMORY"
echo "  CPU:           $CPU"
echo "  Max Instances: $MAX_INSTANCES"
echo "  Min Instances: $MIN_INSTANCES"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Set the project
echo -e "\n${BLUE}🔧 Setting project to $PROJECT_ID...${NC}"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo -e "\n${BLUE}📦 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"

# Create Artifact Registry repository (if it doesn't exist)
echo -e "\n${BLUE}📦 Checking Artifact Registry repository...${NC}"
if ! gcloud artifacts repositories describe "$IMAGE_NAME" \
    --location="$REGION" \
    --project="$PROJECT_ID" &> /dev/null; then
    
    echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"
    gcloud artifacts repositories create "$IMAGE_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="RAG Assistant Docker images" \
        --project="$PROJECT_ID"
else
    echo -e "${GREEN}✓ Repository already exists${NC}"
fi

# Build the image using Cloud Build
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$IMAGE_NAME/$SERVICE_NAME:latest"
echo -e "\n${BLUE}🔨 Building Docker image with Cloud Build...${NC}"
echo "Image tag: $IMAGE_TAG"

gcloud builds submit \
    --tag="$IMAGE_TAG" \
    --project="$PROJECT_ID" \
    --timeout=20m

echo -e "${GREEN}✓ Image built successfully${NC}"

# Check if .env file exists and read API key
GOOGLE_API_KEY=""
if [ -f ".env" ]; then
    # Extract GOOGLE_API_KEY from .env file
    GOOGLE_API_KEY=$(grep -E "^GOOGLE_API_KEY=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
fi

# Prompt for API key if not found
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "\n${YELLOW}⚠️  GOOGLE_API_KEY not found in .env file${NC}"
    echo "Please enter your Google API Key:"
    read -r GOOGLE_API_KEY
fi

# Prompt for authentication users
echo -e "\n${YELLOW}🔐 Configure authentication users${NC}"
echo "Format: user1:pass1,user2:pass2"
echo "Default (press Enter): admin:admin123"
read -r GRADIO_AUTH_USERS
if [ -z "$GRADIO_AUTH_USERS" ]; then
    GRADIO_AUTH_USERS="admin:admin123"
fi

# Deploy to Cloud Run
echo -e "\n${BLUE}🚀 Deploying to Cloud Run...${NC}"

gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_TAG" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --allow-unauthenticated \
    --memory="$MEMORY" \
    --cpu="$CPU" \
    --timeout="$TIMEOUT" \
    --max-instances="$MAX_INSTANCES" \
    --min-instances="$MIN_INSTANCES" \
    --port="$PORT" \
    --set-env-vars="GOOGLE_API_KEY=$GOOGLE_API_KEY,GRADIO_AUTH_USERS=$GRADIO_AUTH_USERS"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format='value(status.url)')

echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "======================================"
echo -e "${GREEN}🎉 Your RAG Assistant is live!${NC}"
echo "======================================"
echo -e "URL: ${BLUE}$SERVICE_URL${NC}"
echo ""
echo "Login credentials:"
echo "  Users: $GRADIO_AUTH_USERS"
echo ""
echo "Useful commands:"
echo "  View logs:    gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo "  View details: gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo "  Delete:       gcloud run services delete $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
