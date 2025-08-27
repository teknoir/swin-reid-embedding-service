FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ca-certificates curl libgomp1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip3 install --no-cache-dir \
    fastapi==0.116.1 "uvicorn[standard]==0.30.6" \
    pillow==10.4.0 numpy==1.26.4 \
    onnxruntime-gpu==1.18.1 \
    python-multipart==0.0.9 python-json-logger==2.0.7

COPY app.py ./

ENV MODEL_PATH=/models/reid_swinb_1024.onnx \
    ORT_THREADS=1 \
    ORT_PROVIDERS="CUDAExecutionProvider,CPUExecutionProvider" \
    INPUT_H=256 INPUT_W=128 \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

EXPOSE 8080
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080","--access-log","--log-level","info"]
