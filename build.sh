#!/usr/bin/env bash
set -eo pipefail
#set -x

export BRANCH_NAME=${BRANCH_NAME:-"local"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export IMAGE=${IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/swin-reid-embedding-service"}

# Build and push CPU image
docker buildx build \
  --platform=linux/amd64 \
  --push \
  --build-arg BUILD_TARGET=cpu \
  --tag "${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}-cpu" \
  .

echo "Image built and pushed: ${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}-cpu"

# Build and push GPU image
docker buildx build \
  --platform=linux/amd64 \
  --push \
  --build-arg BUILD_TARGET=gpu \
  --tag "${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}-gpu" \
  .

echo "Image built and pushed: ${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}-gpu"
