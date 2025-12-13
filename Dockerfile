FROM python:3.11-slim AS base

WORKDIR /app

# Build target: cpu or gpu (default cpu)
ARG BUILD_TARGET=cpu
ENV BUILD_TARGET=${BUILD_TARGET}

# Install Python deps based on build target
COPY requirements-cpu.txt /app/requirements-cpu.txt
COPY requirements-gpu.txt /app/requirements-gpu.txt
RUN if [ "$BUILD_TARGET" = "gpu" ]; then \
        echo "Installing GPU requirements" && \
        pip install --no-cache-dir -r /app/requirements-gpu.txt ; \
    else \
        echo "Installing CPU requirements" && \
        pip install --no-cache-dir -r /app/requirements-cpu.txt ; \
    fi

# App source
COPY app.py ./

# Model
COPY --from=us-docker.pkg.dev/teknoir/gcr.io/reid-swinb-1024-tracker-deepstream:latest-retrained-20251209-132725 /tracker/reid-swinb-1024-tracker/reid_swinb_1024.onnx /app/
ENV MODEL_PATH=reid_swinb_1024.onnx \
    INPUT_H=224 INPUT_W=224

EXPOSE 8000
CMD ["python", "app.py"]
