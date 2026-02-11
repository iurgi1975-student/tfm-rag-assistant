# Quick Cloud Run Redeploy Script (PowerShell)
# Rebuilds the Docker image with correct port configuration

Write-Host "🔧 Quick Cloud Run Redeploy - Port Fix" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Get project ID from gcloud config
$PROJECT_ID = gcloud config get-value project 2>$null

if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "❌ No project configured." -ForegroundColor Red
    $PROJECT_ID = Read-Host "Please enter your Google Cloud Project ID"
    gcloud config set project $PROJECT_ID
}

$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$SERVICE_NAME = if ($env:SERVICE_NAME) { $env:SERVICE_NAME } else { "rag-assistant" }
$IMAGE_NAME = if ($env:IMAGE_NAME) { $env:IMAGE_NAME } else { "rag-assistant" }

Write-Host ""
Write-Host "Project: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Service: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host ""

# Build new image
$IMAGE_TAG = "$REGION-docker.pkg.dev/$PROJECT_ID/$IMAGE_NAME/$SERVICE_NAME:latest"

Write-Host "🔨 Rebuilding image with port 8080..." -ForegroundColor Cyan
gcloud builds submit --tag="$IMAGE_TAG" --project="$PROJECT_ID" --timeout=20m

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image rebuilt successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Cloud Run will automatically use the new image." -ForegroundColor Green
    Write-Host "Run the full deploy script if you need to update environment variables." -ForegroundColor Yellow
} else {
    Write-Host "❌ Build failed. Check the logs above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 To check service status:" -ForegroundColor Cyan
Write-Host "   gcloud run services describe $SERVICE_NAME --region=$REGION" -ForegroundColor White
Write-Host ""
Write-Host "📋 To view logs:" -ForegroundColor Cyan
Write-Host "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50" -ForegroundColor White
Write-Host ""
Write-Host "📋 To get service URL:" -ForegroundColor Cyan
Write-Host "   gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'" -ForegroundColor White
