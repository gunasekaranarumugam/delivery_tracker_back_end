#!/bin/bash
set -e

echo "Pulling latest Docker image..."
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 294253399473.dkr.ecr.ap-south-1.amazonaws.com

docker pull 294253399473.dkr.ecr.ap-south-1.amazonaws.com/delivery-tracker-back-end-main:latest

echo "Stopping old container..."
docker stop delivery-tracker-backend-master || true
docker rm delivery-tracker-backend-master || true

echo "Starting new container..."
docker run -d --name delivery-tracker-back-end-main -p 8000:8000 294253399473.dkr.ecr.ap-south-1.amazonaws.com/delivery-tracker-back-end-main:latest

echo "Deployment completed successfully."
