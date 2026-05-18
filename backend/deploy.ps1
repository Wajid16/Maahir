$ErrorActionPreference = "Stop"

$PROJECT_ID = "aiseekho2026-495022"
$REGION = "us-central1"
$SERVICE_NAME = "maahir-orchestrator"

Write-Host "Deploying Maahir to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host "----------------------------------------------------"

# Deploy using Cloud Run buildpacks/source deployment
& gcloud run deploy $SERVICE_NAME `
    --source . `
    --project $PROJECT_ID `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDeployment Successful! 🚀" -ForegroundColor Green
    Write-Host "Make sure to update the Flutter app's api_service.dart with the new Cloud Run URL." -ForegroundColor Yellow
} else {
    Write-Host "`nDeployment Failed. ❌" -ForegroundColor Red
}
