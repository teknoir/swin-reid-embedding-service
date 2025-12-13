# CPU image stage
FROM python:3.11-slim AS cpu

WORKDIR /app

# Install CPU Python deps
COPY requirements-cpu.txt /app/requirements-cpu.txt
RUN pip install --no-cache-dir -r /app/requirements-cpu.txt

# App source
COPY app.py ./

# Model
COPY --from=us-docker.pkg.dev/teknoir/gcr.io/reid-swinb-1024-tracker-deepstream:latest-retrained-20251209-132725 /tracker/reid-swinb-1024-tracker/reid_swinb_1024.onnx /app/
ENV MODEL_PATH=reid_swinb_1024.onnx \
    INPUT_H=224 INPUT_W=224

EXPOSE 8000
CMD ["python", "app.py"]

# GPU image stage (uses NVIDIA CUDA runtime base)
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04 AS gpu

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Install GPU Python deps
COPY requirements-gpu.txt /app/requirements-gpu.txt
RUN pip3 install --no-cache-dir -r /app/requirements-gpu.txt

# App source
COPY app.py ./

# Model
COPY --from=us-docker.pkg.dev/teknoir/gcr.io/reid-swinb-1024-tracker-deepstream:latest-retrained-20251209-132725 /tracker/reid-swinb-1024-tracker/reid_swinb_1024.onnx /app/
ENV MODEL_PATH=reid_swinb_1024.onnx \
    INPUT_H=224 INPUT_W=224

# Ensure CUDA libraries are on the runtime path
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

EXPOSE 8000
CMD ["python3", "app.py"]
