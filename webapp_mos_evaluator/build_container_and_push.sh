#!/bin/bash
set -euo pipefail

echo "BUILDING CONTAINER AND PUSHING TO REGISTRIES  "

GIT_COMMIT="$(git rev-parse --short HEAD)"
BUILD_DATE="$(date +"%Y-%m-%dT%H:%M:%SZ")-$GIT_COMMIT"

###### building vits_mos amd64
echo "Building container"
docker buildx build --platform linux/amd64 -f Dockerfile -t nasdnn.local:5050/vits:latest --build-arg BUILD_DATE="$BUILD_DATE" --load .

echo "tagging  container latest "
docker tag nasdnn.local:5050/vits:latest ghcr.io/andrenatal/vits:latest

###### pushing vits amd64

echo "pushing to nasdnn latest "
docker push nasdnn.local:5050/vits:latest

echo "pushing to ghcr.io latest "
docker push ghcr.io/andrenatal/vits:latest

