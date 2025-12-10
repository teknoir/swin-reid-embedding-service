FROM python:3.11-slim

WORKDIR /app

# Install Python deps from requirements.txt
COPY requirements-cpu.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY app.py ./

COPY --from=us-docker.pkg.dev/teknoir/gcr.io/reid-swinb-1024-tracker-deepstream:latest-retrained-20251209-132725 /tracker/reid-swinb-1024-tracker/reid_swinb_1024.onnx /app/
ENV MODEL_PATH=reid_swinb_1024.onnx \
    INPUT_H=224 INPUT_W=224

EXPOSE 8000
CMD ["python", "app.py"]
