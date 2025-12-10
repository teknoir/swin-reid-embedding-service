#!/usr/bin/env bash
set -eo pipefail
#set -x

export BRANCH_NAME=${BRANCH_NAME:-"local"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export IMAGE=${IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/swin-reid-embedding-service"}

docker buildx build \
  --platform=linux/amd64 \
  --push \
  --tag "${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  .

echo "Image built and pushed: ${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"
