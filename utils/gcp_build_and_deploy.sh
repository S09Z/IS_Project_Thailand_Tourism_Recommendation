#!/bin/bash
# build_and_deploy.sh

PROJECT_ID="murpheys09-sandboxs"
REGION="asia-southeast1"
IMAGE="gcr.io/$PROJECT_ID/my-streamlit-app:latest" 
SERVICE_NAME="my-streamlit-app"

# echo "🚀 Pushing image to GCR..."
# gcloud builds submit --config=cloudbuild.yaml

echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --allow-unauthenticated \
  --memory=4Gi \
  --cpu=2

echo "🌐 Publish URL"
gcloud run services describe my-streamlit-app \
  --platform managed --region asia-southeast1 \
  --format 'value(status.url)'