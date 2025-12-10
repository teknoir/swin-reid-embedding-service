#!/usr/bin/env bash
set -e
#set -x

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -t|--target)
    TARGET="$2"
    shift
    shift
    ;;
    *)
    POSITIONAL+=("$1")
    shift
    ;;
esac
done

if [ -z "$TARGET" ]; then
    # Default target if none provided
    TARGET="victra-poc"
fi

# Build the Docker images first
export BRANCH_NAME=${BRANCH_NAME:-"local-build"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}

./build.sh

export NAMESPACE=${TARGET}
if [[ $NAMESPACE == "demonstrations" ]] ; then
  CONTEXT="gke_teknoir-poc_us-central1-c_teknoir-dev-cluster"
  DOMAIN="teknoir.dev"
else
  CONTEXT="gke_teknoir_us-central1-c_teknoir-cluster"
  DOMAIN="teknoir.cloud"
fi

cat <<EOF | kubectl --context "$CONTEXT" --namespace "$NAMESPACE" apply -f -
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: swin-reid-embedding-service
  namespace: ${NAMESPACE}
spec:
  repo: https://teknoir.github.io/swin-reid-embedding-service
  chart: swin-reid-embedding-service
  version: 0.0.1
  targetNamespace: ${NAMESPACE}
  valuesContent: |-
    basePath: /${NAMESPACE}/swin-reid-embedding-service
    image:
      tag: ${BRANCH_NAME}-${SHORT_SHA}

EOF