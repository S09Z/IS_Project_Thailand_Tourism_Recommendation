#!/bin/bash
# build_and_deploy.sh

PROJECT_ID="murpheys09-sandboxs"
SERVICE_NAME="my-streamlit-service"
REGION="asia-southeast1"
IMAGE="gcr.io/$PROJECT_ID/my-streamlit-app"

echo "🔨 Building Docker image..."
docker build -f app/frontend/Dockerfile -t $IMAGE .

echo "🚀 Pushing image to GCR..."
docker push $IMAGE

echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --timeout 300s 