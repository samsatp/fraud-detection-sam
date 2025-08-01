#!/bin/bash

image_name="fraud-api-sam"
container_name="fraud-api-sam-container"

# Clean up any existing containers or images
docker rm -f $container_name || true
docker rmi $image_name || true

# Build and run the Docker container
docker build -t $image_name .
docker run -d --name $container_name -p 80:80 \
    -v "$(pwd)/output:/app/output" \  # Mount output directory to persist predictions
    -v "$(pwd)/models:/app/models" \  # Mount models directory for easy model updates
    $image_name 