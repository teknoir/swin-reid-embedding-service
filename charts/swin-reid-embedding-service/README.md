# SWIN ReId Embedding Service Helm Chart

This chart deploys SWIN ReId Embedding Service application to a Kubernetes cluster.

> The implementation of the Helm chart is right now the bare minimum to get it to work.
> The purpose of the chart is not to be infinitely configurable, but to provide a limited set of configuration options that make sense for the Teknoir platform.

# Helm usage

## Usage in Teknoir platform
Use the HelmChart to deploy the SWIN ReId Embedding Service application to a Namespace.

```yaml
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: swin-reid-embedding-service
  namespace: demonstrations # or any other namespace
spec:
  repo: https://teknoir.github.io/swin-reid-embedding-service
  chart: swin-reid-embedding-service
  targetNamespace: demonstrations # or any other namespace
  valuesContent: |-
    # Example for minimal configuration
    
```

## Adding the repository

```bash
helm repo add teknoir-swin-reid-embedding-service https://teknoir.github.io/swin-reid-embedding-service/
```

## Installing the chart

```bash
helm install teknoir-swin-reid-embedding-service teknoir-swin-reid-embedding-service/swin-reid-embedding-service -f values.yaml
```
