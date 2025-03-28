#!/bin/bash
# build_and_deploy.sh

PROJECT_ID="murpheys09-sandboxs"
SERVICE_NAME="my-streamlit-service"
REGION="asia-southeast1"
IMAGE="gcr.io/$PROJECT_ID/my-streamlit-app" 

echo "🚀 Pushing image to GCR..."
gcloud builds submit --config=cloudbuild.yaml

echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300s

echo "🌐 Publish URL"
gcloud run services describe my-streamlit-service \
  --platform managed --region $REGION \
  --format 'value(status.url)'