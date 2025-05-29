#!/bin/bash

# Set variables
REGION="us-east-1"
ACCOUNT_ID="248189947068"
REPOSITORY_NAME="govsananga"
REPOSITORY_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORY_NAME}"
IMAGE_TAG="latest"

echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REPOSITORY_URI

echo "Pulling the Docker image from ECR..."
docker pull ${REPOSITORY_URI}:${IMAGE_TAG}

echo "Running the Docker image locally..."
docker run -p 8501:8501 ${REPOSITORY_URI}:${IMAGE_TAG}

