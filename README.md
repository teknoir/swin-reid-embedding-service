# SWIN ReId Embedding Service

A high-performance Re-identification (ReID) embedding service built with Swin Transformer models

### Deployment
```bash
./deploy.sh
```

## API Usage
In a separate terminal, port forward the service port:

```bash
kubectl port-forward svc/swin-reid-embedding-service 8000:80 -n victra-poc
```


Generate embeddings from person images:

```bash
curl -i -X POST \                                                                                                                                                                                                                                                                     ✔  swin-reid-docker   at 20:51:50  
  -F "file=@gnc0211-front-door-1-916f16c1-2619-2025-12-10T02:12:29.184Z.jpg" \
  http://localhost:8000/embed


# OR using GCS URI


curl -i -X POST \                                                                                                                                                                                                                                                                     ✔  swin-reid-docker   at 20:51:50  
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"gs_uri":"gs://victra-poc.teknoir.cloud/media/person-cutouts/2025-12-10/victra-poc-03/nc0211-front-door-1-916f16c1-2619-2025-12-10T02:12:29.184Z.jpg"}' \
  http://localhost:8000/embed_gcs
```

Use API from other applications use the host and port where the service is deployed.
```
# Example
http://swin-reid-embedding-service/embed_gcs
```