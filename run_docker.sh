#!/bin/bash

image_name="fraud-api-sam"
container_name="fraud-api-sam-container"

# Clean up any existing containers or images
docker stop $container_name || true
docker rm -f $container_name || true
docker rmi $image_name || true

# Build and run the Docker container
docker build -t $image_name .
docker run -d --name $container_name -p 8080:8080 -v "$(pwd)/output:/app/output" -v "$(pwd)/models:/app/models" $image_name 