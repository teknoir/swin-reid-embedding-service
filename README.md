# ReID Embedding API

A high-performance Re-identification (ReID) embedding service built with Swin Transformer models, optimized for GPU inference using ONNX Runtime.

## Overview

This service provides REST API endpoints for generating person re-identification embeddings using state-of-the-art Swin Transformer models. The API accepts person images and returns normalized feature vectors suitable for vector databases and similarity search applications.

## Features

- **GPU Acceleration**: Optimized for CUDA execution with ONNX Runtime
- **CPU Fallback**: Full CPU support for deployment flexibility
- **Auto-resizing**: Automatic image preprocessing - no manual resizing required
- **L2 Normalized**: Embeddings are pre-normalized for efficient similarity search
- **Docker Ready**: Containerized deployment with GPU/CPU support

## Quick Start

### API Usage

Generate embeddings from person images:

```bash
# Basic usage
curl -F "file=@person_001.png" http://localhost:8080/embed | jq .dim,.embedding[0:8]

# Base64 encoded response
curl -F "file=@person_001.png" "http://localhost:8080/embed?as_base64=true" | jq .
```

### Response Format

The API returns JSON responses with:
- `dim`: Embedding dimensionality (1024 for Swin Base model)
- `embedding`: Normalized feature vector
- Optional base64 encoding for efficient transport

## Deployment

### Building the Image

```bash
docker build --no-cache -t reid-embed-api:cuda118-ort118 .
```

### GPU Deployment

```bash
docker run --rm --gpus all -p 8080:8080 \
  -v /data/reid-embed-api/export:/models:ro \
  -e MODEL_PATH=/models/reid_swinb_1024.onnx \
  -e ORT_PROVIDERS="CUDAExecutionProvider" \
  reid-embed-api:cuda118-ort118
```

### CPU Deployment

```bash
docker run --rm -p 8080:8080 \
  -v /data/reid-embed-api/export:/models:ro \
  -e MODEL_PATH=/models/reid_swinb_1024.onnx \
  -e ORT_PROVIDERS="CPUExecutionProvider" \
  reid-embed-api:cuda118-ort118
```

### Monitoring

View container logs:
```bash
docker logs -f reid-embed-api
```

## Model Export

### Prerequisites

- NVIDIA TAO Toolkit installed
- Access to NGC model registry

### Export Process

```bash
# Download pre-trained model
ngc registry model download-version "nvidia/tao/reidentificationnet_transformer:swin_base_1024" --dest data/swin_base_1024

# Create export directory
mkdir -p /data/tao/results/reid_transformer/export

# Set environment variables
export SPEC_C=/workspace/tao-experiments/specs/reid_transformer.yaml
export RESULTS_C=/workspace/tao-experiments/results/reid_transformer
export CKPT_C=/workspace/tao-experiments/data/reidentificationnet_transformer_vswin_base_1024/swin_base_market1501_aicity156_featuredim1024.tlt
export ONNX_C=/workspace/tao-experiments/results/reid_transformer/export/reid_swinb_1024.onnx

# Export to ONNX format
tao model re_identification export \
  -e "$SPEC_C" \
  results_dir="$RESULTS_C" \
  model.backbone=swin_base_patch4_window7_224 \
  model.input_height=256 model.input_width=128 \
  model.neck=bnneck model.reduce_feat_dim=False model.feat_dim=1024 \
  dataset.num_classes=857 \
  export.checkpoint="$CKPT_C" \
  export.onnx_file="$ONNX_C"
```

## Technical Details

- **Model**: Swin Base Transformer (Swin-B)
- **Input Resolution**: 256x128 pixels
- **Feature Dimension**: 1024
- **Normalization**: L2-normalized embeddings
- **Similarity Metrics**: Use dot-product or cosine similarity
- **Framework**: ONNX Runtime with CUDA/CPU providers


## PNotes

- Embeddings are L2-normalized for efficient similarity search
- No pre-processing required - images are automatically resized
